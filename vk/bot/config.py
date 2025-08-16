import os

from vkbottle import BuiltinStateDispenser, ErrorHandler

from config.t_api import *
from log import get_logger

# VK_TOKEN = os.getenv("VK_TOKEN")
MODERATORS_IDS = list(map(int, os.getenv("MODERATORS_IDS").split(" ")))

TERMINAL_KEY = os.getenv("TERMINAL_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")

# api = API(VK_TOKEN)
state_dispenser = BuiltinStateDispenser()
err_handler = ErrorHandler()
logger = get_logger("bot")
