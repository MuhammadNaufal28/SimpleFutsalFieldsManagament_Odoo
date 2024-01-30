from odoo import models, fields, api, _

class DoodexfutsalKaryawan(models.Model):
    _name = 'doodexfutsal.karyawan'
    _description = 'Doodexfutsal Karyawan'
    

    name = fields.Char(string='Nama')
    bagian = fields.Selection(string='Bagian', 
                              selection=[('kasir', 'Kasir'), 
                                         ('kebersihan', 'Kebersihan'), 
                                         ('manajer_lapangan', 'Manajer Lapangan'),], 
                              required=True)

    gaji = fields.Integer(string='Gaji per bulan')
    alamat = fields.Html(string='Alamat')
    gender = fields.Selection(string='Gender', selection=[('pria', 'Pria'), ('wanita', 'Wanita'),])
    foto = fields.Image(string='foto', max_width=3, max_height=4)
    