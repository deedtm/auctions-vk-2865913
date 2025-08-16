import os
import time

from vkbottle import BaseMiddleware
from vkbottle.bot import Message

from config.admin import ADMIN_ACCESS, MODERATOR_ACCESS
from database.users.utils import add_user, get_user
from templates import COMMANDS

from ..config import state_dispenser
from ..handlers.__utils import get_command

STOP_LITERALS = get_command("stop")["literals"]
STOP_LITERALS.extend([l[1:] for l in STOP_LITERALS])
CACHED_USERS = set()


class RegistrationMiddleware(BaseMiddleware[Message]):
    def __init__(self, event, view):
        super().__init__(event, view)
        self.moderators_ids = os.getenv("MODERATORS_IDS", "").split()
        self.admins_ids = os.getenv("ADMINS_IDS", "").split()

    async def pre(self):
        if self.event.text[1:] in ["ping", "ing"]:
            self.send({"past_time": time.time()})
        elif self.event.text[1:] in STOP_LITERALS and self.event.state_peer:
            await state_dispenser.delete(self.event.state_peer.peer_id)
            await self.event.answer(COMMANDS["stop"])
            return

        if self.event.from_id in CACHED_USERS:
            return
        
        api = self.event.ctx_api
        user = (await api.users.get(user_ids=[self.event.from_id]))[0]
        user_db = await get_user(user.id)
        if user_db is None:
            kwargs = {}
            if str(user.id) in self.admins_ids:
                kwargs["access_level"] = ADMIN_ACCESS
            elif str(user.id) in self.moderators_ids:
                kwargs["access_level"] = MODERATOR_ACCESS
            await add_user(user, **kwargs)
            self.send({"info": user})
        CACHED_USERS.add(user.id)
