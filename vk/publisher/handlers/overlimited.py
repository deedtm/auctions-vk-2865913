from vkbottle.bot import Message
from database.lots.utils import update_lot_data
from templates import PUBLISH
from ...states_groups.publisher import PublisherStates
from ...keyboards import PUBLISHER
from ...types.labeler import labeler
from enums.moderation import LotStatusDB


@labeler.message(state=PublisherStates.OVERLIMITED_CHOICE)
async def overlimited_handler(msg: Message):
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
