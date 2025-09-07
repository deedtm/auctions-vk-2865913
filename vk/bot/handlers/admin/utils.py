import re

from database.lots.utils import get_all_lots_by_ids

ID_PATTERN = re.compile(r"\d+_\d+")


async def get_lots_by_ids(ids: list[str]) -> list:
    vk_ids = re.findall(ID_PATTERN, " ".join(ids))
    vk_group_ids = {}
    for vk_id in vk_ids:
        group_id, post_id = list(map(int, vk_id.split("_")))
        group_id = -group_id
        if post_id not in vk_group_ids.get(group_id, []):
            vk_group_ids.setdefault(group_id, []).append(post_id)

    db_ids = list(map(int, filter(lambda x: "_" not in x, ids)))

    lots = await get_all_lots_by_ids(db_ids=db_ids, vk_ids=vk_group_ids)
    return lots
