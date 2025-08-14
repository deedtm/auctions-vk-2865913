from vkbottle.bot import Message

from config.admin import SET_ACCESS
from database.groups.models import Group as DBGroup
from database.groups.utils import (get_all_groups, get_group_by_id,
                                   update_group_data)
from templates import ADMIN_COMMANDS as ADMIN
from templates import ERRORS

from ....hyperlinks import group_hl
from ....keyboards.managegroups import main_menu_kb, templates_menu_kb
from ....states_groups import EmptySG, ManageGroupsSG
from ....types import MessageEvent, labeler
from ...config import state_dispenser
from ...rules import AccessFilter, CommandFilter
from .__utils import get_command

command_data = get_command("managegroups")
LITERALS = command_data["literals"]


async def is_group_id_valid(group_id: int) -> bool:
    groups = await get_all_groups()
    return any(g.id == group_id for g in groups)


async def check_ids(
    msg: Message, ids: list[int], return_single: bool = True
) -> list[int]:
    bad_ids = []
    for i in ids:
        if not i.isdigit():
            await msg.answer(ERRORS["not_int"])
            return False
        if not await is_group_id_valid(int(i)):
            await msg.answer(ERRORS["not_found"].format(i))
            bad_ids.append(i)

    if bad_ids:
        tmpl = ADMIN["managegroups"]["group_not_found"]
        await msg.answer(tmpl.format(", ".join(map(str, bad_ids))))
        return False

    output = [i for i in ids if i not in bad_ids]
    if len(output) == 1 and return_single:
        return output[0]
    return output


def groups_text(groups: list[DBGroup]) -> str:
    fmt = ADMIN["managegroups"]["group_fmt"]
    texts = []

    for g in groups:
        waterfalls = []
        if g.waterfalls:
            for g_id in g.waterfalls.split(","):
                g_id = int(g_id)
                waterfalling = list(filter(lambda x: x.group_id == g_id, groups))
                if waterfalling:
                    waterfalls.append(str(waterfalling[0].id))

        if not waterfalls:
            waterfalls = ["—"]
        text = fmt.format(
            id=g.id,
            name=group_hl(g.group_id, g.name),
            percent=g.commission_percent,
            min=g.commission_min,
            waterfalls=" ~ ".join(waterfalls),
        )
        texts.append(text)

    return "\n".join(texts)


@labeler.message(CommandFilter(LITERALS), AccessFilter(SET_ACCESS))
async def managegroups_handler(msg: Message):
    groups = await get_all_groups()
    tmpl = ADMIN["managegroups"]["main"]
    text = tmpl.format(groups_text(groups))
    await msg.answer(text, keyboard=main_menu_kb, dont_parse_links=True)


@labeler.callback_query({"managegroups": "set:waterfalls"})
async def set_waterfalls_callback(e: MessageEvent):
    text = ADMIN["managegroups"]["set_waterfalls"]
    await e.answer(text)
    await state_dispenser.set(
        e.object.peer_id,
        ManageGroupsSG.WATERFALLS,
    )


@labeler.message(state=ManageGroupsSG.WATERFALLS)
async def set_waterfalls_handler(msg: Message):
    ids = await check_ids(msg, msg.text.strip().split(), return_single=False)
    if not ids:
        return

    waterfalls = []
    if len(ids) > 1:
        for i in ids[1:]:
            group = await get_group_by_id(i)
            if not group:
                continue
            waterfalls.append(str(group.group_id))

    await update_group_data(id=ids[0], waterfalls=",".join(waterfalls))
    text = ADMIN["managegroups"]["waterfalls_set"]
    await msg.answer(text)

    await managegroups_handler(msg)


@labeler.callback_query({"managegroups": "set:commissions"})
async def set_commissions_callback(e: MessageEvent):
    text = ADMIN["managegroups"]["set_commissions"]
    await e.answer(text)
    await state_dispenser.set(
        e.object.peer_id,
        ManageGroupsSG.COMMISSIONS,
    )


@labeler.message(state=ManageGroupsSG.COMMISSIONS)
async def set_commissions_handler(msg: Message):
    args = msg.text.strip().split()
    if len(args) != 3:
        await msg.answer(ERRORS["not_enough_args"])
        return
    args[0] = await check_ids(msg, [args[0]])
    if not args[0]:
        return

    id, percent, minimum = map(int, args)
    await update_group_data(id=id, commission_percent=percent, commission_min=minimum)
    text = ADMIN["managegroups"]["commissions_set"]
    await msg.answer(text)

    await managegroups_handler(msg)


@labeler.callback_query({"managegroups": "set:auctions_template"})
async def templates_group_input_callback(e: MessageEvent):
    text = ADMIN["managegroups"]["auctions_templates"]["group_input"]
    await e.answer(text)
    await state_dispenser.set(
        e.object.peer_id,
        ManageGroupsSG.AT_GROUP,
    )


async def templates_menu(msg: Message, id: int):
    group = await get_group_by_id(id)

    tmpl = ADMIN["managegroups"]["auctions_templates"]["menu"]
    text = tmpl.format(group.auctions_template.replace("\\n", "\n"))
    await msg.answer(text, keyboard=templates_menu_kb)
    await state_dispenser.set(msg.peer_id, EmptySG.EMPTY, gid=id)


@labeler.message(state=ManageGroupsSG.AT_GROUP)
async def templates_menu_handler(msg: Message):
    id = msg.text.strip()
    id = await check_ids(msg, [id])
    if not id:
        return
    await templates_menu(msg, id)


@labeler.callback_query({"managegroups": "templates:edit"})
async def templates_edit(e: MessageEvent):
    input_text = ADMIN["managegroups"]["auctions_templates"]["template_input"]
    example_text = ADMIN["managegroups"]["auctions_templates"]["template_example"]
    await e.answer(input_text)
    await e.answer(example_text)

    sp = await state_dispenser.get(e.object.peer_id)
    await state_dispenser.set(e.object.peer_id, ManageGroupsSG.AT, **sp.payload)


def check_template(text: str) -> bool:
    has_urgent = "{URGENT}" in text
    has_main = "{MAIN}" in text
    has_additional = "{ADDITIONAL}" in text
    return has_urgent and has_main and has_additional


@labeler.message(state=ManageGroupsSG.AT)
async def templates_handler(msg: Message):
    if not check_template(msg.text):
        text = ADMIN["managegroups"]["auctions_templates"]["invalid_template"]
        await msg.answer(text)
        return

    sp = await state_dispenser.get(msg.peer_id)
    group_id = sp.payload.get("gid")

    await update_group_data(id=group_id, auctions_template=msg.text)
    await msg.answer(ADMIN["managegroups"]["auctions_templates"]["success"])
    await state_dispenser.delete(msg.peer_id)
    await templates_menu(msg, group_id)
