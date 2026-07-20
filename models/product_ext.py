# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    lens_type = fields.Selection([
        ('monofocal', 'Monofocal'),
        ('bifocal', 'Bifocal'),
        ('progresivo', 'Progresivo'),
        ('blended', 'Blended'),
        ('otros', 'Otros')
    ], string='Tipo de Lente', default='monofocal')[cite: 1]

    serie_price_ids = fields.One2many(
        'optica.product.serie.price', 
        'product_tmpl_id', 
        string='Precios por Serie'
    )[cite: 1]


# Esta clase va completamente afuera, al mismo nivel (alineada a la izquierda)
class OpticaProductSeriePrice(models.Model):
    _name = 'optica.product.serie.price'
    _description = 'Precio del producto por serie'[cite: 1]

    product_tmpl_id = fields.Many2one('product.template', 'Producto', required=True, ondelete='cascade')[cite: 1]
    
    # Cambiamos Many2one por Selection para que use tus llaves estáticas del diccionario (RX1, RX2, RX3)
    serie_key = fields.Selection([
        ('RX1', 'Primera Serie'),
        ('RX2', 'Segunda Serie'),
        ('RX3', 'Tercera Serie')
    ], string='Serie de Mica', required=True)
    
    price = fields.Monetary('Precio', currency_field='currency_id')[cite: 1]
    currency_id = fields.Many2one('res.currency', string='Moneda', default=lambda self: self.env.company.currency_id)[cite: 1]

    # Restricción opcional para que no te deje repetir la misma serie en el mismo producto
    _sql_constraints = [
        ('uniq_product_serie', 'unique(product_tmpl_id, serie_key)', 'Ya existe un precio asignado a esta serie para este producto.')
    ]
