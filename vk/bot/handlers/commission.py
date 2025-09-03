from datetime import datetime

from vkbottle.bot import Message
from vkbottle.tools.formatting import *

from config.time import TZ
from database.lots.utils import get_lots_with_commissions, update_lot_data
from database.users.utils import get_user, update_user_data
from enums.moderation import LotStatusDB
from templates import COMMANDS

from ...keyboards import COMMISSION as KB_TEXT
from ...keyboards.commission import commission_main_kb
from ...states_groups import CommissionSG
from ...types import MessageEvent, labeler
from ..config import state_dispenser
from ..pay import pay_link_handler
from ..rules import CommandFilter
from .__utils import get_command

__literals = get_command("commission")["literals"]


@labeler.message(CommandFilter(__literals))
async def commission_handler(msg: Message):
    lots = await get_lots_with_commissions(msg.from_id)
    if not lots:
        await msg.answer(COMMANDS["commission"]["no_lots"])
        return

    coms = [lot.commission for lot in lots if lot.commission]
    total_commission = sum(coms)
    lots_text = [
        f"{lot.id}. {lot.description} — {lot.commission} руб."
        for lot in lots
        if lot.commission
    ]

    template = COMMANDS["commission"]["main"]
    text = template.format(total_commission, "\n".join(lots_text))

    await msg.answer(text, keyboard=commission_main_kb)
    await state_dispenser.set(
        msg.peer_id,
        CommissionSG.PAY_CHOICE,
        all_lots=lots,
        commission=total_commission,
    )


@labeler.message(state=CommissionSG.PAY_CHOICE, text=KB_TEXT["pay_all"])
async def pay_handler(msg: Message):
    pl = msg.state_peer.payload
    commission = pl["commission"]
    user = await get_user(user_id=msg.from_id)
    is_loyal_active = user.loyal and datetime.now(TZ).timestamp() < user.loyal

    if user.balance >= commission or is_loyal_active:
        add_rating = False
        if not is_loyal_active:
            await update_user_data(user.user_id, balance=user.balance - commission)
            add_rating = True
        await success_payment(msg, pl, add_rating)
        await state_dispenser.delete(msg.peer_id)
    else:
        pl["on_confirmed"] = success_payment
        pl["money"] = commission
        await pay_link_handler(msg)


async def success_payment(
    e: MessageEvent, payload: dict = None, add_rating: bool = True
):
    text = COMMANDS["commission"]["success_payment"]
    await e.answer(text)

    lots = payload.get("lots", payload.get("all_lots"))
    for l in lots:
        await update_lot_data(l.id, commission=None)

    if add_rating:
        user = await get_user(lots[0].user_id)
        await update_user_data(user.user_id, rating=user.rating + len(lots))


@labeler.message(state=CommissionSG.PAY_CHOICE, text=KB_TEXT["pay_partially"])
async def pay_partially_handler(msg: Message):
    text = COMMANDS["commission"]["lots_choice"]
    await msg.answer(text)
    await state_dispenser.set(
        msg.peer_id, CommissionSG.LOTS_CHOICE, **msg.state_peer.payload
    )


@labeler.message(state=CommissionSG.LOTS_CHOICE)
async def lots_choice_handler(msg: Message):
    lots = msg.state_peer.payload["all_lots"]
    lots_by_ids = {str(lot.id): lot for lot in lots}

    ids = msg.text.split()
    is_ids_valid = True if ids else False
    for id_ in ids:
        if not id_.isdigit() or id_ not in lots_by_ids:
            is_ids_valid = False
            break

    if not is_ids_valid:
        await msg.answer(COMMANDS["commission"]["invalid_ids"])
        return

    choosed_lots = []
    commission = 0
    for id_ in ids:
        l = lots_by_ids[id_]
        choosed_lots.append(l)
        commission += l.commission

    msg.state_peer.payload["commission"] = commission
    msg.state_peer.payload["lots"] = choosed_lots

    await pay_handler(msg)
    