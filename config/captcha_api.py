from . import _config

WAITING_RESULT_DELAY = _config.getint("captcha_api", "waiting_result_delay")
