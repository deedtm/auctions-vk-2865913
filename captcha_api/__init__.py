import os

from . import config, errors
from .utils import solve

__all__ = ("solve", "errors", "config")

if not "solution_tokens.txt" in os.listdir("captcha_api"):
    with open("solution_tokens.txt", "w") as f:
        f.write("hi!!:3")
