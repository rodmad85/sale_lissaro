
from odoo import fields, models, api

class OrcaTabela(models.TransientModel):
    _name="orca.tabela"
    _description = "Tabela de orçamento"

    fiscal = fields.Many2one('account.fiscal.position', string='Posição Fiscal', related='linha.order_id.fiscal_position_id')
    linha = fields.Many2one('sale.order.line', string='Linha Pedido')
    pedido = fields.Many2one('sale.order', string='Pedido de Venda', related='linha.order_id')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id, readonly=True)
    mp = fields.Monetary(string='Matéria Prima')
    mo = fields.Integer(string='Horas MO')
    mo_valor = fields.Monetary(string='Valor Hora MO')
    mo_total = fields.Monetary(string='Total Mão de Obra')
    terc = fields.Monetary(string='Terceiros')
    total = fields.Monetary(string='Total Orçado')
    lucro =fields.Float(string='% Lucro', default=30)
    custos = fields.Float(string='% Custos')
    comissao = fields.Float(string='% Comissão')

    valor_custo= fields.Monetary(string='Total Custo Fixo', help='Valor proporcional ao custo fixo.')
    valor_venda = fields.Monetary(string='Valor de Venda', compute='calcular')
    valor_serv = fields.Monetary(string='Valor Serviço',compute='calcular')
    valor_ind = fields.Monetary(string='Valor Industrialização',compute='calcular')

    cvenda =fields.Monetary(string='Valor Custo Fixo Venda', help='Valor proporcional da venda ao custo fixo')
    cind = fields.Monetary(string='Valor Custo Fixo Industrialização', help='Valor proporcional da industrialização ao custo fixo')
    cserv = fields.Monetary(string='Valor Custo Fixo Servico', help='Valor proporcional do serviço ao custo fixo')
    product_id = fields.Many2many(
        'product.product', 'prod_orca_rel','prod_id', 'orca_id', string='Product',
        domain="[('sale_ok', '=', True), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        change_default=True, ondelete='restrict', check_company=True)
    # Unrequired company
    produto = fields.Many2one('product.product', string='Produto', related='linha.product_id')
    imposto_venda = fields.Float(string="Imposto Venda %")
    impv_valor = fields.Monetary(string="Imposto Venda $")
    imposto_ind = fields.Float(string="Imposto Industrialização %")
    impi_valor = fields.Monetary(string="Imposto Industrialização $")
    imposto_serv = fields.Float(string="Imposto Serviço %")
    imps_valor =fields.Monetary(string="Imposto Serviço $")

    resulv = fields.Monetary(string="Resultado Venda")
    resuli = fields.Monetary(string="Resultado Industrialização")
    resuls = fields.Monetary(string="Resultado Serviço")



    def default_get(self, fields):
        res = super(OrcaTabela, self).default_get(fields)
        value = self.env['ir.config_parameter'].sudo().get_param('orcamento.custo_fixo')
        vvenda = self.env['ir.config_parameter'].sudo().get_param('orcamento.venda')
        vhora = self.env['ir.config_parameter'].sudo().get_param('orcamento.vhora')
        vservico = self.env['ir.config_parameter'].sudo().get_param('orcamento.servico')
        vindus = self.env['ir.config_parameter'].sudo().get_param('orcamento.industrializacao')
        pedido = self.env.context.get('active_id')

        res.update({
            'custos': value,
            'mo_valor':vhora,
            'imposto_venda': vvenda,
            'imposto_serv': vservico,
            'imposto_ind':vindus,
            'linha': pedido,
        })

        return res



    def seleciona(self):
        if self.fiscal.name == 'Venda':
            self.env['sale.order.line'].browse(self.linha.id).write({'price_unit': self.valor_venda})
        if self.fiscal.name == 'Industrialização':
            self.env['sale.order.line'].browse(self.linha.id).write({'price_unit': self.valor_ind})
        if self.fiscal.name == 'Serviço':
            self.env['sale.order.line'].browse(self.linha.id).write({'price_unit': self.valor_serv})
        return{}

    def salva_orca(self):
        self.ensure_one()
        vals = {
            'produto': self.produto.id,
            'fiscal': self.fiscal.id,
            'mp': self.mp,
            'mo': self.mo,
            'mo_valor': self.mo_valor,
            'mo_total': self.mo_total,
            'terc': self.terc,
            'lucro': self.lucro,
            'comissao': self.comissao,
            'custos': self.custos,
            'imposto_venda': self.imposto_venda,
            'imposto_ind': self.imposto_ind,
            'imposto_serv': self.imposto_serv,
            'valor_venda': self.valor_venda,
            'valor_serv': self.valor_serv,
            'valor_ind': self.valor_ind,
            'linha': self.linha.id,
        }

        new_rec = self.env['orca.geral'].create(vals)
        if self.fiscal.name == 'Venda':
            self.env['sale.order.line'].browse(self.linha.id).write({'price_unit': self.valor_venda})
        if self.fiscal.name == 'Industrialização':
            self.env['sale.order.line'].browse(self.linha.id).write({'price_unit': self.valor_ind})
        if self.fiscal.name == 'Serviço':
            self.env['sale.order.line'].browse(self.linha.id).write({'price_unit': self.valor_serv})
        return new_rec

    @api.onchange('mp','mo','mo_valor','terc','lucro')
    def calcular(self):

        custovenda = (self.custos + self.imposto_venda)
        custoind = (self.custos + self.imposto_ind)
        custoserv = (self.custos + self.imposto_serv)

        indicevenda = custovenda + self.lucro
        indiceind = custoind + self.lucro
        indiceserv = custoserv + self.lucro

        indv = (100)/(100-indicevenda)
        indi = (100)/(100-indiceind)
        inds = (100)/(100-indiceserv)

        self.write({'mo_total': self.mo_valor * self.mo})
        self.write({'total': self.mo_total + self.mp + self.terc})
        self.write({'valor_venda': self.total * indv,'valor_ind': self.total * indi,'valor_serv': self.total * inds})

        cv = (self.valor_venda * (self.custos / 100))
        ci = (self.valor_ind * (self.custos / 100))
        cs = (self.valor_serv * (self.custos / 100))

        impv = self.valor_venda / self.imposto_venda
        imps = self.valor_serv / self.imposto_serv
        impi = self.valor_ind / self.imposto_ind

        self.write({'cvenda': cv, 'cind': ci, 'cserv': cs})
        self.write({'impv_valor': impv, 'impi_valor': impi, 'imps_valor': imps})

        resv = (self.valor_venda - cv - impv - self.total)
        resi = (self.valor_ind - ci - impi - self.total)
        ress = (self.valor_serv - cs - imps - self.total)

        self.write({'resulv': resv, 'resuli': resi, 'resuls': ress})


    # class OrcaSaleLine(models.Model):
#     _inherit = "sale.order"
#
#     def _tabela(self):
#         view_id = self.env.ref('orcamento.orca_tabela_form').id
#         return {
#             'name':'Tabela Orçamento',
#             'view_mode': 'form',
#             'view_id': view_id,
#             'view_type': 'form',
#             'res_model': 'object name',
#             'type': 'ir.actions.act_window',
#             'target': 'new',
#         }

class OrcaGeral(models.Model):

    _name = "orca.geral"
    _description = "Listagem de orçamentos"
    name = fields.Char(string='Orçamento')
    fiscal = fields.Many2one('account.fiscal.position', string='Posição Fiscal')
    linha = fields.Many2one('sale.order.line', string='Linha Pedido')
    pedido = fields.Many2one('sale.order', string='Pedido de Venda', related='linha.order_id')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id, readonly=True)
    mp = fields.Monetary(string='Matéria Prima')
    mo = fields.Integer(string='Horas MO')
    mo_valor = fields.Monetary(string='Valor Hora MO')
    mo_total = fields.Monetary(string='Total Mão de Obra')
    terc = fields.Monetary(string='Terceiros')
    total = fields.Monetary(string='Total Orçado', compute='calcula')
    lucro = fields.Float(string='% Lucro', default=30)
    custos = fields.Float(string='% Custos')
    comissao = fields.Float(string='% Comissão')
    produto = fields.Many2one('product.product', string='Produto')

    valor_custo = fields.Monetary(string='Total Custo Fixo', help='Valor proporcional ao custo fixo.')
    valor_venda = fields.Monetary(string='Valor de Venda')
    valor_serv = fields.Monetary(string='Valor Serviço')
    valor_ind = fields.Monetary(string='Valor Industrialização')

    cvenda = fields.Monetary(string='Valor Custo Fixo Venda', help='Valor proporcional da venda ao custo fixo')
    cind = fields.Monetary(string='Valor Custo Fixo Industrialização',
                           help='Valor proporcional da industrialização ao custo fixo')
    cserv = fields.Monetary(string='Valor Custo Fixo Servico', help='Valor proporcional do serviço ao custo fixo')

    imposto_venda = fields.Float(string="Imposto Venda %")
    impv_valor = fields.Monetary(string="Imposto Venda $")
    imposto_ind = fields.Float(string="Imposto Industrialização %")
    impi_valor = fields.Monetary(string="Imposto Industrialização $")
    imposto_serv = fields.Float(string="Imposto Serviço %")
    imps_valor = fields.Monetary(string="Imposto Serviço $")

    resulv = fields.Monetary(string="Resultado Venda")
    resuli = fields.Monetary(string="Resultado Industrialização")
    resuls = fields.Monetary(string="Resultado Serviço")

    def default_get(self, fields):

        res = super(OrcaGeral, self).default_get(fields)
        value = self.env['ir.config_parameter'].sudo().get_param('orcamento.custo_fixo')
        vvenda = self.env['ir.config_parameter'].sudo().get_param('orcamento.venda')
        vhora = self.env['ir.config_parameter'].sudo().get_param('orcamento.vhora')
        vservico = self.env['ir.config_parameter'].sudo().get_param('orcamento.servico')
        vindus = self.env['ir.config_parameter'].sudo().get_param('orcamento.industrializacao')
        pedido = self.env.context.get('active_id')

        res.update({
            'custos': value,
            'mo_valor':vhora,
            'imposto_venda': vvenda,
            'imposto_serv': vservico,
            'imposto_ind':vindus,
            'linha': pedido,
        })

        return res

    @api.onchange('mp', 'mo', 'mo_valor', 'terc', 'lucro')
    def calcula(self):
        custovenda = (self.custos + self.imposto_venda)
        custoind = (self.custos + self.imposto_ind)
        custoserv = (self.custos + self.imposto_serv)

        indicevenda = custovenda + self.lucro
        indiceind = custoind + self.lucro
        indiceserv = custoserv + self.lucro

        indv = (100) / (100 - indicevenda)
        indi = (100) / (100 - indiceind)
        inds = (100) / (100 - indiceserv)

        self.write({'mo_total': self.mo_valor * self.mo})
        self.write({'total': self.mo_total + self.mp + self.terc})
        self.write({'valor_venda': self.total * indv, 'valor_ind': self.total * indi, 'valor_serv': self.total * inds})

        cv = (self.valor_venda * (self.custos / 100))
        ci = (self.valor_ind * (self.custos / 100))
        cs = (self.valor_serv * (self.custos / 100))

        impv = self.valor_venda / self.imposto_venda
        imps = self.valor_serv / self.imposto_serv
        impi = self.valor_ind / self.imposto_ind

        self.write({'cvenda': cv, 'cind': ci, 'cserv': cs})
        self.write({'impv_valor': impv, 'impi_valor': impi, 'imps_valor': imps})

        resv = (self.valor_venda - cv - impv - self.total)
        resi = (self.valor_ind - ci - impi - self.total)
        ress = (self.valor_serv - cs - imps - self.total)

        self.write({'resulv': resv, 'resuli': resi, 'resuls': ress})

    @api.model
    def create(self, vals):
        if vals.get('name', ('New')) == ('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('orca.seq') or ('New')
            result = super(OrcaGeral, self).create(vals)

            return result


class OrcaConfig(models.TransientModel):
    _inherit = 'res.config.settings'

    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id, readonly=True)
    custo_fixo = fields.Float(string='Custo Fixo %')
    venda = fields.Float(string='Imposto Venda %')
    servico = fields.Float(string='Imposto Serviço %')
    industrializacao = fields.Float(string='Imposto Industrialização %')
    vhora = fields.Monetary(string='Valor Hora')
    # impostos = fields.Many2many('orca.impostos', 'orca_impostos_rel', 'orca_id', 'imposto_id',
    #                             string='Arquivos', store=True, copy=True, limit=3)

    def set_values(self):
        """employee setting field values"""
        res = super(OrcaConfig, self).set_values()
        self.env['ir.config_parameter'].set_param('orcamento.custo_fixo', self.custo_fixo)
        self.env['ir.config_parameter'].set_param('orcamento.vhora', self.vhora)
        self.env['ir.config_parameter'].set_param('orcamento.venda', self.venda)
        self.env['ir.config_parameter'].set_param('orcamento.servico', self.servico)
        self.env['ir.config_parameter'].set_param('orcamento.industrializacao', self.industrializacao)
        return res

    def get_values(self):

        res = super(OrcaConfig, self).get_values()
        value = self.env['ir.config_parameter'].sudo().get_param('orcamento.custo_fixo')
        vhora = self.env['ir.config_parameter'].sudo().get_param('orcamento.vhora')
        vvenda = self.env['ir.config_parameter'].sudo().get_param('orcamento.venda')
        vservico = self.env['ir.config_parameter'].sudo().get_param('orcamento.servico')
        vindus = self.env['ir.config_parameter'].sudo().get_param('orcamento.industrializacao')
        res.update(
            custo_fixo=float(value),
            vhora=vhora,
            venda=float(vvenda),
            servico=float(vservico),
            industrializacao=float(vindus),
        )
        return res

class OrcaImpostos(models.Model):
    _name="orca.impostos"

    name=fields.Selection([('venda', 'Venda'), ('industrializacao', 'Industrialização'), ('servico', 'Serviço')],
        string='Tipo', store=True, copy=True, default='venda')
    icms = fields.Float(string='ICMS %')
    ipi = fields.Float(string='IPI %')
    pis = fields.Float(string='PIS %')
    cofins = fields.Float(string='COFINS %')
    ir = fields.Float(string='IR %')
    csl = fields.Float(string='CSL %')
    iss = fields.Float(string='ISS %')
    cpp = fields.Float(string='CPP %')
    total_imp = fields.Float(string='Total %', compute='_total_imp', store=True)



    @api.onchange('pis','icms','cofins','ir','csl','iss','cpp')
    def _total_imp(self):
        for rec in self:
            rec.update({'total_imp': rec.ipi + rec.pis + rec.cofins + rec.ir + rec.csl + rec.iss + rec.cpp + rec.icms})