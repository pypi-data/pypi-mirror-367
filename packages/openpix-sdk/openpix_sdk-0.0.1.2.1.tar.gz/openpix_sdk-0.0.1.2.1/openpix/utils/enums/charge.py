from enum import Enum


class ChargeType(str, Enum):
    DYNAMIC = "DYNAMIC"
    OVERDUE = "OVERDUE"