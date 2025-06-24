from ..config import labeler
from vkbottle.bot import Message, BotLabeler, rules
from vkbottle_types.objects import MessagesConversation, UsersUserFull
from .__utils import get_command
from ..rules.command import CommandFilter

__literals = get_command("ping")["literals"]


@labeler.message(CommandFilter(__literals))
async def ping_handler(message: Message):
    await message.answer("pong")


@labeler.message(lev="кто я")
async def who_i_am_handler(message: Message, info: UsersUserFull):
    text = [f"{k} — {v}" for k, v in info.__dict__.items() if v is not None]
    await message.answer("\n".join(text))
