from odoo import models, fields, api

class CotizadorWizard(models.TransientModel):
    _name = 'cotizador.wizard'
    _description = 'Wizard Cotizador por Medios Pares'

    partner_id = fields.Many2one('res.partner', string='Paciente', required=True)
    graduacion_id = fields.Many2one('optica.graduacion', string='Graduación', required=True)
    
    
    serie_od = fields.Char(string='Serie Ojo Derecho')
    serie_oi = fields.Char(string='Serie Ojo Izquierdo')
    
    line_ids = fields.One2many('cotizador.wizard.line', 'wizard_id', string='Líneas de Cotización')

    def action_create_quotation(self):
        self.ensure_one()
        sale_order = self.env['sale.order'].create({
            'partner_id': self.partner_id.id,
            'origin': f"Graduación {self.graduacion_id.id}",
        })
        
        for line in self.line_ids:
            qty_to_sell = 2.0 if line.ojo == 'ambos' else 1.0
            
            self.env['sale.order.line'].create({
                'order_id': sale_order.id,
                'product_id': line.product_id.id,
                'name': f"{line.product_id.display_name} ({line.get_ojo_label()})",
                'product_uom_qty': qty_to_sell,
                'price_unit': line.price,
            })
            
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'form',
            'res_id': sale_order.id,
            'target': 'current',
        }


class CotizadorWizardLine(models.TransientModel):
    _name = 'cotizador.wizard.line'
    _description = 'Líneas del Cotizador por Ojo'

    wizard_id = fields.Many2one('cotizador.wizard', string='Wizard', ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Mica / Producto', required=True)
    
    #
    ojo = fields.Selection([
        ('od', 'Ojo Derecho (OD)'),
        ('oi', 'Ojo Izquierdo (OI)'),
        ('ambos', 'Ambos Ojos (Par)')
    ], string='Ojo', default='ambos', required=True)
    
    qty = fields.Float(string='Cantidad', default=1.0)
    price = fields.Monetary(string='Precio Unitario', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Moneda', default=lambda self: self.env.company.currency_id)

    def get_ojo_label(self):
        return dict(self._fields['ojo'].selection).get(self.ojo)

   @api.onchange('product_id', 'ojo')
    def _onchange_product_or_ojo(self):
        """ Calcula el precio unitario dependiendo del ojo seleccionado y su serie """
        if not self.product_id:
            return

        # Asignamos precio por defecto primero por seguridad
        self.price = self.product_id.lst_price

        # Si no hay wizard vinculado todavía, no podemos buscar series, salimos seguros
        if not self.wizard_id:
            return

        serie_a_buscar = False
        if self.ojo == 'od':
            serie_a_buscar = self.wizard_id.serie_od
            self.qty = 1.0
        elif self.ojo == 'oi':
            serie_a_buscar = self.wizard_id.serie_oi
            self.qty = 1.0
        elif self.ojo == 'ambos':
            # Si son ambos ojos pero las series son distintas, usamos la del derecho por defecto
            serie_a_buscar = self.wizard_id.serie_od
            self.qty = 2.0

        if not serie_a_buscar:
            return

        # Buscamos el precio mapeado en el modelo que corregimos hace un momento
        serie_price = self.env['optica.product.serie.price'].search([
            ('product_tmpl_id', '=', self.product_id.product_tmpl_id.id),
            ('serie_key', '=', serie_a_buscar)
        ], limit=1)

        if serie_price:
            self.price = serie_price.price
