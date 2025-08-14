import os
from vkbottle import API
from vkbottle.bot import BotLabeler
from log import get_logger

from ..types.labeler import labeler

PUBLISHER_TOKENS = os.getenv("PUBLISHER_TOKENS").split(" ")
USER_TOKEN = os.getenv("USER_TOKEN")

apis = [API(token) for token in PUBLISHER_TOKENS]
user_api = API(USER_TOKEN)
# labeler = BotLabeler()

logger = get_logger(__name__)
