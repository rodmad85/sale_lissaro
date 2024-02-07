
from odoo import models, api
class ProjectMrp (models.Model):
    _inherit = "project.task"

    @api.onchange('stage_id')
    def _donemrp(self):
        for rec in self:
            if rec.stage_id.name == 'Concluido':
                lin_venda = rec.sale_line_id.id
                pedido = self.env['sale.order.line'].browse(lin_venda).order
                produto = pedido.product_id
                ordem = self.env['mrp.production'].search([('origin','=',pedido),('product_id','=',produto)])
                if ordem.status != 'done':
                    ordem.update({'status':'done'})

