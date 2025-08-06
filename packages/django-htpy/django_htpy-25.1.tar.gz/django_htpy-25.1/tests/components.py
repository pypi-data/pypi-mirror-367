from htpy import Renderable, h1


def page_title(title: str) -> Renderable:
    return h1[title]
