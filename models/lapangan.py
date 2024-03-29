from odoo import models, fields, api, _



class DoodexfutsalLapangan(models.Model):
    _name = 'doodexfutsal.lapangan'
    _description = 'Doodexfutsal Lapangan'

    name = fields.Selection(string='Tipe Lapangan', selection=[('vinyl', 'Vinyl'), ('sintetis', 'Sintetis'),])
    harga = fields.Integer(string='Harga')
    
    
    