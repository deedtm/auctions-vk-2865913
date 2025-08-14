from enum import Enum


class PaymentRoute(Enum):
    ACQ = "ACQ"
    MC = "MC"
    EINV = "EINV"
    WM = "WM"

    