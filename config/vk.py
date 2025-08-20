from datetime import datetime
from random import randint

from . import _config

_prefixes = _config.get("vk", "default_prefixes")
DEFAULT_PREFIXES = _prefixes.split(",")

FAKE_MODERATION_MIN_DURATION = _config.getint(
    "vk", "fake_moderation_min_duration_seconds"
)
FAKE_MODERATION_MAX_DURATION = _config.getint(
    "vk", "fake_moderation_max_duration_seconds"
)
fake_moderation_duration = lambda: randint(
    FAKE_MODERATION_MIN_DURATION, FAKE_MODERATION_MAX_DURATION
)

GROUP_LOTS_LIMIT = _config.getint("vk", "group_lots_limit")
USER_LOTS_LIMIT = _config.getint("vk", "user_lots_in_group_limit")

LOOPING_INITIAL_DELAY = _config.getint("vk", "looping_initial_delay_seconds")
MODERATION_INTERVAL = _config.getint("vk", "moderation_interval_seconds")
POSTING_INTERVAL = _config.getint("vk", "posting_interval_seconds")
RESULTS_INTERVAL = _config.getint("vk", "sending_results_interval_seconds")

_RAW_AUCTIONS_ENDING_TIME = _config.get("vk", "auctions_ending_time")
AUCTIONS_ENDING_TIME = datetime.strptime(_RAW_AUCTIONS_ENDING_TIME, "%H:%M")

AUCTIONS_EXTENSION = _config.getint("vk", "auctions_extension_seconds")
AUCTIONS_CLOSING_INTERVAL = _config.getint('vk', "auctions_closing_interval")

_RAW_COLLECTOR_NOTIFICATIONS_TIME = _config.get("vk", "collector_notifications_time")
COLLECTOR_NOTIFICATIONS_TIME = datetime.strptime(
    _RAW_COLLECTOR_NOTIFICATIONS_TIME, "%H:%M"
)

_reminder = _config.get("vk", "collector_reminder")
COLLECTOR_REMINDER = list(map(int, _reminder.split()))
COLLECTOR_REMINDER.sort()
FIRST_COLLECTOR_REMINDER = COLLECTOR_REMINDER[0]
LAST_COLLECTOR_REMINDER = COLLECTOR_REMINDER[-1]

BANS_INTERVAL = _config.getint("vk", "bans_interval_seconds")
BAN_COMMENT = _config.get("vk", "ban_comment")

_RAW_LOYAL_NOTIFICATIONS_TIME = _config.get("vk", "loyal_notifications_time")
LOYAL_NOTIFICATIONS_TIME = datetime.strptime(_RAW_LOYAL_NOTIFICATIONS_TIME, "%H:%M")
_loyal_reminders = _config.get("vk", "loyal_before_end_reminder")
LOYAL_REMINDERS = list(map(int, _loyal_reminders.split()))
LOYAL_REMINDERS.sort()

MAX_RATING_TO_DANGER = _config.getint("vk", "max_rating_to_danger")
_RAW_DIGEST_POSTING_TIME = _config.get("vk", "digest_posting_time")
DIGEST_POSTING_TIME = datetime.strptime(_RAW_DIGEST_POSTING_TIME, "%H:%M")
