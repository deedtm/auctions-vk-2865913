from enum import Enum


class HistoryEmojis(Enum):
    NEW = "❓"
    FORM_SHOWED = "❓"
    AUTHORIZING = "❓"
    THREEDS_CHECKING = "❓"
    THREEDS_CHECKED = "❓"
    AUTHORIZED = "❓"
    PAY_CHECKING = "❓"
    CONFIRMING = "❓"
    CONFIRMED = "✅"
    REVERSING = "❓"
    PARTIAL_REVERSED = "❓"
    REVERSED = "❓"
    REFUNDING = "❓"
    PARTIAL_REFUNDED = "❓"
    REFUNDED = "❓"
    CANCELLED = "❌"
    DEADLINE_EXPIRED = "❓"
    REJECTED = "❌"
    AUTH_FAIL = "❓"
