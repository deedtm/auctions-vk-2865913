from ..config import labeler
from vkbottle.bot import Message
from vkbottle.tools.formatting import *
from ..rules.command import CommandFilter
from templates import COMMANDS
from .__utils import get_command, get_commands


__literals = get_command("help")["literals"]


@labeler.message(CommandFilter(__literals))
async def help_handler(msg: Message):
    commands = get_commands()
    commands_text = []
    for c in commands:
        literals = "/".join(c["literals"])        
        commands_text.append(f"{bold(literals)} — {c['description']}")
    text = COMMANDS["help"].format("\n".join(commands_text))
    await msg.answer(text)
