import os
from asyncio import sleep
from json import JSONDecodeError
from random import uniform

from vkbottle import API, PhotoWallUploader, VKAPIError

from config.admin import (ADMIN_ACCESS, ADMINS_IDS, MODERATOR_ACCESS,
                          MODERATORS_IDS)
from database.groups.utils import add_group, get_group
from database.lots.models import Lot
from database.lots.utils import get_lots_by_fields, update_lot_data
from database.users.utils import get_user, update_user_data
from enums.editing_responses import EditingResponses as ER
from enums.moderation import LotStatusDB

from ..bot.config import err_handler, logger
from ..utils import get_self_group
from .config import apis, groups_apis, logger, user_api


async def init_groups():
    global groups_apis

    for api in apis:
        group = await get_self_group(api)
        dbgroup = await get_group(group.id)
        if not dbgroup:
            dbgroup = await add_group(group.id, group.name)
        groups_apis[str(abs(group.id))] = api
    logger.debug(
        f'Initialized {len(groups_apis)} groups APIs: {", ".join(groups_apis.keys())}'
    )


async def _init_access(ids: list[int], level: int):
    good_ids = []
    for i in ids:
        r = await update_user_data(i, access_level=level)
        if r:
            good_ids.append(str(i))

    logger.debug(
        f'Initialized {len(good_ids)} users\' access level as {level}: {", ".join(good_ids)}'
    )
    return good_ids


async def init_accesses():
    await _init_access(MODERATORS_IDS, MODERATOR_ACCESS)
    await _init_access(ADMINS_IDS, ADMIN_ACCESS)


def get_api(group_id: int):
    return groups_apis.get(str(abs(group_id)), None)


@err_handler.catch
async def edit_post(lot: Lot, **kwargs):
    user = await get_user(lot.user_id)
    urgent, main = await lot.as_post(user)
    group = await get_group(lot.group_id)
    additional_ind = group.auctions_template.find("{ADDITIONAL}")
    text = group.auctions_template[:additional_ind].format(URGENT=urgent, MAIN=main)
    try:
        await user_api.wall.edit(
            owner_id=lot.group_id,
            post_id=lot.post_id,
            message=text,
            attachments=lot.user_photos,
            **kwargs,
        )
    except VKAPIError as e:
        if e.code != 15:
            raise e
        logger.debug(f"Closing lot {lot.id} because post deleted")
        await update_lot_data(lot.id, moderation_status=LotStatusDB.CLOSED.value)
        return ER.DELETED_POST
    return ER.SUCCESS


async def sleep_random(min_time: int = 5, max_time: int = 10):
    waiting = uniform(min_time, max_time)
    logger.debug(f"Sleeping {waiting:.2f} seconds and retrying to upload")
    await sleep(waiting)
    return waiting


async def upload_photo(
    path: str,
    group_id: int,
    api: API = user_api,
    uploader: PhotoWallUploader = None,
    try_: int = 1,
    err: Exception = None,
):
    assert api or uploader, "`api` or `uploader` must been provided"

    if try_ > 5:
        logger.error(f"Exceeded limit of tries while uploading {path}: {group_id=}")
        if isinstance(err, Exception):
            raise err

    if uploader is None:
        uploader = PhotoWallUploader(api)
    try:
        res = await uploader.upload(path, group_id=abs(group_id))
        if res:
            logger.debug(f"Uploaded {path}: {res}")
            return res
        logger.debug(f"Got `None` result while trying to upload {path}")
    except VKAPIError as e:
        logger.error(
            f"[{e.code}] VK API Error while trying to upload {path}: {group_id=}; {e=}"
        )
        await sleep_random()
        return await upload_photo(path, group_id, api, uploader, try_ + 1, e)
    except JSONDecodeError as e:
        logger.error(
            f"JSON Decode Error while trying to upload {path}: {group_id=}; {e=}"
        )
        await sleep_random()
        return await upload_photo(path, group_id, api, uploader, try_ + 1, e)
    except Exception as e:
        logger.warning(f"Error uploading photo {path}: {e}")
        return e


async def remove_excessive_photos():
    
    # lots = await get_lots_by_fields(moderation_status=LotStatusDB.CLOSED.value)
    # lots.extend(
    #     await get_lots_by_fields(
    #         moderations_status=LotStatusDB.FAILED_USER_PHOTO_UPLOAD.value
    #     )
    # )
    # if not lots:
    #     return

    # removed_paths = []
    # for l in lots:
    #     paths = l.photos_paths.split(",")
    #     for p in paths:
    #         try:
    #             os.remove(p)
    #             removed_paths.append(p)
    #         except FileNotFoundError:
    #             pass
            
    # return removed_paths, lots
