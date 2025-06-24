from vkbottle import BaseMiddleware
from vkbottle.bot import Message
from database.utils import get_user, add_user
from ..handlers.ping import who_i_am_handler
from ..config import api

# class GeneralMiddleware(BaseMiddleware[Message]):
#     async def pre(self):
#         await self.event.answer(
#             "Сообщение было получено, но не обработано. "
#             "Пожалуйста, проверьте логи для получения дополнительной информации."
#         )
#         # if self.event.from_id < 0:
#         #     self.stop("Groups are not allowed to use bot")
#     async def post(self):
#         if not self.handlers:
#             self.stop("Сообщение не было обработано")
#         await self.event.answer(
#             "Сообщение было обработано:\n\n"
#             f"View - {self.view}\n\n"
#             f"Handlers - {self.handlers}"
#         )


class RegistrationMiddleware(BaseMiddleware[Message]):
    call_count = 0

    def __init__(self, event, view):
        super().__init__(event, view)
        self.cached = False

    async def pre(self):
        user = (await api.users.get(user_ids=[self.event.from_id]))[0]
        user_db = await get_user(user.id)
        if user_db is None:
            await add_user(user)
            self.cached = False
        else:
            self.cached = True
        self.send({"info": user})

    async def post(self):
        if who_i_am_handler in self.handlers:
            self.__class__.call_count += 1
            cached_str = "был" if self.cached else "не был"
            await self.event.answer(
                f"Ответ {cached_str} взят из кеша. Количество вызовов: {self.call_count}"
            )
