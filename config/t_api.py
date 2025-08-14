from . import _config

config_keys = (
    "description",
    "language",
    "notification_url",
    "success_url",
    "fail_url",
    "redirect_due_date",
)

DESCRIPTION, LANGUAGE, NOTIFICATION_URL, SUCCESS_URL, FAIL_URL, REDIRECT_DUE_DATE = [
    _config.get("t_api", key) or None for key in config_keys
]

__all__ = (
    "DESCRIPTION",
    "LANGUAGE",
    "NOTIFICATION_URL",
    "SUCCESS_URL",
    "FAIL_URL",
    "REDIRECT_DUE_DATE",
)
