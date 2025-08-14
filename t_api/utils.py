from typing import Optional
from .types.payments import *
from .types.threeds import *
from .methods.payments import *
from .methods.threeds import *


async def create_payment(
    terminal_key: str,
    amount: int,
    password: str,
    description: Optional[str] = None,
    language: Optional[str] = None,
    notification_url: Optional[str] = None,
    success_url: Optional[str] = None,
    fail_url: Optional[str] = None,
    redirect_due_date: Optional[str] = None,
    data: Optional[dict] = None,
):
    # data = data or {}
    # if not "OperationInitiatorType" in data:
    #     data["OperationInitiatorType"] = "0"

    payment_init = PaymentInit(
        terminal_key=terminal_key,
        amount=amount * 100,
        password=password,
        description=description,
        language=language,
        notification_url=notification_url,
        success_url=success_url,
        fail_url=fail_url,
        redirect_due_date=redirect_due_date,
        data=data
    )
    res = await init(payment_init)

    return res


async def get_payment_state(
    payment: PaymentInitResponse,
    password: str,
    ip: Optional[str] = None,
):
    get_state_obj = GetState(
        terminal_key=payment.terminal_key,
        payment_id=payment.payment_id,
        password=password,
        ip=ip,
    )
    res = await get_state(get_state_obj)

    return res


async def check_payment_order(payment: PaymentInitResponse, password: str):
    check_order_obj = CheckOrder(
        terminal_key=payment.terminal_key,
        order_id=payment.order_id,
        password=password,
    )
    res = await check_order(check_order_obj)

    return res


async def get_payment_confirm_operation(
    payment: PaymentInitResponse,
    password: str,
    payment_ids: list[int],
    callback_url: Optional[str] = None,
    email_list: Optional[list[str]] = None,
):
    assert (
        callback_url or email_list
    ), "You must provide either callback_url or email_list"
    kwargs = {
        "terminal_key": payment.terminal_key,
        "password": password,
        "payment_ids": payment_ids,
    }
    if callback_url:
        confirm_operation = GetConfirmOperationURL(**kwargs, callback_url=callback_url)
    else:
        confirm_operation = GetConfirmOperationEmail(**kwargs, email_list=email_list)
    res = await get_confirm_operation(confirm_operation)

    return res


__all__ = (
    "create_payment",
    "get_payment_state",
    "check_payment_order",
    "get_payment_confirm_operation",
)
