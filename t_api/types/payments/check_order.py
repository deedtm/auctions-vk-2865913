from dataclasses import dataclass
from typing import Optional

from ...enums.payments import PaymentStatus
from ..token import generate_token


@dataclass
class CheckOrder:
    terminal_key: str
    order_id: str
    password: str

    @property
    def token(self) -> str:
        return generate_token(self, self.password)

    def to_dict(self) -> dict:
        return {
            "TerminalKey": self.terminal_key,
            "OrderId": self.order_id,
            "Token": self.token,
        }


@dataclass(frozen=True)
class CheckOrderPayment:
    payment_id: str
    status: PaymentStatus
    success: bool
    amount: Optional[int] = None
    rrn: Optional[str] = None
    error_code: Optional[int] = None
    message: Optional[str] = None
    sbp_payment_id: Optional[str] = None
    sbp_customer_id: Optional[str] = None

    def from_dict(cls, data: dict) -> "CheckOrderPayment":
        return cls(
            payment_id=data.get("PaymentId", ""),
            status=PaymentStatus(data.get("Status", "")),
            success=data.get("Success", False),
            amount=data.get("Amount"),
            rrn=data.get("RRN"),
            error_code=data.get("ErrorCode"),
            message=data.get("Message"),
            sbp_payment_id=data.get("SbpPaymentId"),
            sbp_customer_id=data.get("SbpCustomerId"),
        )


@dataclass(frozen=True)
class CheckOrderResponse:
    terminal_key: str
    order_id: str
    success: bool
    error_code: str
    message: Optional[str] = None
    details: Optional[str] = None
    payments: Optional[list[CheckOrderPayment]] = None

    def from_dict(cls, data: dict) -> "CheckOrderResponse":
        payments = []
        for item in data.get("Payments", []):
            p = CheckOrderPayment.from_dict(item)
            payments.append(p)

        return cls(
            terminal_key=data.get("TerminalKey", ""),
            order_id=data.get("OrderId", ""),
            success=data.get("Success", False),
            error_code=data.get("ErrorCode", ""),
            message=data.get("Message"),
            details=data.get("Details"),
            payments=payments if payments else None,
        )
