from vkbottle.bot import Message
from vkbottle.exception_factory import VKAPIError

from config.admin import BAN_ACCESS
from templates import ADMIN_COMMANDS as ADMIN
from templates import ERRORS

from ....hyperlinks import user_hl
from ....publisher.config import user_api
from ....types import labeler
from ....utils import get_self_group, get_users_from_links
from ...rules import AccessFilter, CommandFilter
from .__utils import get_command, separate_args

command_data = get_command("unban")
LITERALS = command_data["literals"]


@labeler.message(CommandFilter(LITERALS), AccessFilter(BAN_ACCESS))
async def unban_handler(msg: Message):
    _, args = separate_args(msg.text)
    link = args[0]

    try:
        user = await get_users_from_links(msg.ctx_api, link)
    except ValueError as e:
        await msg.answer(ERRORS["not_vk_links"])
        return
    if not user:
        await msg.answer(ERRORS["not_found"])
        return

    group = await get_self_group(msg.ctx_api, False)
    try:
        await user_api.groups.unban(group_id=group.id, user_id=user.id)

        tmpl = ADMIN["unban"]["success"]
        text = tmpl.format(user_hl(user.id, f"{user.first_name} {user.last_name}"))
    except VKAPIError as e:
        undefined_text = ERRORS["vk_api_undefined"].format(str(e))
        # error_msg = getattr(e, "error_msg", undefined_text)
        err_text = getattr(e, "kwargs", {}).get("error_text", undefined_text)
        text = ERRORS["vk_api"].format(err_text)
    await msg.answer(text)
