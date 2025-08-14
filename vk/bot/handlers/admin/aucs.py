from os import path as p

from vkbottle.bot import Message

from config.admin import EXPORT_DIRECTORY, INFO_ACCESS
from database.export.utils import export_to_excel
from database.lots.utils import get_lot
from templates import ERRORS

from ....types import labeler
from ....utils import get_groups_from_links, get_self_group
from ...config import doc_msgs_uploader
from ...rules import AccessFilter, CommandFilter
from .__utils import get_command, separate_args

command_data = get_command("aucs")
LITERALS = command_data["literals"]
ARGS = command_data["args"]


@labeler.message(CommandFilter(LITERALS, args=ARGS), AccessFilter(INFO_ACCESS))
async def aucs_handler(msg: Message):
    literal, args = separate_args(msg.text)

    if args:
        group = await get_groups_from_links(msg.ctx_api, args)
        group_id = -abs(group.id)
    else:
        group = await get_self_group(msg.ctx_api)
        group_id = group.id

    lots = await get_lot(group_id=group_id)
    if not lots:
        await msg.answer(ERRORS["failed_get_data"])
        return

    filepath = p.join(EXPORT_DIRECTORY, literal + str(group_id))
    filepath = export_to_excel(lots, filepath)
    docs = await doc_msgs_uploader.upload(filepath, peer_id=msg.peer_id)
    await msg.answer(attachment=docs)
