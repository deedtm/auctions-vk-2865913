from vkbottle.bot import Message

from database.groups.utils import get_group
from database.lots.utils import get_lots_by_fields
from database.users.utils import get_user
from enums.moderation import LotStatusDB
from templates import COMMANDS, ERRORS

from ...keyboards.swipe import swipe_kb
from ...states_groups import EmptySG
from ...types import MessageEvent, labeler
from ..config import state_dispenser
from ..rules.command import CommandFilter
from .__utils import get_command

__literals = get_command("wins")["literals"]


@labeler.message(CommandFilter(__literals))
async def wins_handler(msg: Message):
    ended_lots = await get_lots_by_fields(
        last_bettor_id=msg.from_id, moderation_status=LotStatusDB.ENDED.value
    )
    closed_lots = await get_lots_by_fields(
        last_bettor_id=msg.from_id, moderation_status=LotStatusDB.CLOSED.value
    )
    lots = ended_lots + closed_lots
    if not lots:
        text = COMMANDS["wins"]["no_lots"]
        await msg.answer(text)
        return

    last_index = len(lots) - 1

    lot = lots[0]
    g = await get_group(lot.group_id)
    template = g.auctions_template
    user = await get_user(lot.user_id)
    urgent, main, additional = await lot.as_user_review(user, for_bettor=True)
    text = template.format(URGENT=urgent, MAIN=main, ADDITIONAL=additional)
    await msg.answer(text, lot.photos, keyboard=swipe_kb("wins", 0, last_index))
    await state_dispenser.set(
        msg.peer_id, EmptySG.EMPTY, lots=lots, last_index=last_index
    )


@labeler.callback_query({"wins": "swipe:{}"})
async def edit_lot_msg(e: MessageEvent):
    pl = e.object.payload
    offset = int(pl["wins"].split(":")[-1])

    sp = await state_dispenser.get(e.object.peer_id)
    try:
        lots = sp.payload["lots"]
        last_index = sp.payload["last_index"]
    except AttributeError:
        await e.edit_message(ERRORS['outdated'])
        return
    
    lot = lots[offset]
    g = await get_group(lot.group_id)
    template = g.auctions_template
    user = await get_user(lot.user_id)
    urgent, main, additional = await lot.as_user_review(user, for_bettor=True)
    text = template.format(URGENT=urgent, MAIN=main, ADDITIONAL=additional)
    await e.edit_message(
        text, attachment=lot.photos, keyboard=swipe_kb("wins", offset, last_index)
    )
