from odoo import models, fields, api, _




class DoodexfutsalBarang(models.Model):
    _name = 'doodexfutsal.barang'
    _description = 'Doodexfutsal Barang'

    name = fields.Char(string='Nama Barang')
    harga_barang = fields.Integer(string='Harga Barang')
    
    
    
    
    



    
    
    
