from vkbottle.bot import Message

from database.lots.utils import update_lot_data
from enums.moderation import LotStatusDB
from templates import PUBLISH

from ...keyboards import PUBLISHER
from ...states_groups.publisher import PublisherStates
from ...types.labeler import labeler


@labeler.message(state=PublisherStates.OVERLIMITED_CHOICE)
async def overlimited_handler(msg: Message):
    if not msg.text or msg.text not in [
        PUBLISHER["other_group"],
        PUBLISHER["same_group"],
    ]:
        return

    lots = msg.state_peer.payload["lots"]

    if msg.text == PUBLISHER["other_group"]:
        ag = msg.state_peer.payload["available_group"]
        fields = {
            "group_id": ag.group_id,
            "moderation_status": LotStatusDB.MODERATED.value,
        }
    elif msg.text == PUBLISHER["same_group"]:
        fields = {"moderation_status": LotStatusDB.WAITING_LIMIT.value}

    for lot in lots:
        await update_lot_data(lot.id, **fields)

    await msg.answer(PUBLISH["overlimited_handled"])
