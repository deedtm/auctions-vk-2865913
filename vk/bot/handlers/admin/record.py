from os import path as p

from vkbottle import DocMessagesUploader
from vkbottle.bot import Message

from config.admin import EXPORT_DIRECTORY, INFO_ACCESS
from database.export.utils import export_to_excel
from database.lots.utils import get_lots_with_commissions
from database.users.utils import get_user
from templates import ERRORS

from ....types import labeler
from ...rules import AccessFilter, CommandFilter
from .__utils import get_command

command_data = get_command("record")
LITERALS = command_data["literals"]


@labeler.message(CommandFilter(LITERALS), AccessFilter(INFO_ACCESS))
async def record_handler(msg: Message):
    lots = await get_lots_with_commissions()
    if not lots:
        await msg.answer(ERRORS["failed_get_data"])
        return

    users, added_ids = [], []
    for lot in lots:
        if lot.user_id in added_ids:
            continue
        user = await get_user(lot.user_id)
        users.append(user)
        added_ids.append(lot.user_id)
    users = list(sorted(users, key=lambda x: x.id))

    filepath = p.join(EXPORT_DIRECTORY, msg.text)
    filepath = export_to_excel(users, filepath)
    doc_msgs_uploader = DocMessagesUploader(msg.ctx_api)
    docs = await doc_msgs_uploader.upload(filepath, peer_id=msg.peer_id)
    await msg.answer(attachment=docs)
