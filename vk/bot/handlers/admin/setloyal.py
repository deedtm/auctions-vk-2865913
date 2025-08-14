from datetime import datetime

from vkbottle.bot import Message

from config.admin import SET_ACCESS
from config.time import DATETIME_FORMAT as DTFMT
from config.time import TZ
from database.users.utils import update_user_data
from templates import ADMIN_COMMANDS as ADMIN
from templates import ERRORS

from ....hyperlinks import user_hl
from ....types import labeler
from ....utils import get_users_from_links
from ...notificator.utils import send_notification
from ...rules import AccessFilter, CommandFilter
from .__utils import get_command, get_required_args, separate_args

command_data = get_command("setloyal")
LITERALS = command_data["literals"]
ARGS = command_data["args"]
REQUIRED_ARGS = get_required_args(command_data)


@labeler.message(
    CommandFilter(LITERALS, args=ARGS, required_args=REQUIRED_ARGS),
    AccessFilter(SET_ACCESS),
)
async def setloyal_handler(msg: Message):
    _, args = separate_args(msg.text)
    link, new_loyal_days = args[0], args[1] if len(args) > 1 else 0

    if not new_loyal_days.isdigit():
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

    new_loyal = int(datetime.now(TZ).timestamp()) + int(new_loyal_days) * 86400
    await update_user_data(user.id, loyal=new_loyal)

    loyal_date = datetime.fromtimestamp(new_loyal, tz=TZ).strftime(DTFMT)

    tmpl = ADMIN["setloyal"]["success"]
    text = tmpl.format(
        user_hl(user.id, f"{user.first_name} {user.last_name}"), loyal_date
    )
    await msg.answer(text)

    tmpl = ADMIN["setloyal"]["user_notification"]
    text = tmpl.format(loyal_date)
    await send_notification(user.id, text)
