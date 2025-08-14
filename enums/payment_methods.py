from enum import Enum


class PaymentMethod(Enum):
    LINK = "link"
    BALANCE = "balance"
    LOYAL = "loyal"


class PaymentMethodUser(Enum):
    LINK = "по ссылке"
    BALANCE = "с баланса"
    LOYAL = "бесплатно засчет абонемента"
    