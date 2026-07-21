from odoo import models, fields, api

class OpticaGraduacion(models.Model):
    _inherit = 'optica.graduacion'

    def action_open_cotizador(self):
        """ Abre el Wizard pasando de manera independiente la serie de cada ojo """
        self.ensure_one()
        
        return {
            'name': 'Cotizador de Lentes',
            'type': 'ir.actions.act_window',
            'res_model': 'cotizador.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_partner_id': self.paciente_id.id if hasattr(self, 'paciente_id') else False,
                'default_graduacion_id': self.id,
                'default_serie_od': self.serie_recomendada_od,
                'default_serie_oi': self.serie_recomendada_oi,
            }
        }
