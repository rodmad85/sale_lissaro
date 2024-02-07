# Copyright 2022 Madureira Ind. e Com.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Sale Lissaro',
    'description': """
        Este módulo adequa a visualização Kanban do módulo de Vendas e adapta o módulo sale_project a trabalhar com produtos.""",
    'version': '14.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Madureira Ind. e Com.',
    'website': 'www.madureira.ind.br',
    'depends': [
        'sale','sale_purchase_stock','sales_order_delivery_status',
    ],
    'data': [
        'views/sale_order.xml',
        'views/sale_project.xml',
    ],
    'demo': [
    ],
    "installable": True,
}
