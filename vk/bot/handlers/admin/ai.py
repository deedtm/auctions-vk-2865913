from vkbottle.bot import Message

from config.admin import INFO_ACCESS
from database.groups.utils import get_group
from database.lots.models import Lot
from database.users.utils import get_user
from templates import ADMIN_COMMANDS as ADMIN

from ....hyperlinks import group_post_hl
from ....keyboards.swipe import swipe_kb
from ....states_groups import EmptySG
from ....types import MessageEvent, labeler
from ...config import state_dispenser
from ...rules import AccessFilter, CommandFilter
from .__utils import get_command, get_required_args, separate_args
from .utils import get_lots_by_ids

command_data = get_command("ai")
LITERALS = command_data["literals"]
ARGS = command_data["args"]
REQUIRED_ARGS = get_required_args(command_data)


@labeler.message(
    CommandFilter(LITERALS, args=ARGS, required_args=REQUIRED_ARGS),
    AccessFilter(INFO_ACCESS),
)
async def ai_handler(msg: Message):
    _, args = separate_args(msg.text)

    lots = await get_lots_by_ids(args)
    if not lots:
        text = ADMIN["ai"]["no_lots"]
        await msg.answer(text)
        return

    last_index = len(lots) - 1
    await state_dispenser.set(
        msg.peer_id, EmptySG.EMPTY, lots=lots, last_index=last_index
    )

    l: Lot = lots[0]
    g = await get_group(l.group_id)
    template = g.auctions_template
    hl = group_post_hl(l.group_id, l.post_id, ADMIN["ai"]["link_placeholder"])
    user = await get_user(l.user_id)
    urgent, main, additional = await l.as_user_review(user, additional_lines=[hl])
    text = template.format(URGENT=urgent, MAIN=main, ADDITIONAL=additional)
    await msg.answer(text, attachment=l.photos, keyboard=swipe_kb("ai", 0, last_index))


@labeler.callback_query({"ai": "swipe:{}"})
async def swipe_handler(e: MessageEvent):
    pl = e.object.payload
    offset = int(pl["ai"].split(":")[-1])

    sp = await state_dispenser.get(e.object.peer_id)
    lots = sp.payload["lots"]
    last_index = sp.payload["last_index"]

    l: Lot = lots[offset]
    g = await get_group(l.group_id)
    template = g.auctions_template
    hl = group_post_hl(l.group_id, l.post_id, ADMIN["ai"]["link_placeholder"])
    user = await get_user(l.user_id)
    urgent, main, additional = await l.as_user_review(user, additional_lines=[hl])
    text = template.format(URGENT=urgent, MAIN=main, ADDITIONAL=additional)
    await e.edit_message(
        text, attachment=l.photos, keyboard=swipe_kb("ai", offset, last_index)
    )
