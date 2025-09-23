from datetime import datetime

from sqlalchemy import Column, Integer, Text

from config.time import DATETIME_FORMAT as DTFMT
from config.time import TZ
from enums.moderation import LotStatusDB, LotStatusUser
from enums.rating import get_name
from utils import int_to_emojis

from ..connect import Base


class Lot(Base):
    __tablename__ = "lots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    description = Column(Text, nullable=False)
    condition = Column(Text, nullable=False)
    photos = Column(Text, nullable=True)  # Store as comma-separated values
    photos_paths = Column(Text, nullable=True)  # Store as comma-separated values
    user_photos = Column(Text, nullable=True)  # Store as comma-separated values
    start_price = Column(Integer, nullable=False)
    step_price = Column(Integer, nullable=False)
    payment_method = Column(Text, nullable=False)
    city = Column(Text, nullable=False)
    redemption_price = Column(Integer, nullable=True)  # Optional
    delivery_price = Column(Integer, nullable=True)  # Optional
    moderation_status = Column(Text, nullable=False, default=LotStatusDB.PENDING.value)
    moderation_result = Column(Text, nullable=True, default=None)
    moderation_response = Column(Text, nullable=True, default=None)
    group_id = Column(Integer, nullable=True)
    post_id = Column(Integer, nullable=True)
    publish_date = Column(Integer, nullable=True)  # Unix timestamp
    end_date = Column(Integer, nullable=True)  # Unix timestamp
    last_bet = Column(Integer, nullable=True)
    last_bet_comment = Column(Integer, nullable=True)
    last_bet_date = Column(Integer, nullable=True)  # Unix timestamp
    last_bettor_id = Column(Integer, nullable=True)
    commission = Column(Integer, nullable=True)

    async def as_post(self, seller):
        urgent_info = []
        main_info = [
            f"Рейтинг продавца: {get_name(seller.rating)}",
            f"Лот: {self.description}",
            f"Состояние: {self.condition}",
            f"Стартовая цена: {self.start_price} руб.",
            f"Шаг цены: {self.step_price} руб.",
        ]
        if self.last_bet:
            if self.redemption_price and self.last_bet == self.redemption_price:
                text = f"💸  ЛОТ ВЫКУПЛЕН {self.end_date_formatted()}!"
            else:
                text = f"{int_to_emojis(self.last_bet)}  руб. — ПОСЛЕДНЯЯ СТАВКА"
            urgent_info.append(text)

        if self.moderation_status in (
            LotStatusDB.ENDED.value,
            LotStatusDB.CLOSED.value,
        ):
            urgent_info.insert(0, "")
            urgent_info.insert(0, f"❗️ АУКЦИОН ЗАВЕРШЕН {self.end_date_formatted()} ❗️")

        if self.redemption_price:
            main_info.append(f"Цена выкупа: {self.redemption_price} руб.")
        main_info.append(f"Способ оплаты: {self.payment_method}")
        main_info.append(f"Город: {self.city}")
        if self.delivery_price:
            main_info.append(
                f"Цена доставки (оплата покупателем): {self.delivery_price} руб."
            )
        else:
            main_info.append("Доставка за счет продавца")
        main_info.append(f"Дата окончания: {self.end_date_formatted() or ''}")
        return "\n".join(urgent_info), "\n".join(main_info)

    async def as_user_review(
        self,
        seller,
        for_bettor: bool = False,
        for_admin: bool = False,
        additional_lines: list = None,
    ):
        urgent_info = []
        main_info = [
            f"Рейтинг продавца: {get_name(seller.rating)}",
            f"Лот: {self.description}",
            f"Статус: {LotStatusUser[self.moderation_status].value}",
            f"Состояние: {self.condition}",
            f"Стартовая цена: {self.start_price} руб.",
            f"Шаг цены: {self.step_price} руб.",
        ]
        additional_info = []

        is_ended = self.moderation_status in (
            LotStatusDB.ENDED.value,
            LotStatusDB.CLOSED.value,
        )

        if self.last_bet:
            bet_info = "победная" if is_ended else "последняя"
            text = f"{int_to_emojis(self.last_bet)}  руб. — {bet_info} ставка"
            urgent_info.append(text)

        if self.redemption_price:
            main_info.append(f"Цена выкупа: {self.redemption_price} руб.")
        main_info.append(f"Способ оплаты: {self.payment_method}")
        main_info.append(f"Город: {self.city}")
        if self.delivery_price:
            main_info.append(
                f"Цена доставки (оплата покупателем): {self.delivery_price} руб."
            )
        else:
            main_info.append("Доставка за счет продавца")
        main_info.append(f"Дата окончания: {self.end_date_formatted() or ''}")

        if for_admin:
            additional_info.append(f"Владелец: {self.user_link}")
            if self.last_bet:
                additional_info.append(f"Победитель: {self.bettor_link}")
            additional_info.append(
                f"Ответ модерации: {self.moderation_response or '—'}"
            )
            additional_info.append(f"Комиссия: {self.commission or '—'} руб.")
        elif is_ended and self.last_bet:
            if for_bettor:
                additional_info.append(f"Владелец: {self.user_link}")
            if not for_bettor:
                additional_info.append(f"Победитель: {self.bettor_link}")

        additional_info.extend(additional_lines or [])

        return "\n".join(urgent_info), "\n".join(main_info), "\n".join(additional_info)

    def end_date_formatted(self):
        if not self.end_date:
            return
        end_datetime = datetime.fromtimestamp(self.end_date, tz=TZ)
        return end_datetime.strftime(DTFMT)

    @property
    def user_link(self):
        return f"https://vk.com/id{self.user_id}"

    @property
    def bettor_link(self):
        if not self.last_bettor_id:
            return None
        return f"https://vk.com/id{self.last_bettor_id}"
