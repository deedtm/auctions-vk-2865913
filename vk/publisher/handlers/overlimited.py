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

    if pl["overlimited"] == "same_group":
        fields = {"moderation_status": LotStatusDB.WAITING_LIMIT.value}
    else:
        available_group_id = pl["overlimited"].split("_")[0]
        fields = {
            "group_id": int(available_group_id),
            "moderation_status": LotStatusDB.MODERATED.value,
        }

    for lot in lots:
        await update_lot_data(lot.id, **fields)

    await e.edit_message(PUBLISH["overlimited_handled"], keyboard=None)
