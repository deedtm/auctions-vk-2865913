from dataclasses import dataclass
from typing import Optional

from vkbottle_types.objects import MessagesMessageAttachment

PHOTOS_FORMAT = "photo{}_{}_{}"
# PHOTOS_FORMAT = "photo{}_{}"


@dataclass
class Lot:
    description: str
    condition: str
    photos: list[str]
    photos_paths: list[str]
    start_price: int
    step_price: int
    payment_method: str
    city: str
    group_id: int
    redemption_price: Optional[int] = None  # цена выкупа
    delivery_price: Optional[int] = None

    def get_photos(attachments: list[MessagesMessageAttachment]):
        return [
            PHOTOS_FORMAT.format(a.photo.owner_id, a.photo.id, a.photo.access_key)
            for a in attachments
            if a.photo
        ]

    def from_poll(
        lot_data: list,
        attachments: list[MessagesMessageAttachment],
        photos_paths: list[str],
        group_id: int,
    ):
        description = lot_data[0]
        condition = lot_data[1]
        start_price = int(lot_data[2])
        step_price = int(lot_data[3])
        redemption_price = int(lot_data[4]) if lot_data[4] else None
        payment_method = lot_data[5]
        city = lot_data[6]
        delivery_price = int(lot_data[7]) if lot_data[7] else None

        photos = Lot.get_photos(attachments)

        return Lot(
            description=description,
            condition=condition,
            photos=photos,
            photos_paths=photos_paths,
            start_price=start_price,
            step_price=step_price,
            redemption_price=redemption_price,
            payment_method=payment_method,
            city=city,
            delivery_price=delivery_price,
            group_id=group_id,
        )

    def from_form(
        text: str,
        attachments: list[MessagesMessageAttachment],
        photos_paths: list[str],
        group_id: int,
    ) -> "Lot":
        lines = text.split("\n")
        return Lot.from_poll(lines, attachments, photos_paths, group_id)

    @property
    def photos_as_attachments(self) -> list[str]:
        return ",".join(self.photos)

    def __str__(self):
        return (
            f"Лот: {self.description}\n"
            + f"Состояние: {self.condition}\n"
            + f"Стартовая цена: {self.start_price} руб.\n"
            + f"Шаг цены: {self.step_price} руб.\n"
            + (
                f"Цена выкупа: {self.redemption_price} руб.\n"
                if self.redemption_price
                else ""
            )
            + f"Способ оплаты: {self.payment_method}\n"
            + f"Город: {self.city}\n"
            + (
                f"Цена доставки (оплата покупателем): {self.delivery_price} руб."
                if self.delivery_price
                else "Доставка за счет продавца"
            )
        )
