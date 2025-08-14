from typing import List, Optional

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from enums.payment_methods import PaymentMethod
from t_api.types.payments import GetStateResponse

from ..connect import get_session
from .models import Payment


async def add_payment(
    user_id: int,
    amount: int,
    order_id: str,
    success: bool,
    status: str,
    payment_id: str,
    error_code: str,
    message: Optional[str] = None,
    details: Optional[str] = None,
    lots_ids: Optional[list[int]] = None,
) -> Payment:
    """
    Добавить новый платеж в базу данных

    Args:
        user_id: ID пользователя
        amount: Сумма платежа
        order_id: ID заказа
        success: Успешность платежа
        status: Статус платежа
        payment_id: ID платежа
        error_code: Код ошибки
        message: Сообщение (опционально)
        details: Детали (опционально)

    Returns:
        Payment: Созданный объект платежа
    """
    async for session in get_session():
        if lots_ids:
            lots_ids = ",".join(map(str, lots_ids))
        payment = Payment(
            user_id=user_id,
            lots_ids=lots_ids,
            amount=amount,
            order_id=order_id,
            success=success,
            status=status,
            payment_id=payment_id,
            error_code=error_code,
            message=message,
            details=details,
        )
        session.add(payment)
        await session.commit()
        await session.refresh(payment)
        return payment


async def add_payment_from_response(
    user_id: int,
    response: GetStateResponse,
    lots_ids: Optional[List[int]] = None,
) -> Payment:
    """
    Добавить платеж из ответа API

    Args:
        user_id: ID пользователя
        response: Ответ от API платежной системы

    Returns:
        Payment: Созданный объект платежа
    """
    async for session in get_session():
        payment = Payment.from_get_state_response(
            user_id, response, lots_ids
        )
        session.add(payment)
        await session.commit()
        await session.refresh(payment)
        return payment


async def get_payment_by_id(payment_id: int) -> Optional[Payment]:
    """
    Получить платеж по ID

    Args:
        payment_id: ID платежа в базе данных

    Returns:
        Payment | None: Объект платежа или None если не найден
    """
    async for session in get_session():
        result = await session.execute(select(Payment).where(Payment.id == payment_id))
        return result.scalar_one_or_none()


async def get_payments_by_user_id(user_id: int) -> List[Payment]:
    """
    Получить все платежи пользователя

    Args:
        user_id: ID пользователя

    Returns:
        List[Payment]: Список платежей пользователя
    """
    async for session in get_session():
        result = await session.execute(
            select(Payment).where(Payment.user_id == user_id)
        )
        return list(result.scalars().all())


async def get_successful_payments_by_user_id(user_id: int) -> List[Payment]:
    """
    Получить все успешные платежи пользователя

    Args:
        user_id: ID пользователя

    Returns:
        List[Payment]: Список успешных платежей пользователя
    """
    async for session in get_session():
        result = await session.execute(
            select(Payment).where(Payment.user_id == user_id, Payment.success == True)
        )
        return list(result.scalars().all())


async def update_payment(payment_id: int, **fields) -> Optional[Payment]:
    """
    Обновить платеж по указанным полям

    Args:
        payment_id: ID платежа в базе данных
        **fields: Поля для обновления

    Returns:
        Payment | None: Обновленный объект платежа или None если не найден
    """
    if not fields:
        return await get_payment_by_id(payment_id)

    async for session in get_session():
        # Проверяем существование платежа
        result = await session.execute(select(Payment).where(Payment.id == payment_id))
        payment = result.scalar_one_or_none()

        if not payment:
            return None

        # Обновляем поля
        await session.execute(
            update(Payment).where(Payment.id == payment_id).values(**fields)
        )
        await session.commit()

        # Возвращаем обновленный объект
        await session.refresh(payment)
        return payment


async def delete_payment(payment_id: int) -> bool:
    """
    Удалить платеж по ID

    Args:
        payment_id: ID платежа в базе данных

    Returns:
        bool: True если платеж был удален, False если не найден
    """
    async for session in get_session():
        # Проверяем существование платежа
        result = await session.execute(select(Payment).where(Payment.id == payment_id))
        payment = result.scalar_one_or_none()

        if not payment:
            return False

        # Удаляем платеж
        await session.execute(delete(Payment).where(Payment.id == payment_id))
        await session.commit()
        return True


async def delete_payment_by_order_id(order_id: str) -> bool:
    """
    Удалить платеж по ID заказа

    Args:
        order_id: ID заказа

    Returns:
        bool: True если платеж был удален, False если не найден
    """
    async for session in get_session():
        # Проверяем существование платежа
        result = await session.execute(
            select(Payment).where(Payment.order_id == order_id)
        )
        payment = result.scalar_one_or_none()

        if not payment:
            return False

        # Удаляем платеж
        await session.execute(delete(Payment).where(Payment.order_id == order_id))
        await session.commit()
        return True


async def delete_payments_by_user_id(user_id: int) -> int:
    """
    Удалить все платежи пользователя

    Args:
        user_id: ID пользователя

    Returns:
        int: Количество удаленных платежей
    """
    async for session in get_session():
        result = await session.execute(
            delete(Payment).where(Payment.user_id == user_id)
        )
        await session.commit()
        return result.rowcount


async def get_total_amount_by_user_id(
    user_id: int, only_successful: bool = True
) -> int:
    """
    Получить общую сумму платежей пользователя

    Args:
        user_id: ID пользователя
        only_successful: Учитывать только успешные платежи

    Returns:
        int: Общая сумма платежей
    """
    async for session in get_session():
        query = select(Payment).where(Payment.user_id == user_id)

        if only_successful:
            query = query.where(Payment.success == True)

        result = await session.execute(query)
        payments = result.scalars().all()

        return sum(payment.amount for payment in payments)
