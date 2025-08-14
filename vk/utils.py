from vkbottle import API
from vkbottle_types.codegen.objects import GroupsGroupFull, UsersUserFull

from log import get_logger

logger = get_logger(__name__)


async def get_self_group(api: API, negative_id: bool = True) -> GroupsGroupFull:
    res = await api.groups.get_by_id()
    data = res.groups[0].__dict__
    data["id"] *= (-1 * int(negative_id)) or 1
    return GroupsGroupFull(**data)


def check_vk_link(link: str) -> bool:
    return link.startswith(("https://vk.com/", "vk.com/"))


async def get_users_from_links(
    api: API, links: str | list[str], **api_kwargs
) -> UsersUserFull | list[UsersUserFull]:
    if isinstance(links, str):
        links = [links]

    links_ = links.copy()
    links = list(filter(check_vk_link, links))
    if not links:
        raise ValueError("Invalid VK user links format.")
    skipped = set(links_) - set(links)
    if skipped:
        logger.debug(f"Skipped invalid links: {', '.join(skipped)}")

    users_ids = []
    for link in links:
        user_id = link.split("/", 3)[-1]
        if user_id.startswith("id"):
            user_id = link.split("id")[-1]
        users_ids.append(user_id)

    users = await api.users.get(user_ids=",".join(users_ids), **api_kwargs)
    if len(users) == 1:
        return users[0]
    return users


async def get_groups_from_links(
    api: API, links: str | list[str]
) -> GroupsGroupFull | list[GroupsGroupFull]:
    if isinstance(links, str):
        links = [links]

    links_ = links.copy()
    links = list(filter(check_vk_link, links))
    if not links:
        raise ValueError("Invalid VK group links format.")
    skipped = set(links_) - set(links)
    if skipped:
        logger.debug(f"Skipped invalid links: {', '.join(skipped)}")

    groups_ids = []
    for link in links:
        group_id = link.split("/", 3)[-1]
        if group_id.startswith("club"):
            group_id = int(link.split("club")[-1])
        elif group_id.startswith("public"):
            group_id = int(link.split("public")[-1])
        groups_ids.append(group_id)

    groups = await api.groups.get_by_id(group_ids=",".join(map(str, groups_ids)))
    groups = groups.groups

    if len(groups) == 1:
        return groups[0]
    return groups
