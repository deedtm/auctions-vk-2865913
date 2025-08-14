from dataclasses import dataclass
from functools import cached_property
from random import randint
from typing import Optional

from ...enums.payments import PaymentStatus
from ..token import generate_token


@dataclass
class PaymentInit:
    terminal_key: str
    amount: int
    password: str
    description: Optional[str] = None
    customer_key: Optional[str] = None
    reccurent: Optional[bool] = None
    pay_type: Optional[str] = None
    language: Optional[str] = None
    notification_url: Optional[str] = None
    success_url: Optional[str] = None
    fail_url: Optional[str] = None
    redirect_due_date: Optional[str] = None
    data: Optional[dict] = None
    receipt: Optional[dict] = None
    shops: Optional[list] = None
    descriptor: Optional[str] = None

    @cached_property
    def order_id(self):
        oid = str(randint(1, 10**35))
        return oid

    @cached_property
    def token(self):
        token = generate_token(self, self.password)
        return token

    def to_dict(self):
        d = {
            "TerminalKey": self.terminal_key,
            "Amount": self.amount,
            "OrderId": self.order_id,
            "Token": self.token,
            "Description": self.description,
            "CustomerKey": self.customer_key,
            "Reccurent": self.reccurent,
            "PayType": self.pay_type,
            "Language": self.language,
            "NotificationURL": self.notification_url,
            "SuccessURL": self.success_url,
            "FailURL": self.fail_url,
            "RedirectDueDate": self.redirect_due_date,
            "DATA": self.data,
            "Receipt": self.receipt,
            "Shops": self.shops,
            "Descriptor": self.descriptor,
        }
        return {k: v for k, v in d.items() if v}

    def copy(self):
        return PaymentInit(
            terminal_key=self.terminal_key,
            amount=self.amount,
            password=self.password,
            description=self.description,
            customer_key=self.customer_key,
            reccurent=self.reccurent,
            pay_type=self.pay_type,
            language=self.language,
            notification_url=self.notification_url,
            success_url=self.success_url,
            fail_url=self.fail_url,
            redirect_due_date=self.redirect_due_date,
            data=self.data,
            receipt=self.receipt,
            shops=self.shops,
            descriptor=self.descriptor,
        )


@dataclass(frozen=True)
class PaymentInitResponse:
    terminal_key: str
    amount: int
    order_id: str
    success: bool
    status: PaymentStatus
    payment_id: str
    error_code: str
    payment_url: Optional[str] = None
    message: Optional[str] = None
    details: Optional[str] = None

    def from_dict(cls, data: dict):
        status_data = data.get("Status")
        status = PaymentStatus[status_data] if status_data else None
        return cls(
            success=data.get("Success"),
            error_code=data.get("ErrorCode"),
            terminal_key=data.get("TerminalKey"),
            status=status,
            payment_id=data.get("PaymentId"),
            order_id=data.get("OrderId"),
            amount=data.get("Amount"),
            payment_url=data.get("PaymentURL"),
            message=data.get("Message"),
            details=data.get("Details"),
        )
