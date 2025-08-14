from dataclasses import dataclass
from functools import cached_property
from typing import Optional

from ..token import generate_token


@dataclass
class ThreeDSCheckVersion:
    payment_id: str
    terminal_key: str
    card_data: str
    password: str

    @cached_property
    def token(self):
        return generate_token(self, self.password)

    def to_dict(self):
        return {
            "PaymentId": self.payment_id,
            "TerminalKey": self.terminal_key,
            "CardData": self.card_data,
            "Token": self.token,
        }


@dataclass(frozen=True)
class ThreeDSCheckVersionResponse:
    version: str
    payment_system: str
    success: bool
    error_code: str
    tds_server_trans_id: Optional[str] = None
    threeds_method_url: Optional[str] = None
    message: Optional[str] = None
    details: Optional[str] = None

    def from_dict(cls, data: dict):
        return cls(
            version=data.get("Version"),
            payment_system=data.get("PaymentSystem"),
            success=data.get("Success"),
            error_code=data.get("ErrorCode"),
            tds_server_trans_id=data.get("TdsServerTransID"),
            threeds_method_url=data.get("ThreeDSMethodURL"),
            message=data.get("Message"),
            details=data.get("Details"),
        )

    def is_3ds_method_required(self):
        return getattr(self, "ThreeDSMethodURL", None) is not None
    