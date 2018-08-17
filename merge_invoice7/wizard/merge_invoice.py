# -*- coding: utf-8 -*-
# © 2016-2018 e-thos SSII
# @author: Bernard Wilmus
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, exceptions
from openerp.tools.translate import _


class MergeInvoice(models.TransientModel):
    _name = "merge.invoice"
    _description = "Merge Partner Invoice"

    # For merging all selected invoice
    @api.multi
    def merge_all_invoices(self):
        inv_obj = self.env['account.invoice']
        allinvoices = {}
        aw_obj = self.env['ir.actions.act_window']
        ids = self.env.context.get('active_ids', [])
        invoices = inv_obj.browse(ids)
        if invoices:
            partners = []
            for invoice in invoices:
                partners.append(invoice.partner_id.id)
            partners = list(set(partners))
            if partners:
                for partner in partners:
                    partner_invoice = []
                    for record in invoices:
                        if record.partner_id.id == partner:
                            partner_invoice.append(record.id)
                    if partner_invoice:
                        invoice_objects = inv_obj.sudo().search([('id', 'in', partner_invoice)])
                        partner_criteria = self._partner_criteria_check(invoice_objects)
                        if partner_criteria['is_invoices'] == True and partner_criteria['mergable_inovice']:
                            mergable_inovices = partner_criteria['mergable_inovice']
                            for mergable_invoice in mergable_inovices:
                                ready_to_merge_inovice = self.env['account.invoice'].sudo().search(
                                    [('id', 'in', mergable_invoice)])
                                partner_invoices = ready_to_merge_inovice.do_merge()
                                allinvoices.update(partner_invoices)
        xid = {
            'out_invoice': 'action_invoice_tree1',
            'out_refund': 'action_invoice_tree3',
            'in_invoice': 'action_invoice_tree2',
            'in_refund': 'action_invoice_tree4',
        }[invoices[0].type]
        action = aw_obj.for_xml_id('account', xid)
        action.update({
            'domain': [('id', 'in', ids + allinvoices.keys())],
        })
        return action

    # For checking the criteria of the selected invoice that are going to merge
    @api.model
    def _partner_criteria_check(self, invoice_objects):
        partner_criteria = {}
        is_invoices = True
        invoice_list = []
        mergable_invoice_list = []
        if invoice_objects:
            if len(invoice_objects) < 2:
                is_invoices = False
            for invoice in invoice_objects:
                invoice_list = []
                for inv in invoice_objects:
                    is_ok_criteria = True
                    if invoice['state'] != 'draft':
                        is_ok_criteria = False
                    if invoice['account_id'] != inv['account_id']:
                        is_ok_criteria = False
                    if invoice['company_id'] != inv['company_id']:
                        is_ok_criteria = False
                    if invoice['type'] != inv['type']:
                        is_ok_criteria = False
                    if invoice['currency_id'] != inv['currency_id']:
                        is_ok_criteria = False
                    if invoice['journal_id'] != inv['journal_id']:
                        is_ok_criteria = False
                    if invoice['user_id'] != inv['user_id']:
                        invoice['user_id'] = inv['user_id']
                    if is_ok_criteria == True:
                        invoice_list.append(inv.id)
                mergable_invoice_list.append(invoice_list)
            mergable_invoice_list = sorted(mergable_invoice_list)
            mergable_invoice_list = [mergable_invoice_list[i] for i in range(len(mergable_invoice_list)) if
                                     i == 0 or mergable_invoice_list[i] != mergable_invoice_list[i - 1]]
            for inv_list in mergable_invoice_list:
                if len(inv_list) < 2:
                    mergable_invoice_list.remove(inv_list)
            partner_criteria['is_invoices'] = is_invoices
            partner_criteria['mergable_inovice'] = mergable_invoice_list
        return partner_criteria
