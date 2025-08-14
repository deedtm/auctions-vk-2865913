import time
from asyncio import sleep
from datetime import timedelta, datetime
from random import randint
from vkbottle import PhotoWallUploader
from config.vk import AUCTIONS_ENDING_TIME, POSTING_INTERVAL, GROUP_LOTS_LIMIT
from config.time import TZ
from database.lots.models import Lot
from database.lots.utils import (
    get_unsended_lots,
    update_lot_data,
    replace_moderation_status,
)
from database.groups.utils import (
    get_group,
    get_posts_amount,
    set_posts_amount,
    get_available_group,
    reset_all_posts_amount,
)
from database.users.utils import get_user
from enums.moderation import LotStatusDB
from templates import PUBLISH
from .config import user_api, apis, logger
from ..bot.config import api as bot_api, state_dispenser
from ..states_groups.publisher import PublisherStates
from ..hyperlinks import group_post_hl, group_link
from ..keyboards.publisher import overlimit_kb


async def reset_posts_amounts_wrapper():
    now = datetime.now(TZ)
    delta = (
        now.replace(day=now.day + 1, hour=0, minute=0, second=0, microsecond=0) - now
    )
    delay = delta.total_seconds()
    await sleep(delay)

    while True:
        try:
            await reset_all_posts_amount()
            await replace_moderation_status(
                LotStatusDB.WAITING_LIMIT.value, LotStatusDB.MODERATED.value
            )
            await sleep(86400)
        except Exception as e:
            logger.error(f"reset_posts_amounts_wrapper: {e.__class__.__name__}: {e}")
            return


async def post_wrapper():
    while True:
        try:
            await post_lots()
            await sleep(POSTING_INTERVAL)
        except Exception as e:
            logger.error(f"post_wrapper: {e.__class__.__name__}: {e}")
            return


async def post_lots():
    lots = await get_unsended_lots()
    if not lots:
        return

    lots = await filter_overlimited(lots)

    posted = []
    for lot in lots:
        await _post_lot(lot)
        posted.append(lot)


async def filter_overlimited(lots: list[Lot]):
    limits = {}
    overlimited = {}
    remove = []

    for lot in lots:
        if lot.group_id not in limits:
            limits[lot.group_id] = await get_posts_amount(lot.group_id)
        limits[lot.group_id] += 1

        if limits[lot.group_id] >= GROUP_LOTS_LIMIT:
            lot.moderation_status = LotStatusDB.OVERLIMITED.value
            await update_lot_data(lot=lot)

            if lot.user_id not in overlimited:
                overlimited[lot.user_id] = []
            overlimited[lot.user_id].append(lot)

            remove.append(lot)

    for group_id, amount in limits.items():
        await set_posts_amount(group_id, amount)

    for uid, lots in overlimited.items():
        await send_overlimited_notification(uid, lots)

    return list(filter(lambda x: x not in remove, lots))


async def send_overlimited_notification(user_id: int, lots: list[Lot]):
    available_group = await get_available_group(lots[0].group_id, GROUP_LOTS_LIMIT)
    with_other_group = bool(available_group)

    tmpl_raw = PUBLISH["overlimited"]
    tmpl = "\n\n".join([tmpl_raw[0], tmpl_raw[int(with_other_group) + 1]])

    args = [", ".join([lot.description for lot in lots])]
    if with_other_group:
        args.append(group_link(available_group.group_id))

    text = tmpl.format(*args)

    await bot_api.messages.send(
        peer_id=user_id,
        random_id=randint(10**6, 10**7),
        message=text,
        keyboard=overlimit_kb(with_other_group),
    )
    await state_dispenser.set(
        user_id,
        PublisherStates.OVERLIMITED_CHOICE,
        lots=lots,
        available_group=available_group,
    )


async def __upload_photos(lot: Lot, group_id: int):
    if not lot.photos_paths:
        return

    uploader = PhotoWallUploader(user_api)
    photos = []
    paths = lot.photos_paths.split(",")
    for path in paths:
        try:
            photo = await uploader.upload(path, group_id=-group_id)
            photos.append(photo)
        except Exception as e:
            print(f"Error uploading photo {path}: {e}")
            continue
        await sleep(0.5)  # To avoid hitting API limits

    return photos


async def _post_lot(lot: Lot):
    lot.publish_date = int(time.time())
    lot.end_date = get_end_date(lot.publish_date)
    attachments = await __upload_photos(lot, lot.group_id)
    user = await get_user(lot.user_id)
    urgent, main = await lot.as_post(user)
    group = await get_group(lot.group_id)
    additional_ind = group.auctions_template.find("{ADDITIONAL}")
    text = group.auctions_template[:additional_ind].format(URGENT=urgent, MAIN=main)

    if attachments:
        post = await user_api.wall.post(
            owner_id=lot.group_id,
            from_group=1,
            message=text,
            attachments=",".join(attachments),
        )
        await update_lot_data(
            lot.id,
            publish_date=lot.publish_date,
            end_date=lot.end_date,
            moderation_status=LotStatusDB.PUBLISHED.value,
            post_id=post.post_id,
            user_photos=",".join(attachments),
        )

        hl = group_post_hl(lot.group_id, post.post_id, lot.description)
        text = PUBLISH["published"].format(hl)
        await bot_api.messages.send(
            peer_id=lot.user_id, random_id=randint(10**6, 10**7), message=text
        )


def get_end_date(publish_date: float):
    publish_dt = datetime.fromtimestamp(publish_date, tz=TZ)
    end_dt = publish_dt.replace(
        hour=AUCTIONS_ENDING_TIME.hour,
        minute=AUCTIONS_ENDING_TIME.minute,
        second=0,
        microsecond=0,
    ) + timedelta(days=1)
    return int(end_dt.timestamp())
