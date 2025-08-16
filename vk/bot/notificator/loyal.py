from asyncio import sleep
from datetime import datetime

from config.time import TZ
from config.vk import LOYAL_NOTIFICATIONS_TIME as LOYAL_TIME
from config.vk import LOYAL_REMINDERS
from database.lots.utils import get_lot
from database.users.utils import get_users_with_loyal_lt
from templates import LOYAL_NOTIFICATIONS as LOYAL

from ..config import logger
from .utils import send_notification

DEFAULT_DELAY = 86400


async def loyal_wrapper():
    now = datetime.now(TZ)
    notification_seconds = LOYAL_TIME.hour * 3600 + LOYAL_TIME.minute * 60
    delay = (
        DEFAULT_DELAY
        - (now.hour * 3600 + now.minute * 60 + now.second)
        + notification_seconds
    )
    await sleep(delay)

    while True:
        try:
            await notificate_loyal_users()
            await sleep(DEFAULT_DELAY)
        except Exception as e:
            logger.error(f"loyal_wrapper: {e.__class__.__name__}: {e}")
            return


async def notificate_loyal_users():
    now = int(datetime.now(TZ).timestamp())
    users = {}
    for lr in LOYAL_REMINDERS:
        th = now + lr * 86400
        users[lr] = await get_users_with_loyal_lt(th)

    if not users:
        return

    tmpl = LOYAL["user_notification"]
    for days, users in users.items():
        text = tmpl.format(days)
        user_group_mappings = {}
        for u in users:
            uid = u.user_id
            lots = await get_lot(uid)
            if lots:
                gid = lots[0].group_id
                user_group_mappings.setdefault(gid, []).append(uid)

        for gid, ids in user_group_mappings.items():
            for max_ind in range(0, len(ids), 100):
                user_ids = ids[max_ind : max_ind + 100]
                await send_notification(gid, ",".join(map(str, user_ids)), text)
