
from odoo import models, api, fields
from odoo.tools.sql import column_exists, create_column

class SaleLissaro(models.Model):
    _inherit= "sale.order"

    delivery_status = fields.Selection(selection=[
        ('nothing', 'Sem Entrega'), ('to_deliver', 'Para Entregar'),
        ('partial', 'Parcialmente Entregue'), ('delivered', 'Entregue'),
        ('processing', 'Processando')
    ], string='Status Entrega', compute='_compute_delivery_status', store=True,
        readonly=True, copy=False, default='nothing')
class SaleOrderLissaro(models.Model):
    _inherit = "sale.order.line"

    @api.depends('product_id.type')
    def _compute_is_service(self):
        for so_line in self:
            so_line.is_service = True

    @api.depends('product_id.type')
    def _compute_product_updatable(self):
        for line in self:
            if line.state == 'sale':
                line.product_updatable = False
            else:
                super(SaleOrderLissaro, line)._compute_product_updatable()

    def _auto_init(self):
        """
        Create column to stop ORM from computing it himself (too slow)
        """
        if not column_exists(self.env.cr, 'sale_order_line', 'is_service'):
            create_column(self.env.cr, 'sale_order_line', 'is_service', 'bool')
            self.env.cr.execute("""
                UPDATE sale_order_line line
                SET is_service = (pt.type = 'service')
                FROM product_product pp
                LEFT JOIN product_template pt ON pt.id = pp.product_tmpl_id
                WHERE pp.id = line.product_id
            """)
        return super()._auto_init()
