# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import ModelSQL, ModelView, fields
from trytond.pool import PoolMeta


class AdministrativeCenter(ModelSQL, ModelView):
    "Facturae Administrative Center"
    __name__ = 'edocument.es_facturae.administrative_center'

    party = fields.Many2One(
        'party.party', "Party", required=True, ondelete='CASCADE')
    role = fields.Selection([
        ('01', "Fiscal"),
        ('02', "Receiver"),
        ('03', "Payer"),
        ('04', "Buyer"),
        ('05', "Collector"),
        ('06', "Seller"),
        ('07', "Payment receiver"),
        ('08', "Collection receiver"),
        ('09', "Issuer"),
        ], "Role", required=True)
    address = fields.Many2One(
        'party.address', "Address", required=True, ondelete='CASCADE')
    description = fields.Char("Description")


class Party(metaclass=PoolMeta):
    __name__ = 'party.party'

    es_facturae_administrative_centers = fields.One2Many(
        'edocument.es_facturae.administrative_center', 'party',
        "Facturae Administrative Centers")


class Address(metaclass=PoolMeta):
    __name__ = 'party.address'

    es_facturae_center_code = fields.Char("Facturae Center Code")


class Identifier(metaclass=PoolMeta):
    __name__ = 'party.identifier'

    def facturae_person_type_code(self):
        if self.type in {'es_dni', 'es_nie'}:
            return 'F'
        return 'J'

    def facturae_residence_type_code(self):
        if self.type.startswith('es_'):
            return 'R'
        if self.type.startswith('eu_'):
            if self.code.upper().startswith('ES'):
                return 'R'
            return 'U'
        return 'E'
