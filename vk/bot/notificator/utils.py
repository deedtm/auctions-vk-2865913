from random import randint

from ..config import api


async def send_notification(user_id: int, text: str, **kwargs):
    await api.messages.send(
        peer_id=user_id, random_id=randint(10**6, 10**8), message=text, **kwargs
    )
