from . import Entity

from openpix.utils.enums import SplitType


class Split(Entity):
    value: int
    pixKey: str
    splitType: SplitType