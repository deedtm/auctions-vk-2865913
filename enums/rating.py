import json

with open('enums/rating_names.json') as f:
    RATINGS_NAMES = json.load(f)


def get_name(rating: int):
    for name, r in RATINGS_NAMES.items():
        condition = f'{r[0]} <= {rating}'
        if len(r) > 1:
            condition += f' <= {r[1]}'
        if eval(condition):
            return name
        