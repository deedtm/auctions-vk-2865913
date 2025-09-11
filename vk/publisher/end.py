from asyncio import sleep
from random import randint
from typing import Optional

from vkbottle.exception_factory import VKAPIError

from config.vk import (
    AUCTIONS_CLOSING_INTERVAL,
    AUCTIONS_EXTENSION,
    MAX_RATING_TO_DANGER,
)
from database.groups.utils import get_group
from database.lots.models import Lot
from database.lots.utils import get_ended_lots, get_lots_by_fields, update_lot_data
from database.users.utils import get_user
from enums.moderation import LotStatusDB
from templates import BETS

from ..hyperlinks import group_post_hl
from ..keyboards.bets import Keyboard, seller_notification_kb
from ..publisher.utils import get_api
from .config import logger
from .utils import edit_post

_endings = {}
DEFAULT_DELAY = 60


async def close_wrapper():
    while True:
        try:
            await close_auctions()
            await sleep(DEFAULT_DELAY)
        except Exception as e:
            logger.error(f"close_wrapper: {e.__class__.__name__}: {e}")
            return


async def close_auctions():
    lots = await get_lots_by_fields(moderation_status=LotStatusDB.ENDED.value)
    if not lots:
        return

    for l in lots:
        res = await edit_post(l, close_comments=True)
        if res:
            await update_lot_data(l.id, moderation_status=LotStatusDB.CLOSED.value)
            logger.debug(f"Closed lot {l.id}")
        else:
            logger.debug(f"Failed to close lot {l.id}, skipping")
        await sleep(AUCTIONS_CLOSING_INTERVAL)



async def end_wrapper():
    delay = DEFAULT_DELAY
    while True:
        try:
            delay = await end_auctions()
            await sleep(delay)
        except Exception as e:
            logger.error(f"end_wrapper: {e.__class__.__name__}: {e}")
            return


async def end_auctions():
    lots = await get_ended_lots()
    if not lots:
        return DEFAULT_DELAY

    delays = [DEFAULT_DELAY]
    for lot in lots:
        delays.append(await _end_lot(lot))

    delays = list(filter(lambda x: x is not None, delays))
    if delays:
        return min(delays)
    return DEFAULT_DELAY


async def _end_lot(lot: Lot):
    global _endings

    if lot.moderation_status != LotStatusDB.REDEEMED.value and lot.last_bet:
        ending_unix = lot.end_date
        if ending_unix - lot.last_bet_date <= AUCTIONS_EXTENSION:
            _endings[lot.id] = ending_unix + AUCTIONS_EXTENSION
            lot.end_date = _endings[lot.id]
            await update_lot_data(lot.id, end_date=lot.end_date)
            await edit_post(lot)
            return AUCTIONS_EXTENSION

    lot.moderation_status = LotStatusDB.ENDED.value

    group = await get_group(lot.group_id)
    user = await get_user(lot.user_id)
    has_commission = False
    if lot.last_bet and not user.loyal:
        has_commission = True
        lot.commission = max(
            lot.start_price * group.commission_percent // 100, group.commission_min
        )
    # else:
    #     lot.commission = group.commission_min

    await update_lot_data(
        lot.id, moderation_status=lot.moderation_status, commission=lot.commission
    )
    await send_notifications(lot, has_commission)


async def send_notifications(lot: Lot, has_commission: bool):
    if lot.last_bet:
        template = BETS["buyer_notification"]
        seller = await get_user(lot.user_id)
        if seller.rating <= MAX_RATING_TO_DANGER:
            template += "\n\n" + BETS["buyer_danger"]
        await _send_notification(
            "buyer",
            lot,
            template=template,
            link=lot.user_link,
            peer_id=lot.last_bettor_id,
            bet=lot.last_bet,
        )

    seller_kwargs = {}
    if lot.last_bet:
        seller_kwargs["link"] = lot.bettor_link
        seller_kwargs["bet"] = lot.last_bet
        if has_commission:
            seller_kwargs["commission"] = lot.commission
        else:
            seller_kwargs["template"] = BETS["seller_notification_no_commission"]
        seller_kwargs["kb"] = seller_notification_kb
    else:
        seller_kwargs["template"] = BETS["lot_failed"]
    await _send_notification("seller", lot, lot.user_id, **seller_kwargs)


async def _send_notification(
    recipient: str,
    lot: Lot,
    peer_id: int,
    kb: Optional[Keyboard] = None,
    template: Optional[str] = None,
    **template_kwargs,
):
    template = template or BETS[recipient + "_notification"]
    hl = group_post_hl(lot.group_id, lot.post_id, lot.description)
    text = template.format(lot=hl, **template_kwargs)
    api = get_api(lot.group_id)
    try:
        await api.messages.send(
            peer_id=peer_id, message=text, random_id=randint(10**7, 10**8), keyboard=kb
        )
    except VKAPIError[901]:
        logger.debug(f"Can't send message to user {peer_id}: no permission")
    # await state_dispenser.set(user_id, recipient + "_state", lot=lot)
