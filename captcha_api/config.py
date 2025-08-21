import os

from config.captcha_api import *

BASE_URL = "https://api.rucaptcha.com/"

RUCAPTCHA_TOKEN = os.getenv("RUCAPTCHA_TOKEN")
PROXY_TYPE = os.getenv("PROXY_TYPE")
PROXY_IP, PROXY_PORT = os.getenv("PROXY_IP").split(":")
PROXY_USERNAME = os.getenv("PROXY_USERNAME", None)
PROXY_PASSWORD = os.getenv("PROXY_PASSWORD")
