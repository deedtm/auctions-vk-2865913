from vkbottle import Bot
from .config import api, state_dispenser, labeler
from .handlers import *
from .middlewares import RegistrationMiddleware

labeler.message_view.register_middleware(RegistrationMiddleware)

bot = Bot(
    api=api,
    labeler=labeler,
    state_dispenser=state_dispenser,
)
