# -*- coding: utf-8 -*-

from odoo import models, fields, api

class OptometriaLaboratorio(models.Model):
    _name = 'optometria.laboratorio'
    _description = 'Laboratorios Proveedores de Lentes'
    _order = 'name'
    
    name = fields.Char(
        string='Nombre del Laboratorio',
        required=True,
        help='Nombre del laboratorio o proveedor'
    )
    
    telefono = fields.Char(
        string='Teléfono',
        help='Teléfono de contacto'
    )
    
    email = fields.Char(
        string='Email',
        help='Correo electrónico de contacto'
    )
    
    dias_entrega = fields.Integer(
        string='Días de Entrega',
        default=5,
        help='Tiempo promedio de entrega en días'
    )
    
    activo = fields.Boolean(
        string='Activo',
        default=True,
        help='¿El laboratorio sigue activo?'
    )
    
    notas = fields.Text(
        string='Notas',
        help='Observaciones adicionales sobre el laboratorio'
    )
    
    # Campo computado para contar productos
    total_productos = fields.Integer(
        string='Total de Productos',
        compute='_compute_total_productos',
        store=False
    )
    
    @api.depends('name')
    def _compute_total_productos(self):
        """Cuenta cuántos productos tiene este laboratorio"""
        for record in self:
            record.total_productos = self.env['product.template'].search_count([
                ('laboratorio_id', '=', record.id)
            ])
    
    def action_ver_productos(self):
        """Botón para ver todos los productos de este laboratorio"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Productos de {self.name}',
            'res_model': 'product.template',
            'view_mode': 'tree,form',
            'domain': [('laboratorio_id', '=', self.id)],
            'context': {'default_laboratorio_id': self.id},
        }
