from enum import Enum


class TaxIDType(str, Enum):
    CPF = "BR:CPF"
    CNPJ = "BR:CNPJ"