from vkbottle.bot import Message

from config.admin import ADMIN_ACCESS
from templates import ADMIN_COMMANDS as ADMIN
from templates import ERRORS

from ....hyperlinks import user_hl
from ....publisher.utils import remove_excessive_photos
from ....types import labeler
from ...config import logger
from ...rules import AccessFilter, CommandFilter
from .__utils import get_command


@labeler.message(
    CommandFilter(get_command("removephotos")["literals"]),
    AccessFilter(ADMIN_ACCESS),
)
async def removephotos_handler(msg: Message):
    data = await remove_excessive_photos()
    templates = ADMIN["removephotos"]

    if data is None:
        text = templates["no_photos"]
    else:
        lengths = len(data[0]), len(data[1])
        logger.debug(
            "User {} removed {} files from {} lots".format(msg.from_id, *lengths)
        )
        text = templates["success"].format(*lengths)

    await msg.answer(text)
