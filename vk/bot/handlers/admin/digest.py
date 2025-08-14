import os
from asyncio import sleep
from os import path as p
from typing import Optional

import aiohttp
from vkbottle.bot import Message
from vkbottle_types.objects import MessagesMessageAttachment as Attachment
from vkbottle_types.objects import PhotosPhoto as Photo

from config.admin import SET_ACCESS
from templates import ADMIN_COMMANDS as ADMIN
from templates import ERRORS

from ....keyboards.digest import main_menu_kb
from ....publisher.digest.utils import BASE_PATH as DIGEST_PATHS
from ....publisher.digest.utils import (CACHE_PATH, cache_pic_for_all_groups,
                                        get_cached_pic, get_settings,
                                        save_settings)
from ....states_groups.digest import DigestSG
from ....types import MessageEvent, labeler
from ....utils import get_self_group
from ...config import state_dispenser
from ...rules import AccessFilter, CommandFilter
from .__utils import get_command

command_data = get_command("digest")
LITERALS = command_data["literals"]


@labeler.message(CommandFilter(LITERALS), AccessFilter(SET_ACCESS))
async def digest_menu(msg: Message):
    settings = get_settings()
    tmpl = ADMIN["digest"]["menu"]
    text = tmpl.format(["нет", "да"][int(settings["to_pin"])])

    attachments = await get_cached_pic(filename="ADMIN")
    kwargs = {"message": text, "keyboard": main_menu_kb, "attachment": attachments}
    await msg.answer(**kwargs)


@labeler.callback_query({"digest": "edit_pin"})
async def reverse_pin(e: MessageEvent):
    settings = get_settings()
    settings["to_pin"] = not settings["to_pin"]
    save_settings(settings)

    tmpl = ADMIN["digest"]["menu"]
    text = tmpl.format(["нет", "да"][int(settings["to_pin"])])

    attachments = await get_cached_pic(filename="ADMIN")
    kwargs = {"text": text, "keyboard": main_menu_kb, "attachment": attachments}
    await e.edit_message(**kwargs)


@labeler.callback_query({"digest": "edit_pic"})
async def edit_pic_handler(e: MessageEvent):
    text = ADMIN["digest"]["photo_input"]
    await e.edit_message(text)
    await state_dispenser.set(e.object.peer_id, DigestSG.PHOTO_INPUT)


async def save_photo(url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response.raise_for_status()
            data = await response.read()

    ext = url.split("?")[0].split(".")[-1]
    filename = f"digestpic.{ext}"

    filepath = os.path.join(DIGEST_PATHS, filename)
    with open(filepath, "wb") as f:
        f.write(data)

    return filename


async def get_attachments(msg: Message):
    history = await msg.ctx_api.messages.get_history(
        peer_id=msg.peer_id, count=200, extended=1
    )
    for m in history.items:
        if m.id == msg.id:
            attachments: list[Attachment] = m.attachments
            break
    return attachments


@labeler.message(state=DigestSG.PHOTO_INPUT)
async def photo_input_handler(msg: Message):
    photos: list[Photo] = msg.get_photo_attachments()
    if not photos:
        text = ERRORS["no_attachments"]
        await msg.answer(text)
        return

    sizes = photos[0].sizes
    mx_height, mx_width, obj = sizes[0].height, sizes[0].width, sizes[0]
    for s in sizes:
        if s.height > mx_height or s.width > mx_width:
            mx_height, mx_width, obj = s.height, s.width, s
    photo_url = s.url
    filename = await save_photo(photo_url)

    settings = get_settings()
    settings["picture_filename"] = filename
    save_settings(settings)

    await cache_pic_for_all_groups()

    ph = (await get_attachments(msg))[0].photo
    attachment_str = f"photo{ph.owner_id}_{ph.id}"
    if ph.access_key:
        attachment_str += f"_{ph.access_key}"

    path = p.join(CACHE_PATH, "ADMIN")
    with open(path, "w") as f:
        f.write(attachment_str)

    text = ADMIN["digest"]["photo_success"]
    await msg.answer(text)
    await sleep(1)
    await digest_menu(msg)
