from dataclasses import dataclass
from typing import Literal, Optional


@dataclass
class ReceiptItem:
    name: str
    price: int
    quantity: int
    tax: Literal[
        "none",
        "vat0",
        "vat5",
        "vat7",
        "vat10",
        "vat20",
        "vat105",
        "vat107",
        "vat110",
        "vat120",
    ]
    payment_method: Optional[
        Literal[
            "full_prepayment",
            "prepayment",
            "advance",
            "full_payment",
            "partial_payment",
            "credit",
            "credit_payment",
        ]
    ] = None
    payment_object: Optional[
        Literal[
            "commodity",
            "excise",
            "job",
            "service",
            "gambling_bet",
            "gambling_prize",
            "lottery",
            "lottery_prize",
            "intellectual_activity",
            "payment",
            "agent_commission",
            "composite",
            "another",
        ]
    ] = None
    ean13: Optional[str] = None
    shop_code: Optional[str] = None
    agent_data: Optional[dict] = None
    supplier_info: Optional[str] = None

    @property
    def amount(self) -> int:
        return self.price * self.quantity

    def to_dict(self):
        d = {
            "Name": self.name,
            "Price": self.price,
            "Quantity": self.quantity,
            "Amount": self.amount,
            "Tax": self.tax,
            "PaymentMethod": self.payment_method,
            "PaymentObject": self.payment_object,
            "EAN13": self.ean13,
            "ShopCode": self.shop_code,
            "AgentData": self.agent_data,
            "SupplierInfo": self.supplier_info,
        }
        return {k: v for k, v in d.items() if v}


@dataclass
class ReceiptFFD105:
    items: list[ReceiptItem]
    taxation: Literal["osn", "usn_income", "usn_income_outcome", "esn", "patent"]
    ffdversion: str = "1.05"
    email: Optional[str] = None
    phone: Optional[str] = None
    payments: Optional[dict] = None
    shops: Optional[list[dict]] = None
    descriptor: Optional[str] = None

    def to_dict(self):
        d = {
            "Items": [item.to_dict() for item in self.items],
            "Taxation": self.taxation,
            "Email": self.email,
            "Phone": self.phone,
            "Payments": self.payments,
            "Shops": self.shops,
            "Descriptor": self.descriptor,
            "FFDVersion": self.ffdversion,
        }
        return {k: v for k, v in d.items() if v}
