from . import _config

WAITING_RESULTS_DELAY = _config.getint("captcha_api", "waiting_results_delay")
