from typing import Self

from pydantic import model_validator

from . import Entity, TaxID, Address


class Customer(Entity):
    name: str
    email: str = None
    phone: str = None
    taxID: TaxID = None
    correlationID: str = None
    address: Address = None

    @model_validator(mode="after")
    def check_data_integrity(self) -> Self:
        if not(self.email or self.phone or self.taxID):
            raise "The customer needs to have at least a email or phone or taxID"
        return self