"""Search source records without upgrading their mathematical status."""

import json
from pathlib import Path

DATA = Path(__file__).resolve().parent / 'data'


def load(name):
    with (DATA / name).open(encoding='utf-8') as stream:
        return json.load(stream)


def search(records, query='', limit=12):
    terms = set(query.casefold().split())
    ranked = []
    for item in records:
        text = json.dumps(item, ensure_ascii=False).casefold()
        score = sum(1 for term in terms if term in text)
        if not terms or score:
            ranked.append((score, item))
    ranked.sort(key=lambda pair: (-pair[0], pair[1].get('name', pair[1].get('id', '')).casefold()))
    return [item for _, item in ranked[:limit]]


def portfolio(query='', limit=12):
    return search(load('portfolio.json')['repositories'], query, limit)


def routes(query='', limit=12):
    return search(load('construction-atlas.json')['routes'], query, limit)


def upstreams(query='', limit=12):
    return search(load('public-upstream-watch.json')['repositories'], query, limit)
