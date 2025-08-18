from asyncio import sleep
from datetime import datetime

from config.time import TZ
from config.vk import COLLECTOR_NOTIFICATIONS_TIME as COLLECTOR_TIME
from config.vk import COLLECTOR_REMINDER
from config.vk import LAST_COLLECTOR_REMINDER as LAST_REMINDER
from database.lots.models import Lot
from database.lots.utils import get_lots_with_commissions
from templates import COLLECTOR

from ...hyperlinks import group_post_hl
from ..config import logger
from .utils import send_notification
from ...keyboards.bets import seller_notification_kb

DEFAULT_DELAY = 86400


async def collector_wrapper():
    now = datetime.now(TZ)
    notification_seconds = COLLECTOR_TIME.hour * 3600 + COLLECTOR_TIME.minute * 60
    delay = DEFAULT_DELAY - (now.hour * 3600 + now.minute * 60 + now.second) + notification_seconds
    await sleep(delay)

    while True:
        try:
            await collector_notificate()
            await sleep(DEFAULT_DELAY)
        except Exception as e:
            logger.error(f"collector_wrapper: {e.__class__.__name__}: {e}")
            return


async def filter_reminders(lots: list[Lot]):
    now = datetime.now(TZ)
    user_reminders: dict[int, dict[int, list[Lot]]] = {}
    for lot in lots:
        end_dt = datetime.fromtimestamp(lot.end_date, TZ)
        days_passed = (now - end_dt).days
        for d in COLLECTOR_REMINDER:
            if d == days_passed:
                user_data = user_reminders.setdefault(lot.user_id, {})
                user_data.setdefault(days_passed, []).append(lot)

    return user_reminders


async def collector_notificate():
    lots = await get_lots_with_commissions()
    if not lots:
        return

    lots = list(sorted(lots, key=lambda x: x.user_id))
    lots = await filter_reminders(lots)

    notified = []
    for user_id, overdue_data in lots.items():
        await _send_notification(user_id, overdue_data)
        notified.append(user_id)
        await sleep(1)


async def lots_text(overdue_data: dict[int, list[Lot]]):
    output, total_sum = [], 0
    for days, lots in overdue_data.items():
        names, sm = [], 0
        for l in lots:
            names.append(group_post_hl(l.group_id, l.post_id, l.description))
            sm += l.commission
        total_sum += sm
        args = [", ".join(names), sm, days]

        tmpl_key = "lot"
        emoji = COLLECTOR["emojis"]["lot"]
        if days == LAST_REMINDER:
            tmpl_key += "_last"
            emoji = COLLECTOR["emojis"]["last"]
            args.pop()
        args.insert(0, emoji)
        template = COLLECTOR[tmpl_key]
        output.append(template.format(*args))
    return output, total_sum


async def get_notification_text(overdue_data: dict[int, list[Lot]]):
    text_lots, total_sum = await lots_text(overdue_data)

    start_emojis = COLLECTOR["emojis"]["start"] * len(text_lots)
    text_start = COLLECTOR["start"].format(start_emojis, total_sum)

    tmpl_info_key, args = "info", [LAST_REMINDER - min(overdue_data)]
    if any([d >= LAST_REMINDER for d in overdue_data]):
        tmpl_info_key += "_last"
        args.pop()
    text_info = COLLECTOR[tmpl_info_key].format(*args)

    return "\n\n".join([text_start, "\n".join(text_lots), text_info])


async def _send_notification(user_id: int, overdue_data: dict[int, list[Lot]]):
    text = await get_notification_text(overdue_data)
    group_id = list(overdue_data.values())[0][0].group_id
    await send_notification(group_id, user_id, text, keyboard=seller_notification_kb)
