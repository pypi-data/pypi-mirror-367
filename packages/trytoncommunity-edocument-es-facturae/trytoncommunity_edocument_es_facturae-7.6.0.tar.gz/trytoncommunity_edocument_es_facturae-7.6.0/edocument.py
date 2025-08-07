# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import os
from decimal import Decimal

import genshi
import genshi.template
# XXX fix: https://genshi.edgewall.org/ticket/582
from genshi.template.astutil import ASTCodeGenerator, ASTTransformer
from lxml import etree
from signxml import DigestAlgorithm
from signxml.xades import (
    XAdESDataObjectFormat, XAdESSignaturePolicy, XAdESSigner)

from trytond.model import Model
from trytond.pool import Pool
from trytond.rpc import RPC
from trytond.tools import cached_property
from trytond.transaction import Transaction

if not hasattr(ASTCodeGenerator, 'visit_NameConstant'):
    def visit_NameConstant(self, node):
        if node.value is None:
            self._write('None')
        elif node.value is True:
            self._write('True')
        elif node.value is False:
            self._write('False')
        else:
            raise Exception("Unknown NameConstant %r" % (node.value,))
    ASTCodeGenerator.visit_NameConstant = visit_NameConstant
if not hasattr(ASTTransformer, 'visit_NameConstant'):
    # Re-use visit_Name because _clone is deleted
    ASTTransformer.visit_NameConstant = ASTTransformer.visit_Name

loader = genshi.template.TemplateLoader(
    os.path.join(os.path.dirname(__file__), 'template'),
    auto_reload=True)


def remove_comment(stream):
    for kind, data, pos in stream:
        if kind is genshi.core.COMMENT:
            continue
        yield kind, data, pos


def strip_spaces(str):
    return ''.join(str.split(' '))


class Invoice(Model):
    "EDocument Spanish Facturae Invoice"
    __name__ = 'edocument.es.facturae.invoice'
    __no_slots__ = True  # to work with cached_property

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls.__rpc__.update({
                'render': RPC(instantiate=0),
                })

    def __init__(self, invoice):
        pool = Pool()
        Invoice = pool.get('account.invoice')
        Lang = pool.get('ir.lang')
        lang = None
        if int(invoice) >= 0:
            invoice = Invoice(int(invoice))
            lang = invoice.party_lang
            with Transaction().set_context(language=invoice.party_lang):
                self.invoice = invoice.__class__(int(invoice))
        else:
            self.invoice = invoice
        self.lang = Lang.get(lang)

    def render(self, version):
        if self.invoice.state not in {'posted', 'paid'}:
            raise ValueError("Invoice must be posted")
        tmpl = self._get_template(version)
        if not tmpl:
            raise NotImplementedError
        content = (tmpl.generate(
            this=self, Decimal=Decimal, strip_spaces=strip_spaces)
            .filter(remove_comment)
            .render().encode('utf-8'))
        key = self.invoice.company.es_facturae_private_key
        cert = self.invoice.company.es_facturae_certificate
        if key and cert:
            signer = XAdESSigner(**self._get_xades_signature_options(version))
            signed = signer.sign(etree.fromstring(content), cert=cert, key=key)
            return etree.tostring(
                signed, xml_declaration=True, encoding='UTF-8')
        return content

    def _get_xades_signature_options(self, version):

        signature_policy = XAdESSignaturePolicy(
            Identifier=('http://www.facturae.es/politica_de_firma_'
                'formato_facturae/politica_de_firma_formato_facturae'
                '_v3_1.pdf'),
            Description=("Política de firma electrónica para facturación "
                "electrónica con formato Facturae"),
            DigestMethod=DigestAlgorithm.SHA1,
            DigestValue='Ohixl6upD6av8N7pEvDABhEL6hM=',
        )
        c14n_algorithm = 'http://www.w3.org/TR/2001/REC-xml-c14n-20010315'
        role = 'emisor' if self.invoice.type == 'out' else 'receptor'
        return {
            'signature_policy': signature_policy,
            'claimed_roles': [role],
            'data_object_format': XAdESDataObjectFormat(
                Description="Factura electrónica",
                MimeType="text/xml",
                ),
            'c14n_algorithm': c14n_algorithm,
            }

    def _get_template(self, version):
        return loader.load(os.path.join(version, 'Facturae.xml'))

    def format_date(self, date, format=None):
        return self.lang.strftime(date, format=format)

    @cached_property
    def batch_identifier(self):
        parts = []
        if self.seller_tax_identifier:
            parts.append(self.seller_tax_identifier.es_code())
        parts.append(self.invoice.number)
        return ''.join(parts)

    @cached_property
    def lines(self):
        return [l for l in self.invoice.lines if l.type == 'line']

    @cached_property
    def seller_party(self):
        if self.invoice.type == 'out':
            return self.invoice.company.party
        else:
            return self.invoice.party

    @cached_property
    def seller_address(self):
        if self.invoice.type == 'out':
            return self.invoice.company.party.address_get('invoice')
        else:
            return self.invoice.invoice_address

    @cached_property
    def seller_tax_identifier(self):
        if self.invoice.type == 'out':
            return self.invoice.tax_identifier
        else:
            return self.invoice.party_tax_identifier

    @cached_property
    def seller_administrative_centers(self):
        if self.invoice.type == 'out':
            return (
                self.invoice.company.party.es_facturae_administrative_centers)
        else:
            return self.invoice.es_facturae_administrative_centers

    @cached_property
    def buyer_party(self):
        if self.invoice.type == 'out':
            return self.invoice.party
        else:
            return self.invoice.company.party

    @cached_property
    def buyer_address(self):
        if self.invoice.type == 'out':
            return self.invoice.invoice_address
        else:
            return self.invoice.company.party.address_get('invoice')

    @cached_property
    def buyer_tax_identifier(self):
        if self.invoice.type == 'out':
            return self.invoice.party_tax_identifier
        else:
            return self.invoice.tax_identifier

    @cached_property
    def buyer_administrative_centers(self):
        if self.invoice.type == 'out':
            return self.invoice.es_facturae_administrative_centers
        else:
            return (
                self.invoice.company.party.es_facturae_administrative_centers)

    @cached_property
    def invoice_number(self):
        return self.invoice.number

    @cached_property
    def invoice_series_code(self):
        return ''

    @cached_property
    def invoice_document_type(self):
        return 'FC'

    @cached_property
    def invoice_class(self):
        if self.invoice.es_facturae_corrective_invoices:
            return 'OR'
        return 'OO'

    @cached_property
    def operation_date(self):
        pass

    @cached_property
    def invoicing_start_date(self):
        pass

    @cached_property
    def invoicing_end_date(self):
        pass

    @cached_property
    def invoice_description(self):
        return self.invoice.description

    @cached_property
    def additional_information(self):
        return self.invoice.comment

    @cached_property
    def payment_means(self):
        if self.invoice and self.invoice.payment_term:
            return self.invoice.payment_term.es_facturae_type

    @cached_property
    def account_to_be_credited(self):
        # Account only required for 04 payment means
        if self.payment_means != '04':
            return
        if self.invoice.type == 'out':
            party = self.invoice.company.party
        else:
            party = self.invoice.party
        for account in getattr(party, 'bank_accounts', []):
            if account.iban:
                return account.iban
        return ''

    def item_description(self, line):
        parts = []
        if line.product:
            parts.append(line.product.rec_name)
        if line.description:
            parts.extend(line.description.split('\n'))
        if not parts:
            parts.append(line.account.rec_name)
        return '\n'.join(parts)

    def item_start_period(self, line):
        pass

    def item_end_period(self, line):
        pass

    def item_file_reference(self, line):
        pass
