from typing import Optional

from vkbottle.bot import Message

from config.t_api import *
from database.payments.utils import add_payment_from_response
from t_api.types.payments import *
from t_api.utils import *
from templates import ERRORS
from templates import PAY as PAY_TMPL

from ..keyboards.pay import update_kb
from ..states_groups.pay import PaySG
from ..types import MessageEvent, labeler
from .config import SECRET_KEY, TERMINAL_KEY, state_dispenser


async def pay_input_handler(e: Message | MessageEvent, **payload):
    if isinstance(e, Message):
        method = e.answer if isinstance(e, Message) else e.edit_message
        peer_id = e.peer_id
    elif isinstance(e, MessageEvent):
        method = e.edit_message
        peer_id = e.object.peer_id
    else:
        raise TypeError("'e' must be Message or MessageEvent object")

    text = PAY_TMPL["input"]
    await method(text)
    await state_dispenser.set(peer_id, PaySG.PAY, **payload)


@labeler.message(state=PaySG.PAY)
async def pay_link_handler(msg: Message):
    pl = msg.state_peer.payload
    money = pl.get("money")

    if not msg.text.isdigit() and not money:
        text = ERRORS["not_int"]
        await msg.answer(text)
        return

    if not money:
        money = int(msg.text)

    template = PAY_TMPL["link"]

    # payment_data = {"user_id": msg.from_id}
    payment = await create_payment(
        TERMINAL_KEY,
        money,
        SECRET_KEY,
        description=DESCRIPTION,
        notification_url=NOTIFICATION_URL,
        success_url=SUCCESS_URL,
        fail_url=FAIL_URL,
        redirect_due_date=REDIRECT_DUE_DATE,
        # data=payment_data,
    )

    if not payment.success:
        text = PAY_TMPL["error"].format(
            money, payment.error_code, payment.message, payment.details
        )
        await msg.answer(text)
        return

    text = template.format(money, payment.payment_url, "-")
    await msg.answer(text, keyboard=update_kb)

    pl["payment"] = payment
    await state_dispenser.set(msg.peer_id, PaySG.EMPTY, **pl)


@labeler.callback_query({"pay": "update"})
async def pay_update_handler(e: MessageEvent):
    o = e.object
    state_peer = await state_dispenser.get(o.peer_id)

    if not state_peer:
        text = ERRORS["failed_get_data"]
        await e.edit_message(text, keyboard=None)
        return

    pl = state_peer.payload

    payment = pl["payment"]
    payment_state = await get_payment_state(payment, SECRET_KEY)
    pl["payment_state"] = payment_state
    status = payment_state.status

    template = PAY_TMPL["link"]
    text = template.format(
        payment_state.amount // 100, payment.payment_url, status.value
    )

    is_end = status in status.end_statuses

    kb = update_kb
    if is_end:
        kb = None
        lots_ids = [lot.id for lot in pl["lots"]] if "lots" in pl else None
        await add_payment_from_response(
            o.user_id, payment_state, lots_ids
        )
        await pl.get(f"on_{status.value.lower()}", pay_final)(e, pl)

    await e.edit_message(text=text, keyboard=kb)


async def pay_final(e: MessageEvent, payload: dict = None):
    payment: PaymentInitResponse = payload["payment"]
    payment_state: GetStateResponse = payload["payment_state"]
    template = PAY_TMPL[payment_state.status.value.lower()]
    text = template.format(payment.amount // 100)
    await e.answer(text)
