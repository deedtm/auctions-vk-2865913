from random import randint

from ...publisher.utils import get_api


async def send_notification(group_id: int, user_id: int, text: str, **kwargs):
    api = get_api(group_id)
    await api.messages.send(
        peer_id=user_id, random_id=randint(10**6, 10**8), message=text, **kwargs
    )
