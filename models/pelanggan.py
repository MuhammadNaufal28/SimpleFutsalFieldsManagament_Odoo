from odoo import models, fields, api, _
from io import BytesIO
from odoo.exceptions import ValidationError, UserError

try:
    import qrcode
except ImportError:
    qrcode = None
try:
    import base64
except ImportError:
    base64 = None


class DoodexfutsalPelanggan(models.Model):
    _name = 'doodexfutsal.pelanggan'
    _description = 'Doodexfutsal Pelanggan'
    _rec_name = 'id_member'

    id_member = fields.Char(
        string="Id Member",
        required=True, copy=False, readonly=True,
        default=lambda self: _('Id Member'))
    email = fields.Char(string='Email')
    nama = fields.Char(string='Nama')
    gender = fields.Selection(string='Jenis Kelamin', selection=[('pria', 'Pria'), ('wanita', 'Wanita'),])
    tgl_daftar = fields.Date(string='Tanggal Daftar', default=fields.Date.today())
    alamat = fields.Char(string='Alamat')
    no_telp = fields.Char(string='No Telepon')
    second_person = fields.Char(string='Penanggung Jawab Kedua')
    no_telp2 = fields.Char(string='No Telepon Penanggung Jawab Kedua')
    notes = fields.Html(string='Catatan')
    qr_code = fields.Char(compute='_compute_qr_code', string='QR Code')    

    @api.depends('id_member')
    def _compute_qr_code(self):
        for record in self:
            if qrcode and base64:
                qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=3, border=4)
                qr.add_data(record.id_member)
                qr.make(fit=True)
                img = qr.make_image()
                temp = BytesIO()
                img.save(temp, format="PNG")
                qr_image = base64.b64encode(temp.getvalue())
                record.update({'qr_code': qr_image})
    

    @api.model
    def create(self, vals):
        if vals.get('id_member', _("New")) == _("New"):
            vals['id_member'] = self.env['ir.sequence'].next_by_code('id_member.pelanggan') or _("New")
        record = super(DoodexfutsalPelanggan, self).create(vals)
        return record
    
    
    
    
    


    
