from . import Entity
from openpix.utils.enums import TaxIDType


class TaxID(Entity):
    taxID: str
    type: TaxIDType