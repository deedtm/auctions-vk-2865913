from datetime import datetime

from vkbottle.bot import Message

from config.time import DATETIME_FORMAT as DTFMT
from config.time import TZ
from database.groups.utils import get_group
from database.lots.models import Lot
from database.lots.utils import get_lot
from database.payments.models import Payment
from database.payments.utils import get_payments_by_user_id
from database.users.utils import get_user, update_user_data
from enums.balance import HistoryEmojis
from templates import COMMANDS

from ...hyperlinks import group_post_hl
from ...keyboards.balance import main_menu_kb
from ...types import MessageEvent, labeler
from ..config import state_dispenser
from ..pay import pay_input_handler
from ..rules import CommandFilter
from .__utils import get_command

__literals = get_command("balance")["literals"]


@labeler.message(CommandFilter(__literals))
async def balance_handler(msg: Message):
    template = COMMANDS["balance"]["main"]
    user = await get_user(msg.from_id)

    if user.loyal:
        loyal_date = datetime.fromtimestamp(int(user.loyal), tz=TZ).strftime(DTFMT)
    else:
        loyal_date = "—"

    text = template.format(user.balance, loyal_date)
    await msg.answer(text, keyboard=main_menu_kb)


@labeler.callback_query({"balance": "top_up"})
async def top_up_handler(e: MessageEvent):
    await pay_input_handler(e, on_confirmed=topped_up)


async def topped_up(e: MessageEvent, payload: dict = None):
    money = payload["payment"].amount // 100
    user = await get_user(e.object.user_id)
    await update_user_data(user.user_id, balance=user.balance + money)

    text = COMMANDS["balance"]["success_payment"]
    await e.answer(text)
    await state_dispenser.delete(e.object.peer_id)


async def get_lot_text(id: int):
    payment_lots_fmt = COMMANDS["balance"]["history_payment_lots_format"]
    lot = await get_lot(id)
    group = await get_group(lot.group_id)
    if lot.last_bet:
        commission = max(
            lot.last_bet * group.commission_percent // 100, group.commission_min
        )
    else:
        commission = "?"
    hl = group_post_hl(lot.group_id, lot.post_id, lot.description)
    return payment_lots_fmt.format(hl, commission)


async def get_payment_text(payment: Payment):
    payment_fmt = COMMANDS["balance"]["history_payment_format"]

    emoji = HistoryEmojis[payment.status].value
    if payment.lots_ids:
        ids = payment.lots_ids.split(",")
        lots_text = [await get_lot_text(id) for id in ids]
        reason = f"оплата комиссии\n" + "\n".join(lots_text)
    else:
        reason = "пополнение баланса"

    return payment_fmt.format(emoji, payment.amount // 100, reason)


@labeler.callback_query({"balance": "history"})
async def history_handler(e: MessageEvent):
    payments = await get_payments_by_user_id(e.object.user_id)
    if not payments:
        await e.edit_message(COMMANDS["balance"]["no_history"])

    text = "\n\n".join([await get_payment_text(p) for p in payments])
    await e.edit_message(text)

    if HistoryEmojis.NEW.value in text or HistoryEmojis.REJECTED.value in text:
        await e.answer(COMMANDS["balance"]["history_note"])
