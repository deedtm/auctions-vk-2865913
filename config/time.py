from datetime import timedelta, timezone

from . import _config

TZ_OFFSET = _config.getint("time", "timezone_offset")
TZ = timezone(timedelta(hours=TZ_OFFSET))

DATETIME_FORMAT = _config.get("time", "datetime_format")
