
from odoo import fields, models


class ProjectTaskLissaro(models.Model):
    _inherit = "project.task"

    sale_line_id = fields.Many2one(
        'sale.order.line', 'Sales Order Item',
        domain="[('company_id', '=', company_id), ('order_partner_id', 'child_of', commercial_partner_id), ('is_expense', '=', False), ('state', 'in', ['sale', 'done']), ('order_id', '=?', project_sale_order_id)]",
        compute='_compute_sale_line', store=True, readonly=False, copy=False,
        help="Sales order item to which the project is linked. Link the timesheet entry to the sales order item defined on the project. "
             "Only applies on tasks without sale order item defined, and if the employee is not in the 'Employee/Sales Order Item Mapping' of the project.")
