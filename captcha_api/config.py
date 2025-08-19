import os

BASE_URL = 'https://api.rucaptcha.com/'

RUCAPTCHA_TOKEN = os.getenv("RUCAPTCHA_TOKEN")
PROXY_IP, PROXY_PORT = os.getenv("PROXY_IP").split(":")
PROXY_PASSWORD = os.getenv("PROXY_PASSWORD")
