import os
from typing import Optional

import aiohttp
from vkbottle.bot import Message
from vkbottle_types.objects import MessagesMessageAttachment as Attachment

from config.vk import USER_LOTS_LIMIT
from database.lots.utils import add_lot, add_random_lots, get_lots_by_fields
from database.users.utils import get_user
from templates import COMMANDS, ERRORS
from types_.lot import Lot

from ...keyboards.auction import confirmation_kb, creation_methods_kb
from ...states_groups.auction import AuctionCreating
from ...types import MessageEvent, labeler
from ...utils import get_self_group
from ..config import state_dispenser
from ..rules.command import CommandFilter
from .__utils import get_command

__literals = get_command("auction")["literals"]


@labeler.message(CommandFilter(__literals))
async def auction_handler(msg: Message):
    group_data = await msg.ctx_api.groups.get_by_id()
    group_id = -group_data.groups[0].id

    lots = await get_lots_by_fields(
        group_id=group_id,
        user_id=msg.from_id,
    )

    if len(lots) >= USER_LOTS_LIMIT:
        template = COMMANDS["auction"]["overlimit"]
        text = template.format(USER_LOTS_LIMIT)
        await msg.answer(text)
        return

    await msg.answer(
        COMMANDS["auction"]["creation_methods"], keyboard=creation_methods_kb
    )


@labeler.callback_query({"auction": "cm:form"})
async def form_callback(event: MessageEvent):
    await event.edit_message(COMMANDS["auction"]["form"])
    await event.answer(COMMANDS["auction"]["form_example"])
    await state_dispenser.set(event.object.peer_id, AuctionCreating.FORM_INPUT)


async def save_photo(url: str, photo_id: int):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response.raise_for_status()
            data = await response.read()

    ext = url.split("?")[0].split(".")[-1]
    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)

    filepath = f"{temp_dir}/{photo_id}.{ext}"
    with open(filepath, "wb") as f:
        f.write(data)

    return filepath


async def get_attachments(msg: Message):
    history = await msg.ctx_api.messages.get_history(
        peer_id=msg.peer_id, count=200, extended=1
    )
    for m in history.items:
        if m.id == msg.id:
            attachments: list[Attachment] = m.attachments
            break
    photos = list(filter(lambda x: x.photo, attachments))
    paths = []
    for a in photos:
        url = a.photo.orig_photo.url
        filepath = await save_photo(url, a.photo.id)
        paths.append(filepath)

    return attachments, paths


async def check_ints(msg: Message, text: str, step: int, start_price: int = 0):
    try:
        num = int(text)
        if num < 0:
            return ERRORS["negative_value"]
        if step in (4, 5) and num < 10:
            return ERRORS["lower_than_minimum"]
        if step == 6 and num <= start_price and num != 0:
            return ERRORS["lower_than_start_price"]
    except ValueError:
        return ERRORS["not_int"]


@labeler.callback_query({"auction": "cm:poll"})
async def poll_callback(event: MessageEvent):
    step = 0
    max_step = len(COMMANDS["auction"]["poll"]) - 1

    await event.edit_message(COMMANDS["auction"]["poll"][step])
    await state_dispenser.set(
        event.object.peer_id,
        AuctionCreating.POLL_INPUT,
        form="",
        attachments=[],
        step=step + 1,
        max_step=max_step,
    )


@labeler.message(state=AuctionCreating.POLL_INPUT)
async def poll_handler(msg: Message):
    payload = msg.state_peer.payload

    lot_data = payload.get("lot_data", [])
    attachments = payload.get("attachments", [])
    photos_paths = payload.get("photos_paths", [])
    step = payload["step"]
    max_step = payload["max_step"]

    if step == 3:
        msg_attachments = msg.attachments
        if list(filter(lambda x: x.photo, msg_attachments)):
            attachments, photos_paths = await get_attachments(msg)
        else:
            await msg.answer(ERRORS["no_attachments"])
            return
    else:
        if step in (4, 5, 6, 9):
            args = [msg, msg.text, step, 0]
            if step == 6:
                args[-1] = int(lot_data[2])
            res = await check_ints(*args)
            if res:
                await msg.answer(res)
                return
        if msg.text:
            lot_data.append(msg.text)
        else:
            await msg.answer(COMMANDS["auction"]["poll_no_answer"])
            return

    if step > max_step:
        group = await get_self_group(msg.ctx_api)
        lot = Lot.from_poll(lot_data, attachments, photos_paths, group.id)
        await send_lot(msg, lot)
        return

    await msg.answer(COMMANDS["auction"]["poll"][step])
    payload["step"] = step + 1
    payload["lot_data"] = lot_data
    payload["attachments"] = attachments
    payload["photos_paths"] = photos_paths


async def get_form_lot(msg: Message):
    attachments, photos_paths = await get_attachments(msg)
    if not photos_paths:
        await msg.answer(ERRORS["no_attachments"])
        return

    text = msg.text
    lines = text.split("\n")

    results = []
    if not lines[2].isdigit():
        start_price = 0
        # results.append((3, ERRORS["not_int"]))
    else:
        start_price = int(lines[2])

    for step, line in enumerate(lines):
        step += 2
        if step in (4, 5, 6, 9):
            res = await check_ints(msg, line, step, start_price)
            if res:
                results.append((step - 1, res))
    if results:
        text = "\n".join(f"{res} в пункте {step}" for step, res in results)
        await msg.answer(text)
        return

    group = await get_self_group(msg.ctx_api)
    lot: Lot = Lot.from_form(text, attachments, photos_paths, group.id)

    return lot


@labeler.message(state=AuctionCreating.FORM_INPUT)
async def send_lot(msg: Message, lot: Optional[Lot] = None):
    if not lot:
        lot = await get_form_lot(msg)
        if not lot:
            return

    await state_dispenser.delete(msg.peer_id)

    text = COMMANDS["auction"]["confirmation"].format(lot)
    await msg.answer(
        text,
        attachment=lot.photos_as_attachments,
        keyboard=confirmation_kb,
    )
    await state_dispenser.set(msg.peer_id, AuctionCreating.CONFIRMATION, lot=lot)


@labeler.message(state=AuctionCreating.CONFIRMATION, text="✅ Подтвердить")
async def confirmed_handler(msg: Message):
    await add_lot(msg.from_id, msg.state_peer.payload["lot"])
    await msg.answer(COMMANDS["auction"]["confirmed"])


@labeler.message(lev="test_random")
async def random_handler(msg: Message):
    group = await msg.ctx_api.groups.get_by_id()
    group_id = -group.groups[0].id
    lot = (await add_random_lots(1, msg.from_id, group_id))[0]
    user = await get_user(lot.user_id)
    urgent, main = await lot.as_post(user)
    await msg.answer(
        COMMANDS["auction"]["random"].format("\n".join([urgent, main])),
        attachments=lot.photos,
    )
