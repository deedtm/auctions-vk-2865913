from vkbottle.bot import Message
from vkbottle.dispatch.rules import ABCRule

from database.users.utils import is_enough_access


class AccessFilter(ABCRule[Message]):
    def __init__(self, access_level: int):
        self.access_level = access_level

    async def check(self, event: Message) -> bool:
        user_vk = await event.get_user()
        return await is_enough_access(self.access_level, user_id=user_vk.id)
    