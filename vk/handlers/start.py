from ..config import labeler
from vkbottle.bot import Message, BotLabeler, rules
from vkbottle_types.objects import MessagesConversation, UsersUserFull
from ..rules.command import CommandFilter
from templates import COMMANDS
from .__utils import get_command

__literals = get_command("start")["literals"]


@labeler.message(text="Начать")
@labeler.message(CommandFilter(__literals))
async def start_handler(message: Message):
    await message.answer(COMMANDS["start"])
