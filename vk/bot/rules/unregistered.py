from vkbottle.bot import Message
from vkbottle.dispatch.rules import ABCRule
from database.users.utils import get_user


class UnregisteredFilter(ABCRule[Message]):
    async def check(self, event: Message) -> bool:
        user = await event.get_user()
        return not bool(await get_user(user.id))
