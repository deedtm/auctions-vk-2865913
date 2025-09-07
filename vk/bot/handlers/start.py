from vkbottle.bot import Message

from templates import COMMANDS

from ...types.labeler import labeler
from ..rules import CommandFilter, UnregisteredFilter
from .__utils import get_command

__literals = get_command("start")["literals"]


@labeler.message(fuzzy="Начать")
@labeler.message(fuzzy="Старт")
@labeler.message(fuzzy="Привет")
@labeler.message(CommandFilter(__literals))
@labeler.message(UnregisteredFilter())
async def start_handler(message: Message):
    await message.answer(COMMANDS["start"])
