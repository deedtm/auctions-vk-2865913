import hashlib
import inspect
from typing import Optional, Any


def snake_to_pascal(snake_str: str) -> str:
    words = snake_str.split("_")
    return "".join(word.capitalize() for word in words)


def token_field_filter(item):
    is_field_valid = isinstance(item[1], (str, int))
    is_token = item[0].lower() in ["password", "token"]
    return is_field_valid and not is_token


def get_required_params(cls):
    sig = inspect.signature(cls.__init__)
    params = [
        name
        for name, param in sig.parameters.items()
        if name != "self"
        and param.default is param.empty
        and param.kind in (param.POSITIONAL_OR_KEYWORD, param.KEYWORD_ONLY)
    ]
    return params


def generate_token(
    obj: Any, password: str, filter_func: Optional[callable] = None, **kwargs
) -> str:
    # snake_data = {k: getattr(obj, k) for k in get_required_params(obj.__class__)}

    snake_data = obj.__dict__

    order_id = getattr(obj, "order_id", None)
    if not "order_id" in snake_data and order_id is not None:
        snake_data["order_id"] = order_id
    snake_data.update(kwargs)

    data = {}
    for k, v in snake_data.items():
        data[snake_to_pascal(k)] = v

    ff = filter_func or token_field_filter

    arr = dict(filter(ff, data.items()))
    arr["Password"] = password
    arr = dict(sorted(arr.items(), key=lambda item: item[0].lower()))
    concatenated = "".join([str(v) for v in arr.values()])
    token = hashlib.sha256(concatenated.encode()).hexdigest()

    return token
