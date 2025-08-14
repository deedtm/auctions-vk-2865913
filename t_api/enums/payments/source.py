from enum import Enum


class PaymentSource(Enum):
    CARDS = "cards"
    BEELINE = "beeline"
    MTS = "mts"
    TELE2 = "tele2"
    MEGAFON = "megafon"
    EINVOICING = "einvoicing"
    WEBMONEY = "webmoney"
    