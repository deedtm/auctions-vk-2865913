from config.vk import GROUP_LOTS_LIMIT
from database.groups.utils import get_available_group
from database.lots.utils import get_lots_by_fields, update_lot_data
from enums.moderation import LotStatusDB
from templates import PUBLISH

from ...types import MessageEvent, labeler


@labeler.callback_query({"overlimited": "{}_group"})
async def overlimited_handler(e: MessageEvent):
    o = e.object
    pl = o.payload

    lots = await get_lots_by_fields(
        moderation_status=LotStatusDB.OVERLIMITED.value,
        user_id=o.user_id,
        group_id=-abs(e.group_id),
    )
    if not lots:
        return

    if pl["overlimited"] == "other_group":
        ag = await get_available_group(e.group_id, GROUP_LOTS_LIMIT)
        fields = {
            "group_id": ag.group_id,
            "moderation_status": LotStatusDB.MODERATED.value,
        }
    elif pl["overlimited"] == "same_group":
        fields = {"moderation_status": LotStatusDB.WAITING_LIMIT.value}

    for lot in lots:
        await update_lot_data(lot.id, **fields)

    await e.edit_message(PUBLISH["overlimited_handled"], keyboard=None)
