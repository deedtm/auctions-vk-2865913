from vkbottle.bot import BotLabeler
from vkbottle import GroupEventType
from .message_event import MessageEvent
from ..bot.rules.payload import PayloadFilter
from .views import MessageView, RawEventView


msg_view = MessageView()
raw_event_view = RawEventView()

class Labeler(BotLabeler):
    def callback_query(self, payload: dict | list[dict]):
        def decorator(func):
            return self.raw_event(
                GroupEventType.MESSAGE_EVENT,
                MessageEvent,
                PayloadFilter(payload),
            )(func)

        return decorator
    
    def views(self):
        return {"message": msg_view, "raw": raw_event_view}


labeler = Labeler(msg_view, raw_event_view)
