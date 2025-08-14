from typing import Optional

from sqlalchemy import Boolean, Column, Integer, Text

from enums.payment_methods import PaymentMethod
from t_api.types.payments import GetStateResponse

from ..connect import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    lots_ids = Column(Text, nullable=True)
    amount = Column(Integer, nullable=False)
    order_id = Column(Text, nullable=False)
    success = Column(Boolean, nullable=False)
    status = Column(Text, nullable=False)
    payment_id = Column(Text, nullable=False)
    error_code = Column(Text, nullable=False)
    message = Column(Text, nullable=True)
    details = Column(Text, nullable=True)

    @staticmethod
    def from_get_state_response(
        user_id: int,
        response: GetStateResponse,
        lots_ids: Optional[list[int]] = None,
    ):
        if lots_ids:
            lots_ids = ",".join(map(str, lots_ids))
        payment = Payment(
            user_id=user_id,
            lots_ids=lots_ids,
            amount=response.amount,
            order_id=response.order_id,
            success=response.success,
            status=response.status.value,
            payment_id=response.payment_id,
            error_code=response.error_code,
            message=response.message,
            details=response.details
        )
        return payment
