from vkbottle.bot import Message

from config.admin import ADMIN_ACCESS
from database.lots.utils import replace_moderation_status
from enums.moderation import LotStatusDB
from templates import ADMIN_COMMANDS as ADMIN

from ....types import labeler
from ...rules import AccessFilter, CommandFilter
from .__utils import get_command

command_data = get_command("publishoverlimit")
LITERALS = command_data["literals"]


@labeler.message(CommandFilter(LITERALS), AccessFilter(ADMIN_ACCESS))
async def publish_overlimit_handler(msg: Message):
    lots_amount = await replace_moderation_status(
        LotStatusDB.WAITING_LIMIT.value, LotStatusDB.MODERATED.value
    )
    text = ADMIN["publish_overlimit"].format(lots_amount)
    await msg.answer(text)
