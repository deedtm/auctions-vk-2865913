import random
import time
from html import escape

from sqlalchemy import delete as sqlalchemy_delete
from sqlalchemy import or_, select
from sqlalchemy import update as sqlalchemy_update

from enums.moderation import LotStatusDB
from types_.lot import Lot

from ..connect import get_session
from ..log import logger
from ..lots.models import Lot as DBLot


async def get_all_lots(vk_ids: dict[int, list[int]] | None = None) -> list[DBLot]:
    """
    Return all lots if no vk_ids provided.
    If vk_ids is given (mapping group_id to list of post_ids),
    return lots matching any (group_id == key AND post_id IN values) pair.
    """
    async for session in get_session():
        stmt = select(DBLot)
        if vk_ids:
            conditions = []
            for group_id, post_ids in vk_ids.items():
                if post_ids:
                    conditions.append(
                        (DBLot.group_id == group_id) & DBLot.post_id.in_(post_ids)
                    )
                else:
                    conditions.append(DBLot.group_id == group_id)
            stmt = stmt.where(or_(*conditions))
        result = await session.execute(stmt)
        return result.scalars().all()
    return []


async def get_lots_by_fields(**fields) -> list[DBLot]:
    """
    Return all lots matching the specified field values
    """
    if not fields:
        return []
    async for session in get_session():
        stmt = select(DBLot)
        for key, value in fields.items():
            if hasattr(DBLot, key):
                stmt = stmt.where(getattr(DBLot, key) == value)
        result = await session.execute(stmt)
        return result.scalars().all()
    return []


async def get_lots_ended_before(end_date: int, **fields) -> list[DBLot]:
    """Return all lots with end_date less than or equal to the specified value and matching additional field filters."""
    async for session in get_session():
        stmt = select(DBLot).where(DBLot.end_date <= end_date)
        for key, value in fields.items():
            if hasattr(DBLot, key):
                stmt = stmt.where(getattr(DBLot, key) == value)
        result = await session.execute(stmt)
        return result.scalars().all()
    return []


async def get_lots_with_commissions(
    user_id: int | None = None, end_date: int | None = None
) -> list[DBLot]:
    """Return all lots with non-zero commission, optionally filtered by user_id and end_date."""
    async for session in get_session():
        stmt = select(DBLot).where(
            DBLot.commission.isnot(None),
            DBLot.commission != 0,
        )
        if user_id is not None:
            stmt = stmt.where(DBLot.user_id == user_id)
        if end_date is not None:
            stmt = stmt.where(DBLot.end_date <= end_date)
        result = await session.execute(stmt)
        return result.scalars().all()
    return []


async def get_lot(
    lot_id: int | None = None,
    user_id: int | None = None,
    group_id: int | None = None,
    post_id: int | None = None,
) -> DBLot | list[DBLot] | None:
    """Fetch a lot by lot_id, all lots by user_id, or all lots with a given description."""
    async for session in get_session():
        if group_id is not None and post_id is not None:
            stmt = select(DBLot).where(
                DBLot.group_id == group_id, DBLot.post_id == post_id
            )
            return await session.scalar(stmt)
        elif group_id is not None:
            stmt = select(DBLot).where(DBLot.group_id == group_id)
            result = await session.execute(stmt)
            return result.scalars().all()
        if user_id is not None:
            stmt = select(DBLot).where(DBLot.user_id == user_id)
            result = await session.execute(stmt)
            return result.scalars().all()
        if lot_id is not None:
            stmt = select(DBLot).where(DBLot.id == lot_id)
            return await session.scalar(stmt)
    return None


async def get_pending_lots() -> list[DBLot]:
    """Return all lots that are pending moderation."""
    async for session in get_session():
        stmt = select(DBLot).where(DBLot.moderation_status == LotStatusDB.PENDING.value)
        result = await session.execute(stmt)
        return result.scalars().all()
    return []


async def get_unsended_lots(group_id: int | None = None) -> list[DBLot]:
    """Return all lots that have not been sent to users."""
    async for session in get_session():
        if group_id is None:
            stmt = select(DBLot).where(
                DBLot.moderation_status == LotStatusDB.MODERATED.value
            )
        else:
            stmt = select(DBLot).where(
                DBLot.moderation_status == LotStatusDB.MODERATED.value,
                DBLot.group_id == group_id,
            )
        result = await session.execute(stmt)
        return result.scalars().all()
    return []


async def get_ended_lots() -> list[DBLot]:
    """Return all lots that have ended."""
    async for session in get_session():
        now = int(time.time())
        is_ended = DBLot.moderation_status == LotStatusDB.ENDED.value
        is_closed = DBLot.moderation_status == LotStatusDB.CLOSED.value
        is_outdated = DBLot.end_date < now
        is_redeemed = DBLot.moderation_status == LotStatusDB.REDEEMED.value
        stmt = select(DBLot).where(~(is_ended | is_closed) & (is_outdated | is_redeemed))
        result = await session.execute(stmt)
        return result.scalars().all()
    return []


async def add_lot(user_id: int, lot: Lot) -> DBLot:
    """Add a new lot to the database from a Lot object"""
    async for session in get_session():
        # Convert photos list to comma-separated string for database storage
        photos_str = ",".join(lot.photos) if lot.photos else None
        photos_paths_str = ",".join(lot.photos_paths) if lot.photos_paths else None

        new_lot = DBLot(
            user_id=user_id,
            group_id=lot.group_id,
            description=lot.description,
            condition=lot.condition,
            photos=photos_str,
            photos_paths=photos_paths_str,
            start_price=lot.start_price,
            step_price=lot.step_price,
            payment_method=lot.payment_method,
            city=lot.city,
            redemption_price=lot.redemption_price,
            delivery_price=lot.delivery_price,
        )
        session.add(new_lot)
        await session.commit()
        await session.refresh(new_lot)
        logger.debug(f"Lot {new_lot.id} added as ORM record")
        return new_lot


async def get_lot_data(
    lot_id: int | None = None,
    user_id: int | None = None,
    description: str | None = None,
) -> dict | list[dict] | None:
    """Return all lot data as a dict, a list of dicts, or None if not found"""
    lots = await get_lot(lot_id, user_id, description)
    if not lots:
        return None

    def to_dict(lot: DBLot) -> dict:
        return {
            "id": lot.id,
            "user_id": lot.user_id,
            "description": lot.description,
            "condition": lot.condition,
            "photos": lot.photos,
            "start_price": lot.start_price,
            "step_price": lot.step_price,
            "payment_method": lot.payment_method,
            "city": lot.city,
            "redemption_price": lot.redemption_price,
            "delivery_price": lot.delivery_price,
        }

    if isinstance(lots, list):
        return [to_dict(lot) for lot in lots]

    return to_dict(lots)


async def get_lot_description(lot_id: int) -> str | None:
    """Return the lot's description or None"""
    lot = await get_lot(lot_id)
    return lot.description if lot else None


async def get_lot_condition(lot_id: int) -> str | None:
    """Return the lot's condition or None"""
    lot = await get_lot(lot_id)
    return lot.condition if lot else None


async def get_lot_photos(lot_id: int) -> str | None:
    """Return the lot's photos or None"""
    lot = await get_lot(lot_id)
    return lot.photos if lot else None


async def get_lot_start_price(lot_id: int) -> int | None:
    """Return the lot's start price or None"""
    lot = await get_lot(lot_id)
    return lot.start_price if lot else None


async def get_lot_step_price(lot_id: int) -> int | None:
    """Return the lot's step price or None"""
    lot = await get_lot(lot_id)
    return lot.step_price if lot else None


async def get_lot_payment_method(lot_id: int) -> str | None:
    """Return the lot's payment method or None"""
    lot = await get_lot(lot_id)
    return lot.payment_method if lot else None


async def get_lot_city(lot_id: int) -> str | None:
    """Return the lot's city or None"""
    lot = await get_lot(lot_id)
    return lot.city if lot else None


async def get_lot_redemption_price(lot_id: int) -> int | None:
    """Return the lot's redemption price or None"""
    lot = await get_lot(lot_id)
    return lot.redemption_price if lot else None


async def get_lot_delivery_price(lot_id: int) -> int | None:
    """Return the lot's delivery price or None"""
    lot = await get_lot(lot_id)
    return lot.delivery_price if lot else None


async def get_lot_user_id(lot_id: int) -> int | None:
    """Return the lot's user_id or None"""
    lot = await get_lot(lot_id)
    return lot.user_id if lot else None


async def is_lot_sended(lot_id: int) -> bool:
    """Check if the lot has not been sent to users"""
    lot = await get_lot(lot_id)
    if (
        lot
        and lot.moderation_status == LotStatusDB.PENDING.value
        and lot.moderation_result is not None
    ):
        return False
    return True


async def is_ongoing_auction(group_id: int, post_id: int) -> bool:
    """Check if the auction is ongoing"""
    lot = await get_lot(group_id=group_id, post_id=post_id)
    if not lot or lot.end_date < int(time.time()):
        return False
    return True


async def update_lot_data(lot_id: int = None, lot: DBLot = None, **fields) -> bool:
    """
    Update lot fields, return True if updated, False if lot not found.
    You must provide either lot_id or lot (DBLot instance).
    If lot is provided, all its fields will be used for update.
    """
    if lot is None and lot_id is None:
        raise ValueError("Either lot_id or lot must be provided")

    if lot is not None:
        lot_id = lot.id
        # Extract all fields except SQLAlchemy internals and id
        fields = {
            key: getattr(lot, key)
            for key in lot.__table__.columns.keys()
            if key != "id"
        }

    async for session in get_session():
        result = await session.execute(
            sqlalchemy_update(DBLot).where(DBLot.id == lot_id).values(**fields)
        )
        if result.rowcount:
            await session.commit()
            logger.debug(f"Lot {lot_id} updated fields {list(fields.keys())}")
            return True
        return False


async def set_lot_description(lot_id: int, description: str) -> bool:
    """Set the lot's description"""
    return await update_lot_data(lot_id, description=description)


async def set_lot_condition(lot_id: int, condition: str) -> bool:
    """Set the lot's condition"""
    return await update_lot_data(lot_id, condition=condition)


async def set_lot_photos(lot_id: int, photos: str) -> bool:
    """Set the lot's photos"""
    return await update_lot_data(lot_id, photos=photos)


async def set_lot_start_price(lot_id: int, start_price: int) -> bool:
    """Set the lot's start price"""
    return await update_lot_data(lot_id, start_price=start_price)


async def set_lot_step_price(lot_id: int, step_price: int) -> bool:
    """Set the lot's step price"""
    return await update_lot_data(lot_id, step_price=step_price)


async def set_lot_payment_method(lot_id: int, payment_method: str) -> bool:
    """Set the lot's payment method"""
    return await update_lot_data(lot_id, payment_method=payment_method)


async def set_lot_city(lot_id: int, city: str) -> bool:
    """Set the lot's city"""
    return await update_lot_data(lot_id, city=city)


async def set_lot_redemption_price(lot_id: int, redemption_price: int) -> bool:
    """Set the lot's redemption price"""
    return await update_lot_data(lot_id, redemption_price=redemption_price)


async def set_lot_delivery_price(lot_id: int, delivery_price: int) -> bool:
    """Set the lot's delivery price"""
    return await update_lot_data(lot_id, delivery_price=delivery_price)


async def replace_moderation_status(old_status: str, new_status: str) -> int:
    """
    Replace all lots with moderation_status == old_status to new_status.
    Returns the number of updated lots.
    """
    async for session in get_session():
        result = await session.execute(
            sqlalchemy_update(DBLot)
            .where(DBLot.moderation_status == old_status)
            .values(moderation_status=new_status)
        )
        if result.rowcount:
            await session.commit()
        return result.rowcount or 0


async def delete_lot(lot_id: int) -> bool:
    """Delete a lot by lot_id, return True if deleted, False otherwise"""
    async for session in get_session():
        result = await session.execute(
            sqlalchemy_delete(DBLot).where(DBLot.id == lot_id)
        )
        if result.rowcount:
            await session.commit()
            logger.debug(f"Lot {lot_id} deleted")
            return True
        return False


async def add_random_lots(
    count: int,
    user_id: int | None = None,
    group_id: int | None = None,
) -> list[DBLot]:
    """Add specified number of randomly generated lots to the database."""
    lots: list[DBLot] = []
    async for session in get_session():
        for _ in range(count):
            if not user_id:
                user_id = random.randint(1000000000, 9999999999)

            descriptions = [
                "Винтажная книга",
                "Антикварная ваза",
                "Старинные часы",
                "Коллекционная монета",
                "Картина маслом",
                "Фарфоровая статуэтка",
                "Редкая марка",
                "Старинное украшение",
            ]

            conditions = [
                "Отличное",
                "Хорошее",
                "Удовлетворительное",
                "Требует реставрации",
            ]
            payment_methods = [
                "Наличные",
                "Банковский перевод",
                "Электронные деньги",
                "Криптовалюта",
            ]
            cities = [
                "Москва",
                "Санкт-Петербург",
                "Новосибирск",
                "Екатеринбург",
                "Нижний Новгород",
                "Казань",
            ]

            new_lot = DBLot(
                user_id=user_id,
                description=escape(random.choice(descriptions)),
                condition=escape(random.choice(conditions)),
                photos="photo-231181743_457239060",
                photos_paths="randomlot.jpg",
                start_price=random.randint(1, 100) * 100,
                step_price=random.randint(1, 50) * 10,
                payment_method=escape(random.choice(payment_methods)),
                city=escape(random.choice(cities)),
                redemption_price=(
                    random.randint(1, 50) * 1000
                    if random.choice([True, False])
                    else None
                ),
                delivery_price=(
                    random.randint(1, 10) * 100
                    if random.choice([True, False])
                    else None
                ),
                group_id=group_id if group_id else None,
            )
            session.add(new_lot)
            lots.append(new_lot)
        await session.commit()
        for lot in lots:
            await session.refresh(lot)
        return lots
    return lots


async def get_last_lot_id() -> int | None:
    """Return the id of the last (highest id) lot in the database, or None if no lots."""
    async for session in get_session():
        stmt = select(DBLot.id).order_by(DBLot.id.desc()).limit(1)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
    return None


async def get_user_win_lots(user_id: int) -> list[DBLot]:
    """Return all lots won by a specific user"""
    async for session in get_session():
        stmt = select(DBLot).where(
            DBLot.last_bettor_id == user_id,
            or_(
                DBLot.moderation_status == LotStatusDB.ENDED.value,
                DBLot.moderation_status == LotStatusDB.CLOSED.value
            )
        )
        result = await session.execute(stmt)
        return result.scalars().all()


async def get_lots_by_user(user_id: int) -> list[DBLot]:
    """Return all lots created by a specific user"""
    return await get_lot(user_id=user_id) or []


async def get_lots_by_price_range(min_price: int, max_price: int) -> list[DBLot]:
    """Return all lots within a specified price range"""
    async for session in get_session():
        stmt = select(DBLot).where(
            DBLot.start_price >= min_price, DBLot.start_price <= max_price
        )
        result = await session.execute(stmt)
        return result.scalars().all()
    return []


async def get_lots_by_city(city: str) -> list[DBLot]:
    """Return all lots in a specific city"""
    async for session in get_session():
        stmt = select(DBLot).where(DBLot.city == city)
        result = await session.execute(stmt)
        return result.scalars().all()
    return []


async def search_lots_by_description(search_term: str) -> list[DBLot]:
    """Search lots by description containing the search term"""
    async for session in get_session():
        stmt = select(DBLot).where(DBLot.description.contains(search_term))
        result = await session.execute(stmt)
        return result.scalars().all()
    return []
