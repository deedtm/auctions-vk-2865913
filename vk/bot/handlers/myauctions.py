from vkbottle.bot import Message

from database.groups.utils import get_group
from database.lots.models import Lot
from database.lots.utils import get_lots_by_user
from database.users.utils import get_user
from templates import COMMANDS

from ...keyboards.swipe import swipe_kb
from ...states_groups import EmptySG
from ...types import MessageEvent, labeler
from ..config import state_dispenser
from ..rules.command import CommandFilter
from .__utils import get_command

__literals = get_command("myauctions")["literals"]


@labeler.message(CommandFilter(__literals))
async def myauctions_handler(msg: Message):
    lots = await get_lots_by_user(msg.from_id)
    if not lots:
        text = COMMANDS["myauctions"]["no_lots"]
        await msg.answer(text)
        return

    last_index = len(lots) - 1

    lot = lots[0]
    g = await get_group(lot.group_id)
    template = g.auctions_template
    user = await get_user(lot.user_id)
    urgent, main, additional = await lot.as_user_review(user)
    text = template.format(URGENT=urgent, MAIN=main, ADDITIONAL=additional)
    await msg.answer(text, lot.photos, keyboard=swipe_kb("myauctions", 0, last_index))
    await state_dispenser.set(
        msg.peer_id, EmptySG.EMPTY, lots=lots, last_index=last_index
    )


@labeler.callback_query({"myauctions": "swipe:{}"})
async def edit_lot_msg(e: MessageEvent):
    pl = e.object.payload
    offset = int(pl["myauctions"].split(":")[-1])

    sp = await state_dispenser.get(e.object.peer_id)
    lots = sp.payload["lots"]
    last_index = sp.payload["last_index"]

    lot = lots[offset]
    g = await get_group(lot.group_id)
    template = g.auctions_template
    user = await get_user(lot.user_id)
    urgent, main, additional = await lot.as_user_review(user)
    text = template.format(URGENT=urgent, MAIN=main, ADDITIONAL=additional)
    await e.edit_message(
        text, attachment=lot.photos, keyboard=swipe_kb("myauctions", offset, last_index)
    )
