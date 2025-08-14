import time

from vkbottle.bot import BotLabeler, Message, rules
from vkbottle_types.objects import MessagesConversation, UsersUserFull

from ...types.labeler import labeler
from ..rules.command import CommandFilter
from .__utils import get_command

__literals = get_command("ping")["literals"]


@labeler.message(CommandFilter(__literals))
async def ping_handler(message: Message, past_time: float = 10**8):
    delta = time.time() - past_time
    await message.answer(f"pong! {delta:.3f} seconds")
