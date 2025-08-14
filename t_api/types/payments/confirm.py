from dataclasses import dataclass
from functools import cached_property
from typing import Optional

from ...enums.payments import PaymentRoute, PaymentSource, PaymentStatus
from ..token import generate_token


@dataclass
class FinishAuthorize:
    terminal_key: str
    payment_id: str
    password: str
    card_data: str
    ip: Optional[str] = None
    send_email: Optional[bool] = None
    source: Optional[PaymentSource] = None
    data: Optional[dict] = None
    info_email: Optional[str] = None
    encrypted_payment_data: Optional[str] = None
    amount: Optional[int] = None
    device_channel: Optional[str] = None
    route: Optional[PaymentRoute] = None

    @cached_property
    def token(self):
        return generate_token(self, self.password)

    def to_dict(self):
        d = {
            "TerminalKey": self.terminal_key,
            "PaymentId": self.payment_id,
            "Password": self.password,
            "CardData": self.card_data,
            "IP": self.ip,
            "SendEmail": self.send_email,
            "Source": self.source,
            "Data": self.data,
            "InfoEmail": self.info_email,
            "EncryptedPaymentData": self.encrypted_payment_data,
            "Amount": self.amount,
            "DeviceChannel": self.device_channel,
            "Route": self.route,
            "Token": self.token,
        }
        return {k: v for k, v in d.items() if v}


@dataclass(frozen=True)
class FinishAuthorizeResponse:
    terminal_key: str
    amount: int
    order_id: str
    success: bool
    status: PaymentStatus
    error_code: str
    payment_id: Optional[str] = None
    message: Optional[str] = None
    details: Optional[str] = None
    rebill_id: Optional[str] = None
    card_id: Optional[str] = None

    def from_dict(cls, data: dict):
        return cls(
            terminal_key=data.get("TerminalKey", ""),
            amount=data.get("Amount", 0),
            order_id=data.get("OrderId", ""),
            success=data.get("Success", False),
            status=PaymentStatus(data.get("Status", "")),
            error_code=data.get("ErrorCode", ""),
            payment_id=data.get("PaymentId"),
            message=data.get("Message"),
            details=data.get("Details"),
            rebill_id=data.get("RebillId"),
            card_id=data.get("CardId"),
        )


@dataclass(frozen=True)
class FinishAuthorizeResponse3DS(FinishAuthorizeResponse):
    md: Optional[str] = None
    pa_req: Optional[str] = None
    acs_url: Optional[str] = None

    def from_dict(cls, data: dict):
        return cls(
            md=data.get("MD"),
            pa_req=data.get("PaReq"),
            acs_url=data.get("AcsUrl"),
            **FinishAuthorizeResponse.from_dict(data)
        )


@dataclass(frozen=True)
class FinishAuthorizeResponse3DSv2APP(FinishAuthorizeResponse):
    tds_server_trans_id: str = ""
    acs_trans_id: str = ""
    acs_reference_number: str = ""
    sdk_trans_id: str = ""
    acs_interface: Optional[str] = None
    acs_ui_template: Optional[str] = None
    acs_signed_content: Optional[str] = None

    def from_dict(cls, data: dict):
        return cls(
            tds_server_trans_id=data.get("TdsServerTransId", ""),
            acs_trans_id=data.get("AcsTransId", ""),
            acs_reference_number=data.get("AcsReferenceNumber", ""),
            sdk_trans_id=data.get("SdkTransId", ""),
            acs_interface=data.get("AcsInterface"),
            acs_ui_template=data.get("AcsUiTemplate"),
            acs_signed_content=data.get("AcsSignedContent"),
            **FinishAuthorizeResponse.from_dict(data)
        )


@dataclass(frozen=True)
class FinishAuthorizeResponse3DSv2WEB(FinishAuthorizeResponse):
    tds_server_trans_id: str = ""
    acs_trans_id: str = ""
    acs_url: Optional[str] = None

    def from_dict(cls, data: dict):
        return cls(
            tds_server_trans_id=data.get("TdsServerTransId", ""),
            acs_trans_id=data.get("AcsTransId", ""),
            acs_url=data.get("AcsUrl"),
            **FinishAuthorizeResponse.from_dict(data)
        )
