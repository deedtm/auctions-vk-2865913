from enum import Enum


class GetStateParamsKeys(Enum):
    ROUTE = "Route"
    SOURCE = "Source"
    CREDIT_AMOUNT = "CreditAmount"
    

class GetStateParamsValues(Enum):
    ACQ = "ACQ"
    BNPL = "BNPL"
    TCB = "TCB"
    SBER = "SBER"
    CARDS = "cards"
    INSTALLMENT = "Installment"
    MIRPAY = "MirPay"
    QRSBP = "qrsbp"
    SBERPAY = "SberPay"
    TINKOFFPAY = "TinkoffPay"
    YANDEXPAY = "YandexPay"
    