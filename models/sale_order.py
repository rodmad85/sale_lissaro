
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

    class SaleLissaro(models.Model):
        _inherit = "sale.order"

        delivery_status = fields.Selection(selection=[
            ('nothing', 'Sem Entrega'), ('to_deliver', 'Para Entregar'),
            ('partial', 'Parcialmente Entregue'), ('delivered', 'Entregue'),
            ('processing', 'Processando')
        ], string='Status Entrega', compute='_compute_delivery_status', store=True,
            readonly=True, copy=False, default='nothing')
        product_kanban = fields.Many2many(
            "product.product",
            string="Products",
            compute="_compute_product_ids",
            store=True
        )

        @api.depends("order_line.product_id")
        def _compute_product_ids(self):
            for order in self:
                products = order.order_line.mapped("product_id")
                order.product_kanban = [(6, 0, products.ids)] if products else [(6, 0, [])]  # Evita valores None
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
