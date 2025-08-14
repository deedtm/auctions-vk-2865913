from vkbottle.bot import Message

from config.admin import SET_ACCESS
from database.lots.utils import update_lot_data
from templates import ADMIN_COMMANDS as ADMIN

from ....hyperlinks import group_post_hl
from ....types import labeler
from ...rules import AccessFilter, CommandFilter
from .__utils import get_command, get_required_args, separate_args
from .utils import get_lots_by_ids

command_data = get_command("pa")
LITERALS = command_data["literals"]
ARGS = command_data["args"]
REQUIRED_ARGS = get_required_args(command_data)


@labeler.message(
    CommandFilter(LITERALS, args=ARGS, required_args=REQUIRED_ARGS),
    AccessFilter(SET_ACCESS),
)
async def pa_handler(msg: Message):
    _, args = separate_args(msg.text)
    lots = await get_lots_by_ids(args)
    if not lots:
        await msg.answer(ADMIN["pa"]["no_lots"])
        return

    for lot in lots:
        await update_lot_data(lot.id, commission=None)

    tmpl_key = "paid_many" if len(lots) > 1 else "paid"
    lots_hls = [group_post_hl(l.group_id, l.post_id, l.description) for l in lots]
    await msg.answer(ADMIN["pa"][tmpl_key].format(", ".join(lots_hls)))
