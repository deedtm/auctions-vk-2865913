from vkbottle.bot import Bot
from .config import *
from .handlers import *


# bot = Bot(labeler=labeler)
bots = [Bot(labeler=labeler, api=api) for api in apis]
