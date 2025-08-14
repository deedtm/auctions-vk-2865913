from dataclasses import dataclass
from typing import Literal, Optional

from ...enums.payments import (GetStateParamsKeys, GetStateParamsValues,
                               PaymentStatus)
from ..token import generate_token


@dataclass
class GetState:
    terminal_key: str
    payment_id: str
    password: str
    ip: Optional[str] = None

    @property
    def token(self) -> str:
        return generate_token(self, self.password)

    def to_dict(self) -> dict:
        return {
            "TerminalKey": self.terminal_key,
            "PaymentId": self.payment_id,
            "Token": self.token,
            "IP": self.ip,
        }


@dataclass(frozen=True)
class GetStateResponseParams:
    key: GetStateParamsKeys
    value: GetStateParamsValues

    def from_dict(cls, data: dict) -> "GetStateResponseParams":
        return cls(
            key=GetStateParamsKeys(data["Key"]),
            value=GetStateParamsValues(data["Value"]),
        )


@dataclass(frozen=True)
class GetStateResponse:
    terminal_key: str
    amount: int
    order_id: str
    success: bool
    status: PaymentStatus
    payment_id: str
    error_code: str
    message: Optional[str] = None
    details: Optional[str] = None
    params: Optional[list[GetStateResponseParams]] = None

    def from_dict(cls, data: dict) -> "GetStateResponse":
        params = []
        for item in data.get("Params", []):
            p = GetStateResponseParams.from_dict(GetStateResponseParams, item)
            params.append(p)

        return cls(
            terminal_key=data.get("TerminalKey", ""),
            amount=data.get("Amount", 0),
            order_id=data.get("OrderId", ""),
            success=data.get("Success", False),
            status=PaymentStatus(data.get("Status", "")),
            payment_id=data.get("PaymentId", ""),
            error_code=data.get("ErrorCode", ""),
            message=data.get("Message"),
            details=data.get("Details"),
            params=params if params else None,
        )
