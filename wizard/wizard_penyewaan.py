from odoo import models, fields, api

class WhatsappSendMessage(models.TransientModel):
    _name = 'whatsapp.message.wizard'

    pelanggan_id = fields.Many2one('doodexfutsal.pelanggan', string='pelanggan')
    # nama_team = fields.Char(related='pelanggan_id.team_name', string="Nama Team", readonly=True)
    contact = fields.Char(string='No Telepon')
    message = fields.Text(string='Pesan')


    def send_message(self):
        print("got it")

    