from vkbottle.bot import Message
from vkbottle.tools.formatting import *

from config.admin import BAN_ACCESS, INFO_ACCESS, SET_ACCESS
from database.users.utils import get_user
from templates import COMMANDS
from utils import int_to_emojis

from ...types import labeler
from ..rules.command import CommandFilter
from .__utils import get_command, get_commands
from .admin.__utils import get_commands as get_admin_commands

__literals = get_command("help")["literals"]


@labeler.message(CommandFilter(__literals))
async def help_handler(msg: Message):
    commands = get_commands()

    command_fmt = "• {} {}— {}"
    commands_text = []
    for c in commands:
        literals = ", ".join(c["literals"])
        args = " ".join(c.get("args", [])) + " "
        commands_text.append(command_fmt.format(literals, args, c["description"]))

    user = await get_user(msg.from_id)
    admin_commands = get_admin_commands()
    admin_commands = sorted(admin_commands, key=lambda x: x.get("access", 1))
    last_iterated_access = -1
    for c in admin_commands:
        access = c.get("access", last_iterated_access)
        if access > user.access_level:
            break
        if not last_iterated_access == access:
            emoji = int_to_emojis(access)
            commands_text.append(COMMANDS["help"]["access_header"].format(emoji))
            last_iterated_access = access
        literals = ", ".join(c["literals"])
        args = " ".join(c.get("args", [])) + " "
        commands_text.append(command_fmt.format(literals, args, c["description"]))

    text = COMMANDS["help"]["user_header"].format("\n".join(commands_text))
    await msg.answer(text)
