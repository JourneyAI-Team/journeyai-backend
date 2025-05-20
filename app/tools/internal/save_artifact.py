from typing import Callable
from agents import function_tool


# TODO: implement tools
@function_tool
def save_artifact():
    pass


def get_tool() -> Callable:
    return save_artifact
