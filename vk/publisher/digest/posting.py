from asyncio import sleep
from datetime import datetime
from time import time

from vkbottle_types.codegen.objects import GroupsGroupFull

from config.time import TZ
from config.vk import DIGEST_POSTING_TIME as DIGEST_TIME
from database.lots.models import Lot
from database.lots.utils import get_lots_ended_before
from enums.moderation import LotStatusDB
from templates import DIGEST

from ...hyperlinks import group_post_hl
from ..config import apis, logger, user_api
from .utils import cache_pic_for_all_groups, get_cached_pic, get_settings

DEFAULT_DELAY = 180  # 86400


async def digest_wrapper():
    groups = await cache_pic_for_all_groups()

    now = datetime.now(TZ)
    delay = 60 * ((DIGEST_TIME.hour - now.hour) * 60 + DIGEST_TIME.minute - now.minute)
    await sleep(delay)

    delay = DEFAULT_DELAY
    while True:
        try:
            await post_digests(groups)
            await sleep(delay)
        except Exception as e:
            logger.error(f"digest_wrapper: {e.__class__.__name__}: {e}")
            return


async def post_digests(groups: list[GroupsGroupFull]):
    end_date = int(time()) + 111222  # 86400
    for g in groups:
        lots = await get_lots_ended_before(
            end_date, group_id=-g.id, moderation_status=LotStatusDB.PUBLISHED.value
        )
        if lots:
            await _post_digest(g, lots)


async def get_lot_text(lot: Lot):
    tmpl = DIGEST["lot"]
    return tmpl.format(
        group_post_hl(lot.group_id, lot.post_id, lot.description),
        lot.last_bet or lot.start_price,
    )


async def get_digest_text(lots: list[Lot]):
    tmpl = DIGEST["digest"]
    lots_bets = list(filter(lambda x: x.last_bet, lots))
    lots_no_bets = list(set(lots) - set(lots_bets))
    texts = [
        [await get_lot_text(l) for l in lots_bets],
        [await get_lot_text(l) for l in lots_no_bets],
    ]
    return tmpl.format("\n".join(texts[0]), "\n".join(texts[1]))


async def _post_digest(group: GroupsGroupFull, lots: list[Lot]):
    text = await get_digest_text(lots)
    attachments = await get_cached_pic(group.id)

    post = await user_api.wall.post(
        owner_id=lots[0].group_id,
        from_group=1,
        message=text,
        attachments=attachments,
    )
    if get_settings()["to_pin"]:
        await user_api.wall.pin(owner_id=lots[0].group_id, post_id=post.post_id)
