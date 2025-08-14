from asyncio import sleep
from time import time

from config.vk import BAN_COMMENT, BANS_INTERVAL
from config.vk import LAST_COLLECTOR_REMINDER as LAST_REMINDER
from database.groups.utils import get_all_groups
from database.lots.utils import get_lots_with_commissions

from ...publisher.config import user_api
from ..config import api, logger


async def ban_wrapper():
    delay = 86400 - (time() % 86400)
    await sleep(delay)
    
    while True:
        try:
            await ban()
            await sleep(BANS_INTERVAL)
        except Exception as e:
            logger.error(f"ban_wrapper: {e.__class__.__name__}: {e}")
            return


async def ban():
    end_time = int(time()) - LAST_REMINDER * 86400
    lots = await get_lots_with_commissions(end_date=end_time)
    if not lots:
        return

    users_ids = set([l.user_id for l in lots])

    for id in users_ids:
        await _ban_user(id)


async def _ban_user(user_id: int):
    groups = await get_all_groups()
    for g in groups:
        await user_api.groups.ban(
            group_id=-g.group_id,
            owner_id=user_id,
            comment=BAN_COMMENT,
            comment_visible=1,
        )
