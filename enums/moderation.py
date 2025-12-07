from enum import Enum


class LotStatusDB(Enum):
    PENDING = "pending"
    MODERATED = "moderated"
    PUBLISHED = "published"
    REDEEMED = "redeemed"
    ENDED = "ended"
    CLOSED = "closed"
    OVERLIMITED = "overlimited"
    WAITING_LIMIT = "waiting_limit"
    MOVED = "moved"
    FAILED_USER_PHOTO_UPLOAD = "failed_user_photo_upload"
    WAITING_END = "waiting_end"

    def __str__(self):
        return self.value


class LotStatusUser(Enum):
    pending = "ожидает модерации"
    moderated = "модерация пройдена"
    published = "опубликован"
    redeemed = "выкуплен"
    ended = "окончен"
    closed = "окончен"
    overlimited = "превышен лимит постов в выбранной группе"
    waiting_limit = "ожидает публикации в выбранную группу (был превышен лимит постов)"
    moved = "перенесен в другую группу"
    failed_user_photo_upload = "не удалось использовать фото для публикации"


class ModerationResult(Enum):
    APPROVED = "approved"
    REJECTED = "rejected"

    def __str__(self):
        return self.value
