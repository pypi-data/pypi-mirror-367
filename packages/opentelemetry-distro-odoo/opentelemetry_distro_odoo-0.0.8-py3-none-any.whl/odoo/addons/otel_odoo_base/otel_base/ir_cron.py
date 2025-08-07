from odoo import api, models


class IrCron(models.Model):
    _inherit = "ir.cron"

    @api.model
    def _callback(self, cron_name, server_action_id, *args, **kwargs):
        attrs = {"odoo.cron.manual": False}
        span_attrs = {"odoo.cron.action_id": server_action_id, "odoo.cron.manual": False}
        self.otel_instrumentor.odoo_run_cron.add(1, attributes=attrs)
        with self.otel_instrumentor.odoo_call_wrapper(self._name, "callback", attrs=attrs, span_attrs=span_attrs):
            return super()._callback(cron_name, server_action_id, *args, **kwargs)

    def method_direct_trigger(self):
        attrs = {"odoo.cron.manual": True}
        for rec in self:
            span_attrs = {
                "odoo.cron.action_id": rec.ir_actions_server_id.id,
                "odoo.cron.manual": True,
            }
            rec.otel_instrumentor.odoo_run_cron.add(1, attributes=attrs)
            with self.otel_instrumentor.odoo_call_wrapper(self._name, "callback", attrs=attrs, span_attrs=span_attrs):
                super(IrCron, rec).method_direct_trigger()
