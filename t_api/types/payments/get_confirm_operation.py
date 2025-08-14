from dataclasses import dataclass
from typing import Optional

from ..token import generate_token

FF = lambda item: item[0] in ["terminal_key"]


@dataclass
class GetConfirmOperationURL:
    terminal_key: str
    callback_url: str
    payment_id_list: list[int]
    password: str

    @property
    def token(self) -> str:
        return generate_token(self, self.password, FF)

    def to_dict(self) -> dict:
        return {
            "TerminalKey": self.terminal_key,
            "CallbackURL": self.callback_url,
            "PaymentIdList": self.payment_id_list,
            "Token": self.token,
        }


@dataclass
class GetConfirmOperationEmail:
    terminal_key: str
    payment_id_list: list[int]
    email_list: list[str]
    token: str

    @property
    def token(self) -> str:
        return generate_token(self, self.token, FF)

    def to_dict(self) -> dict:
        return {
            "TerminalKey": self.terminal_key,
            "PaymentIdList": self.payment_id_list,
            "EmailList": self.email_list,
            "Token": self.token,
        }


@dataclass(frozen=True)
class GetConfirmOperationPayment:
    success: bool
    error_code: str
    message: str
    payment_id: int

    def from_dict(cls, data: dict) -> "GetConfirmOperationPayment":
        return cls(
            success=data.get("Success", False),
            error_code=data.get("ErrorCode", ""),
            message=data.get("Message", ""),
            payment_id=data.get("PaymentId", 0),
        )


@dataclass(frozen=True)
class GetConfirmOperationResponse:
    success: bool
    error_code: str
    payment_id_list: list[GetConfirmOperationPayment]
    message: Optional[str] = None

    def from_dict(cls, data: dict):
        payment_ids = []
        for payment in data["PaymentIdList"]:
            payment_ids.append(GetConfirmOperationPayment.from_dict(payment))

        return cls(
            success=data.get("Success", False),
            error_code=data.get("ErrorCode", ""),
            payment_id_list=payment_ids,
            message=data.get("Message"),
        )
        