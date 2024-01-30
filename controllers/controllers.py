# -*- coding: utf-8 -*-
# from odoo import http


# class FutsalProject(http.Controller):
#     @http.route('/futsal_project/futsal_project', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/futsal_project/futsal_project/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('futsal_project.listing', {
#             'root': '/futsal_project/futsal_project',
#             'objects': http.request.env['futsal_project.futsal_project'].search([]),
#         })

#     @http.route('/futsal_project/futsal_project/objects/<model("futsal_project.futsal_project"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('futsal_project.object', {
#             'object': obj
#         })
