from __future__ import annotations

import contextlib
import logging
import os
import re
import threading
import timeit
from typing import Any, Callable

import psycopg2
import requests
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.metrics import (
    CallbackOptions,
    Counter,
    Histogram,
    Meter,
    NoOpMeter,
    ObservableGauge,
    Observation,
    UpDownCounter,
    get_meter,
)
from opentelemetry.semconv.attributes.error_attributes import ERROR_TYPE
from opentelemetry.trace import Span, Status, StatusCode, get_tracer
from opentelemetry.util import types

import odoo.sql_db
import odoo.tools

from opentelemetry_distro_odoo.semconv.attributes import odoo as odoo_attributes
from opentelemetry_distro_odoo.semconv.attributes.odoo import ODOO_UP_TYPE
from opentelemetry_distro_odoo.semconv.environment_variables import ODOO_OTEL_EXCLUDE_RECORDS
from opentelemetry_distro_odoo.semconv.metrics import odoo as odoo_metrics
from opentelemetry_distro_odoo.version import __version__

Default_exclude_record = {
    (None, "get_views"),
    (None, "load_views"),
    (None, "name_get"),
    (None, "name_search"),
    (None, "name_create"),
    (None, "has_group"),
    (None, "get_formview_action"),
    (None, "search_panel_select_range"),
    ("ir.ui.view", None),
}
_logger = logging.getLogger(__name__)


class OdooInstrumentor(BaseInstrumentor):
    odoo_call_sql_queries_count: Counter
    odoo_call_sql_queries_duration: Histogram
    odoo_call_error: Counter
    odoo_call_duration: Histogram
    odoo_report_duration: Histogram
    odoo_send_mail: Counter
    odoo_run_cron: Counter
    worker_count: UpDownCounter
    worker_max: ObservableGauge
    odoo_up: ObservableGauge

    def __init__(
        self,
        exclude_exception: list[str] | None = None,
        exclude_records: list[tuple[str | None, str | None]] | None = None,
    ):
        self.exclude_exception: set[str] = set(exclude_exception or [])
        _exclude_pattern: set[str] = {
            f"{record_name or '.*'}#{function_name or '.*'}"
            for record_name, function_name in Default_exclude_record.union(exclude_records or ())
        }
        _exclude_pattern |= {
            f"{record_name or '.*'}#{function_name or '.*'}"
            for v in (os.getenv(ODOO_OTEL_EXCLUDE_RECORDS) or "").split(",")
            if v
            for record_name, function_name in v.split("#")
        }
        self._exclude_pattern = {re.compile(str_pattern) for str_pattern in _exclude_pattern}
        self._function_map_name = {
            "search_read": "web_search_read",
            "read_group": "web_read_group",
            "read": "web_read",
            "load_views": "get_views",
        }
        self._create_metrics(NoOpMeter(__name__, __version__))

    def _callback_up(self, opt: CallbackOptions) -> list[Observation]:
        port = odoo.tools.config["http_port"] or "8069"
        ok = 0
        try:
            requests.post(
                f"http://localhost:{port}/web/webclient/version_info", json={}, timeout=opt.timeout_millis / 1000
            )
            ok = 1
        except requests.exceptions.RequestException:
            pass

        return [Observation(ok, {ODOO_UP_TYPE: "web"})]

    def _callback_up_wkhtml(self, opt: CallbackOptions) -> list[Observation]:
        from odoo.addons.base.models.ir_actions_report import wkhtmltopdf_state

        return [Observation(int(wkhtmltopdf_state == "ok"), {ODOO_UP_TYPE: "wkhtmltopdf"})]

    def _callback_up_pg(self, opt: CallbackOptions) -> list[Observation]:
        ok = 0
        try:
            if odoo.release.major_version >= "16.0":
                odoo.sql_db.db_connect("postgres").cursor().close()
            else:
                odoo.sql_db.db_connect("postgres").cursor(serialized=False).close()

            ok = 1
        except psycopg2.Error:
            pass
        return [Observation(ok, {ODOO_UP_TYPE: "database"})]

    def _callback_max_worker(self, opt: CallbackOptions) -> list[Observation]:
        workers = odoo.tools.config["workers"] or 0
        return [
            Observation(
                workers,
            )
        ]

    def _instrument(self, **kwargs: Any):
        super()._instrument(**kwargs)
        self._create_metrics(get_meter(__name__, __version__))

    def _create_metrics(self, meter: Meter):
        self.odoo_call_error = odoo_metrics.create_odoo_call_error(meter)
        self.odoo_call_duration = odoo_metrics.create_odoo_call_duration(meter)
        self.odoo_call_sql_queries_count = odoo_metrics.create_odoo_call_sql_queries_count(meter)
        self.odoo_call_sql_queries_duration = odoo_metrics.create_call_sql_queries_duration(meter)
        self.odoo_send_mail = odoo_metrics.create_odoo_send_mail(meter)
        self.odoo_run_cron = odoo_metrics.create_odoo_run_cron(meter)
        self.worker_count = odoo_metrics.create_worker_count(meter)
        self.worker_max = meter.create_observable_gauge(
            odoo_metrics.ODOO_WORKER_MAX, callbacks=[self._callback_max_worker]
        )
        self.odoo_up = meter.create_observable_gauge(
            odoo_metrics.ODOO_UP,
            callbacks=[self._callback_up, self._callback_up_wkhtml, self._callback_up_pg],
            unit="1",
        )

    def instrumentation_dependencies(self):
        return []

    def _uninstrument(self, **kwargs: Any):
        pass

    @property
    def meter(self):
        return get_meter(__name__, __version__)

    @property
    def tracer(self):
        return get_tracer(__name__, __version__)

    def get_attributes_metrics(self, odoo_record_name, method_name):
        current_thread = threading.current_thread()
        return {
            odoo_attributes.ODOO_MODEL_NAME: odoo_record_name,
            odoo_attributes.ODOO_MODEL_FUNCTION_NAME: method_name,
            odoo_attributes.ODOO_CURSOR_MODE: getattr(current_thread, "cursor_mode", "rw"),
        }

    @contextlib.contextmanager
    def odoo_call_wrapper(
        self,
        odoo_record_name: str,
        method_name: str,
        *,
        attrs: types.Attributes = None,
        metrics_attrs: types.Attributes = None,
        span_attrs: types.Attributes = None,
        post_span_callback: Callable[[Span], None] = None,
    ):
        if not self.is_instrumented_by_opentelemetry:
            _logger.debug("Not instrumented by opentelemetry")
            yield
            return

        m_name = self._function_map_name.get(method_name) or method_name
        if any(pat.match(f"{odoo_record_name}#{m_name}") for pat in self._exclude_pattern):
            _logger.debug("Exclude Metrcis on %s#%s", odoo_record_name, m_name)
            yield
            return

        odoo_attr = self.get_attributes_metrics(odoo_record_name, m_name)

        metrics_attr = dict(odoo_attr)
        metrics_attr.update(attrs or {})
        metrics_attr.update(metrics_attrs or {})

        span_attr = dict(odoo_attr)
        span_attr.update(attrs or {})
        span_attr.update(span_attrs or {})

        start = timeit.default_timer()
        with self.tracer.start_as_current_span(f"{odoo_record_name}#{m_name}", attributes=span_attr) as span:
            try:
                yield
            except Exception as ex:
                if type(ex).__qualname__ in self.exclude_exception:
                    raise ex

                metrics_attr[ERROR_TYPE] = type(ex).__qualname__
                self.odoo_call_error.add(1, metrics_attr)
                span.record_exception(ex)
                span.set_attribute(ERROR_TYPE, type(ex).__qualname__)
                span.set_status(Status(StatusCode.ERROR, str(ex)))
                _logger.exception("Exception :", exec_info=ex)
                raise ex
            finally:
                if post_span_callback:
                    post_span_callback(span)
                duration_s = timeit.default_timer() - start
                metrics = self.odoo_call_duration
                metrics.record(duration_s, metrics_attr)
                current_thread = threading.current_thread()
                if hasattr(current_thread, "query_count"):
                    self.odoo_call_sql_queries_count.add(current_thread.query_count, metrics_attr)
                if hasattr(current_thread, "query_time"):
                    self.odoo_call_sql_queries_duration.record(current_thread.query_time, metrics_attr)
