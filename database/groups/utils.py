from ..constants import DATETIME_FORMAT
from ..log import logger
from config.time import TZ
from datetime import datetime
from html import escape
from ..connect import init_db, get_session, Base
from ..groups.models import Group as DBGroup
from sqlalchemy import select, func
from sqlalchemy import update as sqlalchemy_update, delete as sqlalchemy_delete
import random
import string


async def get_all_groups(count: int = -1, start_id: int = 0) -> list[DBGroup]:
    """Return a list of `count` groups starting from groups with id >= `start_id`."""
    async for session in get_session():
        stmt = select(DBGroup)
        stmt = stmt.where(DBGroup.id >= start_id)
        stmt = stmt.order_by(DBGroup.id)
        if count != -1:
            stmt = stmt.limit(count)
        result = await session.execute(stmt)
        return result.scalars().all()
    return []


async def get_group(
    group_id: int | None = None,
) -> DBGroup | list[DBGroup] | None:
    """Fetch a group by group_id."""
    async for session in get_session():
        if group_id is not None:
            stmt = select(DBGroup).where(DBGroup.group_id == group_id)
            return await session.scalar(stmt)
    return None


async def get_group_by_id(id: int) -> DBGroup | None:
    """Fetch a group by its database id."""
    async for session in get_session():
        stmt = select(DBGroup).where(DBGroup.id == id)
        return await session.scalar(stmt)
    return None


async def add_group(
    group_id: int, name: str, posts_amount: int = 0, waterfalls: str | None = None
) -> DBGroup:
    """Add a new group to the database"""
    async for session in get_session():
        new_group = DBGroup(
            group_id=group_id,
            name=escape(name),
            posts_amount=posts_amount,
            waterfalls=waterfalls,
        )
        session.add(new_group)
        await session.commit()
        await session.refresh(new_group)
        logger.debug(f"Group {group_id} added as ORM record")
        return new_group


async def get_group_data(
    group_id: int | None = None,
) -> dict | list[dict] | None:
    """Return all group data as a dict, a list of dicts, or None if not found"""
    group = await get_group(group_id)
    if not group:
        return None

    def to_dict(g: DBGroup) -> dict:
        return {
            "id": g.id,
            "group_id": g.group_id,
            "posts_amount": g.posts_amount,
            "waterfalls": g.waterfalls,
        }

    if isinstance(group, list):
        return [to_dict(g) for g in group]

    return to_dict(group)


async def get_posts_amount(group_id: int) -> int | None:
    """Return the group's posts_amount or None"""
    group = await get_group(group_id)
    return group.posts_amount if group else None


async def get_waterfalls(group_id: int) -> list[int] | None:
    """Return the group's waterfalls field or None"""
    group = await get_group(group_id)
    if group and group.waterfalls:
        return list(map(int, group.waterfalls.split(",")))


async def get_available_group(group_id: int, posts_limit: int) -> DBGroup | None:
    """Return a group from waterfall if its posts_amount is less than posts_limit"""
    waterfalls = await get_waterfalls(group_id)
    if not waterfalls:
        return

    for id in waterfalls:
        group = await get_group(id)
        if group.posts_amount < posts_limit:
            return group

    return


async def update_group_data(group_id: int | None = None, id: int | None = None, **fields) -> bool:
    """Update group fields by database id or by group_id, return True if updated."""
    if group_id is None and id is None:
        return False
    async for session in get_session():
        stmt = sqlalchemy_update(DBGroup).values(**fields)
        if id is not None:
            stmt = stmt.where(DBGroup.id == id)
        else:
            stmt = stmt.where(DBGroup.group_id == group_id)
        result = await session.execute(stmt)
        if result.rowcount:
            await session.commit()
            key = "id" if id is not None else "group_id"
            val = id if id is not None else group_id
            logger.debug(f"Group updated by {key}={val}, fields={list(fields.keys())}")
            return True
        return False


async def set_posts_amount(group_id: int, posts_amount: int) -> bool:
    """Set the group's posts_amount"""
    return await update_group_data(group_id, posts_amount=posts_amount)


async def set_waterfalls(group_id: int, waterfalls: str | None) -> bool:
    """Set the group's waterfalls field"""
    return await update_group_data(group_id, waterfalls=waterfalls)


async def reset_all_posts_amount() -> int:
    """Set posts_amount to 0 for all groups. Returns number of groups updated."""
    async for session in get_session():
        result = await session.execute(
            sqlalchemy_update(DBGroup).values(posts_amount=0)
        )
        if result.rowcount:
            await session.commit()
            logger.debug(f"Reset posts_amount to 0 for {result.rowcount} groups")
            return result.rowcount
        return 0


async def delete_group(group_id: int) -> bool:
    """Delete a group by group_id, return True if deleted, False otherwise"""
    async for session in get_session():
        result = await session.execute(
            sqlalchemy_delete(DBGroup).where(DBGroup.group_id == group_id)
        )
        if result.rowcount:
            await session.commit()
            logger.debug(f"Group {group_id} deleted")
            return True
        return False


async def add_random_groups(count: int) -> list[DBGroup]:
    """Add specified number of randomly generated groups to the database."""
    groups: list[DBGroup] = []
    async for session in get_session():
        for _ in range(count):
            group_id = random.randint(100000000, 999999999)
            posts_amount = random.randint(0, 100)
            waterfalls = "".join(
                random.choices(string.ascii_letters + string.digits, k=10)
            )
            new_group = DBGroup(
                group_id=group_id,
                posts_amount=posts_amount,
                waterfalls=waterfalls,
            )
            session.add(new_group)
            groups.append(new_group)
        await session.commit()
        for g in groups:
            await session.refresh(g)
        return groups
    return groups


async def get_last_group_id() -> int | None:
    """Return the id of the last (highest id) group in the database, or None if no groups."""
    async for session in get_session():
        stmt = select(DBGroup.id).order_by(DBGroup.id.desc()).limit(1)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
    return None
