from asyncio import sleep
from datetime import datetime
from time import time

from vkbottle.bot import Message
from vkbottle_types.objects import UsersUserFull

from config.admin import INFO_ACCESS
from config.time import DATETIME_FORMAT
from database.lots.utils import (get_lots_by_user, get_lots_with_commissions,
                                 get_user_win_lots)
from database.payments.utils import get_total_amount_by_user_id
from database.users.utils import get_user
from templates import ADMIN_COMMANDS as ADMIN
from templates import ERRORS

from ....hyperlinks import user_hl
from ....keyboards.swipe import swipe_kb
from ....states_groups import EmptySG
from ....types import MessageEvent, labeler
from ....utils import get_users_from_links
from ...config import state_dispenser
from ...rules import AccessFilter, CommandFilter
from .__utils import get_command, get_required_args, separate_args

# from .utils import command_wrapper

command_data = get_command("check")
LITERALS = command_data["literals"]
REQUIRED_ARGS = get_required_args(command_data)


async def user_text(user: UsersUserFull) -> str:
    u = user
    dbu = await get_user(u.id)
    lots = await get_lots_by_user(u.id)
    commission_lots = await get_lots_with_commissions(u.id)
    wins = await get_user_win_lots(u.id)
    spent = await get_total_amount_by_user_id(u.id)
    spent //= 100

    full_name = user_hl(u.id, f"{u.first_name} {u.last_name}")

    access_level = getattr(dbu, "access_level", ADMIN["check"]["no_info"])
    register_date = getattr(dbu, "register_date", ADMIN["check"]["no_info"])
    balance = getattr(dbu, "balance", ADMIN["check"]["no_info"])

    lots_amount, wins_amount = len(lots), len(wins)
    max_overdue, total_commission = 0, 0
    for l in commission_lots:
        overdue = int((time() - l.end_date) // 86400)
        max_overdue = max(max_overdue, overdue)
        total_commission += l.commission
    rating, rating_name = getattr(dbu, "rating", 0), getattr(
        dbu, "rating_name", ADMIN["check"]["no_info"]
    )
    if getattr(dbu, "loyal"):
        loyal = datetime.fromtimestamp(dbu.loyal).strftime(DATETIME_FORMAT)
    else:
        loyal = "—"

    tmpl = ADMIN["check"]["user_msg"]
    return tmpl.format(
        full_name=full_name,
        access=access_level,
        id=u.id,
        register_date=register_date,
        balance=balance,
        spent_money=spent,
        rating=rating,
        rating_name=rating_name,
        lots=lots_amount,
        wins=wins_amount,
        commission=total_commission,
        overdue=max_overdue,
        loyal=loyal,
    )


@labeler.message(
    CommandFilter(LITERALS, args=command_data["args"], required_args=REQUIRED_ARGS),
    AccessFilter(INFO_ACCESS),
)
async def check_handler(msg: Message):
    _, args = separate_args(msg.text)
    try:
        users = await get_users_from_links(msg.ctx_api, args, fields="photo_id")
    except ValueError as e:
        await msg.answer(ERRORS["not_vk_links"])
        return

    if not isinstance(users, list):
        users = [users]

    last_index = len(users) - 1
    await state_dispenser.set(
        msg.peer_id, EmptySG.EMPTY, users=users, last_index=last_index
    )
    text = await user_text(users[0])
    await msg.answer(
        text,
        attachment=f"photo{users[0].photo_id}",
        keyboard=swipe_kb("check", 0, last_index),
    )


@labeler.callback_query({"check": "swipe:{}"})
async def swipe_handler(e: MessageEvent):
    pl = e.object.payload
    offset = int(pl["check"].split(":")[-1])

    sp = await state_dispenser.get(e.object.peer_id)
    users = sp.payload["users"]
    last_index = sp.payload["last_index"]

    user = users[offset]
    text = await user_text(user)
    await e.edit_message(
        text,
        attachment=f"photo{user.photo_id}",
        keyboard=swipe_kb("check", offset, last_index),
    )
