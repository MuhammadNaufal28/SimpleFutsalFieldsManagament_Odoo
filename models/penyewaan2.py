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

from odoo import fields, models, _

class DoodexfutsalPenyewaan(models.Model):
    _name = 'doodexfutsal.penyewaan'
    _description = 'Doodexfutsal Penyewaan'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Field untuk nomor referensi
    referensi = fields.Char(
        string="Referensi",
        required=True, copy=False, readonly=True,
        default=lambda self: _('Referensi'),
        tracking=True
    )

    # Field untuk menandai apakah pelanggan adalah member
    membership = fields.Boolean(
        string='Apakah Member?',
        default=False,
        tracking=True
    )

    # Field untuk menyimpan data pelanggan
    pelanggan_id = fields.Many2one(
        comodel_name='doodexfutsal.pelanggan',
        string='Id Pelanggan',
        tracking=True
    )

    # Field untuk menyimpan nama member (dihasilkan oleh fungsi komputasi)
    id_member_pelanggan = fields.Char(
        compute='_compute_id_member_pelanggan',
        string='Nama Member',
        tracking=True
    )

    # Field untuk nama tim
    name = fields.Char(
        string='Nama Team',
        tracking=True
    )

    # Field untuk total pembayaran (dihasilkan oleh fungsi komputasi)
    total_payment = fields.Integer(
        compute='_compute_bayar',
        string='Total Pembayaran',
        store=True,
        tracking=True
    )

    # Field untuk metode pembayaran
    method = fields.Selection(
        string='Metode Pembayaran',
        selection=[('qris', 'Qris'), ('bank_transfer', 'Bank Transfer'), ('cash', 'Cash')],
        tracking=True
    )

    # Field untuk status pembayaran
    status = fields.Selection(
        string='Status',
        selection=[('done', 'Sudah Lunas'), ('notyet', 'Belum Lunas')],
        tracking=True
    )

    # Field untuk tanggal mulai penyewaan
    start_date = fields.Datetime(
        string='Start Date',
        required=True,
        tracking=True
    )

    # Field untuk tanggal akhir penyewaan
    end_date = fields.Datetime(
        string='End Date',
        required=True,
        tracking=True
    )

    # Field untuk tanggal transaksi
    tgl_transaksi = fields.Datetime(
        string='Tanggal Transaksi',
        default=fields.Datetime.now(),
        tracking=True
    )

    # Field untuk durasi penyewaan dalam jam (dihasilkan oleh fungsi komputasi)
    berapa_jam = fields.Integer(
        compute='_compute_total_jam',
        string='Berapa Jam',
        tracking=True
    )

    # Field untuk deskripsi penyewaan
    description = fields.Text(
        string='Description',
        tracking=True
    )

    # Catatan mengenai pembayaran DP
    notes2 = fields.Char(
        default="Jika pada saat booking tidak membayar dp maka akan hangus apabila ada tim lain yang ingin booking di hari yang sama",
        string='Catatan',
        tracking=True
    )

    # Field untuk menyimpan QR Code (dihasilkan oleh fungsi komputasi)
    qr_code = fields.Char(
        compute='_compute_qr_code',
        string='QR Code',
        tracking=True
    )

    # Field untuk tipe lapangan yang disewa
    tipe_lapangan_id = fields.Many2one(
        comodel_name='doodexfutsal.lapangan',
        string='Tipe Lapangan',
        domain=[('name','=','vinyl')],
        required=True,
        tracking=True
    )

    # Field untuk total biaya sewa (dihasilkan oleh fungsi komputasi)
    total_sewa = fields.Integer(
        compute='_compute_total_sewa',
        string='total_sewa',
        tracking=True
    )

    # Barang yang disewa
    barang_ids = fields.Many2many(
        comodel_name='doodexfutsal.barang',
        string='barang',
        tracking=True
    )

    # Karyawan yang bertanggung jawab
    karyawan_id = fields.Many2one(
        comodel_name='doodexfutsal.karyawan',
        string='Penanggung Jawab',
        tracking=True
    )

    # Detail penjualan barang
    detail_penjualan_barang_ids = fields.One2many(
        comodel_name='detailpenjualanbarang',
        inverse_name='penjualan_barang_id',
        string='Detail Penjualan Barang',
        tracking=True
    )

    # State dari penyewaan (draft, confirm, done, cancel)
    state = fields.Selection([
        ('draft', 'Draft'), ('confirm', 'Confirm'), ('done', 'Done'), ('cancel', 'Cancel')
    ], string='State', readonly=True, default="draft", required=True, tracking=True)


    # Fungsi untuk mengonfirmasi penyewaan
    def action_confirm(self):
        self.write({'state': 'confirm'})

    # Fungsi untuk menyelesaikan penyewaan
    def action_done(self):
        self.write({'state': 'done'})

    # Fungsi untuk membatalkan penyewaan
    def action_cancel(self):
        self.write({'state': 'cancel'})

    # Fungsi untuk mengembalikan ke status draft
    def action_draft(self):
        self.write({'state': 'draft'})

    # Fungsi komputasi untuk menghitung total pembayaran
    @api.depends('total_sewa', 'detail_penjualan_barang_ids.total_barang', 'membership')
    def _compute_bayar(self):
        for record in self:
            total_barang_price = sum(record.detail_penjualan_barang_ids.mapped('total_barang'))
            total_sewa = record.total_sewa

            if record.membership:
                potongan = 0.8 
                total_sewa *= potongan

            record.total_payment = total_sewa + total_barang_price

    # Fungsi komputasi untuk menghitung total biaya sewa
    @api.depends('berapa_jam', 'tipe_lapangan_id')
    def _compute_total_sewa(self):    
        for record in self:
            record.total_sewa = record.berapa_jam * record.tipe_lapangan_id.harga

    # Fungsi komputasi untuk menghitung durasi penyewaan dalam jam
    @api.depends('end_date', 'start_date')
    def _compute_total_jam(self):
        for record in self:
            if record.start_date and record.end_date:
                record.berapa_jam = (record.end_date - record.start_date).seconds // 3600
            else:
                record.berapa_jam = 0

    # Fungsi komputasi untuk menghasilkan QR Code
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

    # Fungsi untuk membuat nomor referensi otomatis
    @api.model
    def create(self, vals):
        if vals.get('referensi', _("New")) == _("New"):
            vals['referensi'] = self.env['ir.sequence'].next_by_code('referensi.penyewaan') or _("New")
        record = super(DoodexfutsalPenyewaan, self).create(vals)
        return record

    # Fungsi untuk menghapus data (hanya dapat dihapus jika dalam status draft)
    def unlink(self):
        for record in self:
            if record.state != 'draft':
                raise ValidationError('Cannot delete records other than in draft state')
        super(DoodexfutsalPenyewaan, self).unlink()

    # Fungsi komputasi untuk mengupdate nama member berdasarkan pelanggan
    @api.depends('pelanggan_id')
    def _compute_id_member_pelanggan(self):
        for record in self:
            record.id_member_pelanggan = record.pelanggan_id.nama
            record.name = record.pelanggan_id.team_name

# Model untuk detail penjualan barang
class Detailpenjualanbarang(models.Model):
    _name = 'detailpenjualanbarang'
    _description = 'Detailpenjualanbarang'

    # Nama barang
    name = fields.Char(string='Nama Barang')

    # Relasi dengan model penyewaan
    penjualan_barang_id = fields.Many2one(comodel_name='doodexfutsal.penyewaan', string='penjualan_barang')

    # Nama barang yang disewa
    list_barang_id = fields.Many2one(comodel_name='doodexfutsal.barang', string='Nama Barang')

    # Harga barang yang disewa (diambil dari relasi dengan model barang)
    harga_barang = fields.Integer(related='list_barang_id.harga_barang', string='Harga Barang', store=True)

    # Jumlah barang yang disewa
    qty = fields.Integer(string='Quantity')

    # Total harga barang yang disewa (dihasilkan oleh fungsi komputasi)
    total_barang = fields.Integer(compute='_compute_total_barang', string='Total')

    # Fungsi komputasi untuk menghitung total harga barang yang disewa
    @api.depends('qty', 'harga_barang')
    def _compute_total_barang(self):
        for record in self:
            record.total_barang = record.qty * record.harga_barang
