import os
from dotenv import load_dotenv
from vkbottle import API, BuiltinStateDispenser
from vkbottle.bot import BotLabeler

load_dotenv()

VK_TOKEN = os.getenv("VK_TOKEN")


api = API(VK_TOKEN)
labeler = BotLabeler()
state_dispenser = BuiltinStateDispenser()
