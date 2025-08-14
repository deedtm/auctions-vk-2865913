from vkbottle import Bot

from ..types import labeler
from .config import api, state_dispenser
from .error_handler import *
from .handlers import *
from .middlewares import *
from .rules import *

labeler.message_view.register_middleware(NoDoublingMessageMiddleware)
labeler.raw_event_view.register_middleware(NoDoublingRawMiddleware)
labeler.message_view.register_middleware(RegistrationMiddleware)

# labeler.custom_rules["command"] = CommandFilter
labeler.custom_rules["payload"] = PayloadFilter
labeler.custom_rules["unregistered"] = UnregisteredFilter


bot = Bot(
    # api=api,
    labeler=labeler,
    state_dispenser=state_dispenser,
)
