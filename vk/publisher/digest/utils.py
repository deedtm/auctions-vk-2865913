import json
import os
from os import path as p
from typing import Optional

from vkbottle import API

from ..config import apis, user_api
from ..utils import get_self_group, upload_photo

BASE_PATH = "vk/publisher/digest/"
CACHE_PATH = p.join(BASE_PATH, "cache")


def get_settings():
    path = p.join(BASE_PATH, "settings.json")
    with open(path) as f:
        settings = json.load(f)
    return settings


def save_settings(new_settings: dict):
    path = p.join(BASE_PATH, "settings.json")
    with open(path, "w") as f:
        json.dump(new_settings, f)


async def get_cached_pic(
    group_id: Optional[int] = None, filename: Optional[str] = None
):
    fn = filename or str(group_id)
    if not fn in os.listdir(CACHE_PATH):
        return

    path = p.join(CACHE_PATH, fn)
    with open(path) as f:
        content = f.read()
    return content


async def cache_pic(
    group_id: int,
    force: bool = False,
    uploader_api: API = user_api,
    filename: Optional[str] = None,
):
    if not force and await get_cached_pic(group_id):
        return

    PIC_PATH = p.join(BASE_PATH, get_settings()["picture_filename"])
    pic = await upload_photo(PIC_PATH, group_id, uploader_api)
    path = p.join(CACHE_PATH, filename or str(group_id))
    with open(path, "w") as f:
        f.write(pic)


async def cache_pic_for_all_groups():
    groups = []
    for api in apis:
        group = await get_self_group(api, False)
        await cache_pic(group.id, True)
        groups.append(group)
    return groups
