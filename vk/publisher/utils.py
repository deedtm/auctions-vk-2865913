from vkbottle import API, PhotoWallUploader

from database.groups.utils import add_group, get_group
from database.lots.models import Lot
from database.users.utils import get_user

from ..bot.config import err_handler
from ..utils import get_self_group
from .config import apis, logger, user_api


async def init_groups():
    for api in apis:
        group = await get_self_group(api)
        if not await get_group(group.id):
            await add_group(group.id, group.name)


@err_handler.catch
async def edit_post(lot: Lot, **kwargs):
    user = await get_user(lot.user_id)
    urgent, main = await lot.as_post(user)
    group = await get_group(lot.group_id)
    additional_ind = group.auctions_template.find("{ADDITIONAL}")
    text = group.auctions_template[:additional_ind].format(URGENT=urgent, MAIN=main)
    await user_api.wall.edit(
        owner_id=lot.group_id,
        post_id=lot.post_id,
        message=text,
        attachments=lot.user_photos,
        **kwargs,
    )


async def upload_photo(path: str, group_id: int, api: API = user_api):
    uploader = PhotoWallUploader(api)
    try:
        return await uploader.upload(path, group_id=abs(group_id))
    except Exception as e:
        logger.warning(f"Error uploading photo {path}: {e}")
