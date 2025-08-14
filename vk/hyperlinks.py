VK_LINK = "https://vk.com/"


def user_link(user_id: int):
    return VK_LINK + f"id{user_id}"


def group_link(group_id: int):
    return VK_LINK + f"club{abs(group_id)}"


def post_link(link: str, owner_id: int, post_id: int):
    return link + f"?w=wall{owner_id}_{post_id}"


def hyperlink(link: str, text: str):
    """!!! WORKS ONLY WITH vk.com LINKS !!!"""
    return f"[{link}|{text}]"


def user_hl(user_id: int, text: str):
    l = user_link(user_id)
    return hyperlink(l, text)


def group_hl(group_id: int, text: str):
    l = group_link(group_id)
    return hyperlink(l, text)


def group_post_hl(group_id: int, post_id: int, text: str):
    l = group_link(group_id)
    pl = post_link(l, group_id, post_id)
    return hyperlink(pl, text)
