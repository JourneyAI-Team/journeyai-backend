from typing import Callable
from agents import function_tool


# TODO: implement tools
@function_tool
def google_search():
    pass


def get_tool() -> Callable:
    return google_search
