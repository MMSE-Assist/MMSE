import os
import base64
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(
        Path(__file__).parents[2] / "vars.local.env",
)

from langchain.agents import create_agent
from langchain.chat_models import BaseChatModel
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain.messages import SystemMessage, HumanMessage, AIMessage
from typing_extensions import TypedDict
from langchain_core.runnables import RunnableConfig
from langgraph.graph.message import add_messages
from typing import Annotated
from langchain.tools import tool
from requests import request


@tool
def send_image_to_user(image_base_64: str):
    return request('POST', os.environ['DRAWING_REST_ENDPOINT'], data={'image': image_base_64})

@tool
def collect_user_image():
    return request('GET', os.environ['DRAWING_REST_ENDPOINT'])['content']



def _load_image_as_base64_url(image_path: Path) -> str:
    """Load an image file and return it as a base64 data URL."""
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")
    mime = f"image/{image_path.suffix.lstrip('.')}"
    return f"data:{mime};base64,{image_data}"


class DrawingTester:
    def __init__(self, model: BaseChatModel) -> None:
        # Get image location
        image_path: Path = Path(__file__).parent / "drawing_data" / "lines_and_cross.png"
        # Create system prompt
        system_prompt = SystemMessage(
            content=[
                {"type": "text", "text": "You are a doctor that is currently performing a MMSE test. (1) Out of the given picture, generate a new one that is slightly different. (2) Ask the patient to copy the drawing. (3) When the patient is done, evaluate his picture and assign him 0 or 1 with 1 if it has 80% similarities"},
                {
                    "type": "image_url",
                    "image_url": {"url": _load_image_as_base64_url(image_path)},
                },
            ]
        )
        # Create agent
        self.agent = create_agent(
            model=model,
            system_prompt=system_prompt,
            tools=[send_image_to_user, collect_user_image]
        )

    def _populate_human_message_with_image(self, message: HumanMessage) -> HumanMessage:
        """Return a new HumanMessage with the user drawing appended if it exists."""
        if not isinstance(message, HumanMessage):
            return message
        # Check if drawing was added
        user_drawing: Path = Path(__file__).parent / "drawing_data" / "user_drawing.png"
        if not user_drawing.exists():
            return message

        # Normalize existing content to list form
        content = message.content
        if isinstance(content, str):
            content = [{"type": "text", "text": content}]
        else:
            content = list(content)

        content.append(
            {
                "type": "image_url",
                "image_url": {"url": _load_image_as_base64_url(user_drawing)},
            }
        )
        return HumanMessage(content=content)

    async def ainvoke(self, state: TypedDict, config: RunnableConfig):
        if state['messages']:
            state['messages'][-1] = self._populate_human_message_with_image(state['messages'][-1])
        result = await self.agent.ainvoke(state, config)
        response = result["messages"][-1]
        return {"messages": [response]}

    def invoke(self, state: TypedDict, config: RunnableConfig):
        if state['messages']:
            state['messages'][-1] = self._populate_human_message_with_image(state['messages'][-1])
        result = self.agent.invoke(state, config)
        response = result["messages"][-1]
        return {"messages": [response]}


if __name__ == "__main__":

    model = ChatNVIDIA(
        model="moonshotai/kimi-k2.5",
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=os.environ["NVIDIA_API_KEY"],
    )

    agent = DrawingTester(model)

    # Simple test dialogue for the drawing MMSE sub-task
    dialogue = [
        HumanMessage(content="Hello doctor, I'm ready to start."),
        HumanMessage(content="I have finished copying the drawing."),
    ]

    # State
    class State(TypedDict):
        messages: Annotated[list, add_messages]
    state = State(messages=[])

    for human_msg in dialogue:
        state["messages"] = state.get("messages", []) + [human_msg]
        result = agent.invoke(state, {})
        # Accumulate full conversation history
        state["messages"] = state["messages"] + result["messages"]
        ai_reply = state["messages"][-1]
        print(f"Doctor: {ai_reply.content}\n")