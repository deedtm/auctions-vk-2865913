from vkbottle.bot import Message

from config.admin import ADMIN_ACCESS, SET_ACCESS
from database.users.utils import get_user, update_user_data
from templates import ADMIN_COMMANDS as ADMIN
from templates import ERRORS

from ....hyperlinks import user_hl
from ....types import labeler
from ....utils import get_users_from_links
# from ...notificator.utils import send_notification
from ...rules import AccessFilter, CommandFilter
from .__utils import get_command, get_required_args, separate_args

command_data = get_command("setaccess")
LITERALS = command_data["literals"]
ARGS = command_data["args"]
REQUIRED_ARGS = get_required_args(command_data)


@labeler.message(
    CommandFilter(LITERALS, args=ARGS, required_args=REQUIRED_ARGS),
    AccessFilter(SET_ACCESS),
)
async def setaccess_handler(msg: Message):
    _, args = separate_args(msg.text)
    link, new_access = args[0], args[1] if len(args) > 1 else 0

    if not new_access.isdigit():
        await msg.answer(ERRORS["not_int"])
        return

    try:
        user = await get_users_from_links(msg.ctx_api, link)
    except ValueError as e:
        await msg.answer(ERRORS["not_vk_links"])
        return
    if not user:
        await msg.answer(ERRORS["not_found"])
        return

    user_db = await get_user(user.id)
    if not user_db:
        tmpl = ERRORS["no_user_in_db"]
        await msg.answer(tmpl)
        return

    if user_db.access_level < ADMIN_ACCESS:
        msg_author_db = await get_user(msg.from_id)
        if user_db.access_level >= msg_author_db.access_level:
            await msg.answer(ERRORS["cannot_update_higher_access"])
            return

    await update_user_data(user.id, access_level=new_access)

    tmpl = ADMIN["setaccess"]["success"]
    text = tmpl.format(
        user_hl(user.id, f"{user.first_name} {user.last_name}"),
        user_db.access_level,
        new_access,
    )
    await msg.answer(text)

    # tmpl = ADMIN["setaccess"]["user_notification"]
    # text = tmpl.format(user_db.access_level, new_access)
    # await send_notification(msg.group_id, user.id, text)
