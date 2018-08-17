# -*- coding: utf-8 -*-
# © 2016-2018 e-thos SSII
# @author: Bernard Wilmus
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api
from openerp import workflow
from openerp.osv.orm import browse_record, browse_null
from openerp.tools import float_is_zero


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    #For getting the invoice fields that need to cinsider in invoice merging process
    @api.model
    def _get_invoice_key_cols(self):
        return [
            'partner_id', 'user_id', 'type', 'account_id', 'currency_id',
            'journal_id', 'company_id', 'partner_bank_id'
        ]

    #For getting the invoice line fields that need to cinsider in invoice merging process
    @api.model
    def _get_invoice_line_key_cols(self):
        fields = [
            'name', 'origin', 'discount', 'invoice_line_tax_ids', 'price_unit',
            'product_id', 'account_id', 'account_analytic_id',
            'uom_id','sale_line_ids'
        ]
        for field in ['analytics_id']:
            if field in self.env['account.invoice.line']._fields:
                fields.append(field)
        return fields

    #For getting the invoice fields values in invoice merging process
    @api.model
    def _get_first_invoice_fields(self, invoice):
        return {
            'origin': '%s' % (invoice.origin or '',),
            'partner_id': invoice.partner_id.id,
            'journal_id': invoice.journal_id.id,
            'user_id': invoice.user_id.id,
            'currency_id': invoice.currency_id.id,
            'company_id': invoice.company_id.id,
            'type': invoice.type,
            'account_id': invoice.account_id.id,
            'state': 'draft',
            'reference': '%s' % (invoice.reference or '',),
            'name': '%s' % (invoice.name or '',),
            'fiscal_position_id': invoice.fiscal_position_id.id,
            'payment_term_id': invoice.payment_term_id.id,
            'invoice_line_ids': {},
            'partner_bank_id': invoice.partner_bank_id.id,
        }

    #For merging the selected invoice of partner
    @api.multi
    def do_merge(self, remove_empty_invoice_lines=True):
        def make_key(br, fields):
            list_key = []
            for field in fields:
                field_val = getattr(br, field)
                if field in ('product_id', 'account_id'):
                    if not field_val:
                        field_val = False
                if (isinstance(field_val, browse_record) and
                        field != 'invoice_line_tax_ids' and field != 'sale_line_ids'):
                    field_val = field_val.id
                elif isinstance(field_val, browse_null):
                    field_val = False
                elif (isinstance(field_val, list) or
                        field == 'invoice_line_tax_ids' or field == 'sale_line_ids'):
                    field_val = ((6, 0, tuple([v.id for v in field_val])),)
                list_key.append((field, field_val))
            list_key.sort()
            return tuple(list_key)

        new_invoices = {}
        draft_invoices = [invoice
                          for invoice in self
                          if invoice.state == 'draft']
        seen_origins = {}
        seen_client_refs = {}

        for account_invoice in draft_invoices:
            invoice_key = make_key(
                account_invoice, self._get_invoice_key_cols())
            new_invoice = new_invoices.setdefault(invoice_key, ({}, []))
            new_invoice[1].append(account_invoice.id)
            invoice_infos = new_invoice[0]
            if not invoice_infos:
                invoice_infos.update(
                    self._get_first_invoice_fields(account_invoice))

            for invoice_line in account_invoice.invoice_line_ids:
                cols = self._get_invoice_line_key_cols()
                line_key = make_key(
                    invoice_line, cols)
                o_line = invoice_infos['invoice_line_ids'].setdefault(line_key,{})
                if o_line:
                    o_line['quantity'] += invoice_line.quantity
                else:
                    o_line['quantity'] = invoice_line.quantity

        allinvoices = []
        allnewinvoices = []
        invoices_info = {}
        qty_prec = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')
        for invoice_key, (invoice_data, old_ids) in new_invoices.iteritems():
            if len(old_ids) < 2:
                allinvoices += (old_ids or [])
                continue
            for key, value in invoice_data['invoice_line_ids'].iteritems():
                value.update(dict(key))
            if remove_empty_invoice_lines:
                invoice_data['invoice_line_ids'] = [
                    (0, 0, value) for value in
                    invoice_data['invoice_line_ids'].itervalues() if
                    not float_is_zero(
                        value['quantity'], precision_digits=qty_prec)]
            else:
                invoice_data['invoice_line_ids'] = [
                    (0, 0, value) for value in
                    invoice_data['invoice_line_ids'].itervalues()]

            newinvoice = self.with_context(is_merge=True).create(invoice_data)
            invoices_info.update({newinvoice.id: old_ids})
            allinvoices.append(newinvoice.id)
            allnewinvoices.append(newinvoice)

            for old_id in old_ids:
                old_invoice_id = self.sudo().browse(old_id)
                old_invoice_id.sudo().action_invoice_cancel() 

        for new_invoice in allnewinvoices:
            new_invoice.compute_taxes()
        return invoices_info
