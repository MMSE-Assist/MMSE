from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages

from langchain.messages import AnyMessage

def merge_agents(left: dict, right: dict) -> dict:
    return {**left, **right}

class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    agents: Annotated[dict, merge_agents]
    to_proceed: bool