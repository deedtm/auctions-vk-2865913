import re
from database.lots.utils import get_all_lots

ID_PATTERN = re.compile(r"\d+_\d+")


async def get_lots_by_ids(ids: list[str]) -> list:
    ids = re.findall(ID_PATTERN, " ".join(ids))
    vk_ids = {}
    for vk_id in ids:
        group_id, post_id = list(map(int, vk_id.split("_")))
        group_id = -group_id
        if post_id not in vk_ids.get(group_id, []):
            vk_ids.setdefault(group_id, []).append(post_id)

    return await get_all_lots(vk_ids=vk_ids)
