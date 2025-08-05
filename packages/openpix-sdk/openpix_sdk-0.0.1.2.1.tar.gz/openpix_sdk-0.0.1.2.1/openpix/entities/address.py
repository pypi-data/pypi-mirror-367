from . import Entity


class Address(Entity):
    zipcode: str
    street: str
    number: str
    neighborhood: str
    city: str
    state: str
    complement: str
    country: str