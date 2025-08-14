from vkbottle.bot import Message

from config.admin import SET_ACCESS
from database.users.utils import get_user, update_user_data
from templates import ADMIN_COMMANDS as ADMIN
from templates import ERRORS

from ....hyperlinks import user_hl
from ....types import labeler
from ....utils import get_users_from_links
from ...rules import AccessFilter, CommandFilter
from .__utils import get_command, get_required_args, separate_args

command_data = get_command("setbalance")
LITERALS = command_data["literals"]
ARGS = command_data["args"]
REQUIRED_ARGS = get_required_args(command_data)


@labeler.message(
    CommandFilter(LITERALS, args=ARGS, required_args=REQUIRED_ARGS),
    AccessFilter(SET_ACCESS),
)
async def setbalance_handler(msg: Message):
    _, args = separate_args(msg.text)
    link, new_balance = args[0], args[1] if len(args) > 1 else '0'

    if not new_balance.isdigit():
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
    await update_user_data(user.id, balance=new_balance)
    tmpl = ADMIN["setbalance"]["success"]
    text = tmpl.format(
        user_hl(user_db.id, user_db.full_name), user_db.balance, new_balance
    )
    await msg.answer(text)
