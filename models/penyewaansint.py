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

class DoodexfutsalPenyewaansintetis(models.Model):
    _name = 'doodexfutsal.penyewaansintetis'
    _description = 'Doodexfutsal Penyewaansintetis'

    referensi = fields.Char(
        string="Referensi",
        required=True, copy=False, readonly=True,
        default=lambda self: _('Referensi'))
    membership = fields.Boolean(string='Apakah Member?', default=False)
    pelanggan_id = fields.Many2one(comodel_name='doodexfutsal.pelanggan', string='Id Pelanggan')
    id_member_pelanggan = fields.Char(compute='_compute_id_member_pelanggan', string='Nama Member')
    name = fields.Char(string='Nama Team')
    total_payment = fields.Integer(compute='_compute_bayar', string='Total Pembayaran', store=True)
    method = fields.Selection(string='Metode Pembayaran', selection=[('qris', 'Qris'), ('bank_transfer', 'Bank Transfer'), ('cash', 'Cash'),])
    status = fields.Selection(string='Status', selection=[('done', 'Sudah Lunas'), ('notyet', 'Belum Lunas'),])
    start_date = fields.Datetime(string='Start Date', required=True)
    end_date = fields.Datetime(string='End Date', required=True)
    berapa_jam = fields.Integer(compute='_compute_total_jam', string='Berapa Jam')
    tgl_transaksi = fields.Datetime(string='Tanggal Transaksi', default=fields.Datetime.now())    
    description = fields.Text(string='Description')
    notes2 = fields.Char(default="Jika pada saat booking tidak membayar dp maka akan hangus apabila ada tim lain yang ingin booking di hari yang sama", string='Catatan')
    qr_code = fields.Char(compute='_compute_qr_code', string='QR Code')
    tipe_lapangan_id = fields.Many2one(comodel_name='doodexfutsal.lapangan', string='Tipe Lapangan', default='sintetis',  domain=[('name','=','sintetis')])
    total_sewa = fields.Integer(compute='_compute_total_sewa', string='total_sewa')
    barang_ids = fields.Many2many(comodel_name='doodexfutsal.barang', string='barang')
    karyawan_id = fields.Many2one(comodel_name='doodexfutsal.karyawan', string='Penanggung Jawab')
    detail_penjualan_barang_ids = fields.One2many(comodel_name='detailpenjualanbarang', inverse_name='penjualan_barang_id', string='Detail Penjualan Barang')
    state = fields.Selection([
        ('draft', 'Draft'), ('confirm', 'Confirm'), ('done', 'Done'), ('cancel', 'Cancel')
    ], string='State', readonly=True, default="draft", required=True)

    def action_confirm(self):
        self.write({'state': 'confirm'})

    def action_done(self):
        self.write({'state': 'done'})

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def action_draft(self):
        self.write({'state': 'draft'})

    @api.depends('total_sewa', 'detail_penjualan_barang_ids.total_barang', 'membership')
    def _compute_bayar(self):
        for record in self:
            total_barang_price = sum(record.detail_penjualan_barang_ids.mapped('total_barang'))
            total_sewa = record.total_sewa

            if record.membership:
                # Berikan potongan 20% hanya pada total_sewa jika membership diatur sebagai True
                potongan = 0.2  # 20%
                total_sewa *= (1 - potongan)

            record.total_payment = total_sewa + total_barang_price

    @api.depends('berapa_jam', 'tipe_lapangan_id')
    def _compute_total_sewa(self):
        for record in self:
            record.total_sewa = record.berapa_jam * record.tipe_lapangan_id.harga


    @api.depends('end_date', 'start_date')
    def _compute_total_jam(self):
        for record in self:
            if record.start_date and record.end_date:
                record.berapa_jam = (record.end_date - record.start_date).seconds // 3600
            else:
                record.berapa_jam = 0

    @api.depends('referensi')
    def _compute_qr_code(self):
        for record in self:
            if qrcode and base64:
                qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=3, border=4)
                qr.add_data(record.referensi)
                qr.make(fit=True)
                img = qr.make_image()
                temp = BytesIO()
                img.save(temp, format="PNG")
                qr_image = base64.b64encode(temp.getvalue())
                record.update({'qr_code': qr_image})

    @api.model
    def create(self, vals):
        if vals.get('referensi', _("New")) == _("New"):
            vals['referensi'] = self.env['ir.sequence'].next_by_code('referensi.penyewaan.sintetis') or _("New")
        record = super(DoodexfutsalPenyewaansintetis, self).create(vals)
        return record

    def unlink(self):
        if self.filtered(lambda line : line.state != 'draft'):
            raise ValidationError('Tidak dapat menghapus selain draft')

    @api.depends('pelanggan_id')
    def _compute_id_member_pelanggan(self):
        for record in self:
            record.id_member_pelanggan = record.pelanggan_id.nama

class Detailpenjualanbarangsint(models.Model):
    _name = 'detailpenjualanbarangsint'
    _description = 'Detailpenjualanbarangsint'

    name = fields.Char(string='Nama Barang')
    penjualan_barang_id = fields.Many2one(comodel_name='doodexfutsal.penyewaan', string='penjualan_barang')
    list_barang_id = fields.Many2one(comodel_name='doodexfutsal.barang', string='Nama Barang')
    harga_barang = fields.Integer(related='list_barang_id.harga_barang', string='Harga Barang', store=True)  # Tambahkan field harga_barang
    qty = fields.Integer(string='Quantity')
    total_barang = fields.Integer(compute='_compute_total_barang', string='Total')

    @api.depends('qty', 'harga_barang')
    def _compute_total_barang(self):
        for record in self:
            record.total_barang = record.qty * record.harga_barang
    