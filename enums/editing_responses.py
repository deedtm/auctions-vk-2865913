from enum import Enum


class EditingResponses(Enum):
    SUCCESS = "success"
    CAPTCHA = "got_captcha"
    DELETED_POST = "deleted_post"
    UNKNOWN_FAILURE = "unknown_failure"
