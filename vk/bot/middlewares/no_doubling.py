from vkbottle import BaseMiddleware
from vkbottle.bot import Message

_HANDLED = set()


class EmptyError(Exception):
    """Raised when the middleware is stopped without an error."""


class NoDoublingRawMiddleware(BaseMiddleware[dict]):
    def __init__(self, event, view):
        super().__init__(event, view)

    async def pre(self):
        event_id = self.event.get("event_id")
        if not event_id or event_id in _HANDLED:
            self.stop('DOUBLING DETECTED!!!')

        if len(_HANDLED) > 1000:
            _HANDLED.clear()

        _HANDLED.add(event_id)

    def __repr__(self):
        return self.__class__.__name__

    def __str__(self):
        return self.__repr__()


class NoDoublingMessageMiddleware(BaseMiddleware[Message]):
    def __init__(self, event, view):
        super().__init__(event, view)

    async def pre(self):
        if self.event.id in _HANDLED:
            self.stop('DOUBLING DETECTED!!!')

        if len(_HANDLED) > 1000:
            _HANDLED.clear()

        _HANDLED.add(self.event.id)

    def __repr__(self):
        return self.__class__.__name__

    def __str__(self):
        return self.__repr__()
