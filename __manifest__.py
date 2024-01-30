# -*- coding: utf-8 -*-
{
    'name': "futsal_project",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/referensi_pelanggan.xml',
        'data/referensi_penyewaan.xml',
        'data/referensi_penyewaan_sintetis.xml',
        'report/report.xml',
        'report/report_penyewaan_futsal.xml',
        'report/report_penyewaan_sintetis.xml',
        'report/report_pelanggan_futsal.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/menu_view.xml',
        'views/pelanggan_view.xml',
        'views/penyewaan_view2.xml',
        'views/lapangan_view.xml',
        'views/barang_view.xml',
        'views/karyawan_view.xml',
        'views/penyewaansint_view.xml',
        'views/sales_view_sintetis.xml',        
        'views/sales_view_vinyl.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
