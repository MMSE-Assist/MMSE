import os
import base64
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(
    Path(__file__).parents[2] / "vars.local.env",
)

from langchain.agents import create_agent
from langchain.chat_models import BaseChatModel
from langchain.messages import SystemMessage, HumanMessage, AnyMessage, AIMessage
from langchain_core.runnables import RunnableConfig
from typing import Any, cast
from langchain.tools import tool
from requests import request
from .local_system_prompt.load import load
from pydantic import BaseModel, Field
from typing import Literal
from .state_definition import State
from langchain.agents.middleware import ModelRetryMiddleware, ToolRetryMiddleware


@tool
def send_image_to_user():
    """Send a reference image to the drawing UI so the patient can see and copy it.

    Posts the image to the drawing REST endpoint. The UI will display the image
    on the canvas and prompt the patient to draw a copy of it.

    Returns:
        A confirmation string once the image has been delivered successfully.
    """
    user_drawing: Path = Path(__file__).parent / "drawing_data" / "user_drawing.png"
    image_base_64 = _load_image_as_base64_url(user_drawing)

    response = request(
        "POST",
        os.environ["DRAWING_REST_ENDPOINT"],
        json={"image": image_base_64},
        timeout=10,
    )
    response.raise_for_status()
    return "Reference image sent to drawing UI."


@tool
def collect_user_image():
    """Retrieve the drawing the patient submitted through the UI.

    Performs a GET request to the drawing REST endpoint and returns the image
    as a base64 data URL. The endpoint returns 404 until the patient presses
    the *Done* button, so this tool should only be called after the patient
    has had sufficient time to complete the drawing.

    Returns:
        The patient's drawing as a ``data:<mime>;base64,<data>`` URL string.
    """
    response = request("GET", os.environ["DRAWING_REST_ENDPOINT"], timeout=10)
    response.raise_for_status()
    mime_type = response.headers.get("Content-Type", "image/png")
    image_data = base64.b64encode(response.content).decode("utf-8")
    return f"data:{mime_type};base64,{image_data}"


def _load_image_as_base64_url(image_path: Path) -> str:
    """Load an image file and return it as a base64 data URL."""
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")
    mime = f"image/{image_path.suffix.lstrip('.')}"
    return f"data:{mime};base64,{image_data}"


Status = Literal["NOT_PROCESSED", "PROCESSING", "COME_BACK_LATER", "FINISHED"]


class Conclusion(BaseModel):
    status: Status = Field(
        description="Define your current status", default="NOT_PROCESSED"
    )
    reasoning: str = Field(
        description="Final reasoning about the chosen score", default=""
    )
    score: int = Field(description="Given score to the answer of the user", default=-1)


class FollowUp(BaseModel):
    message: str = Field(
        description="You have to use this channel to speak to the user. It should never be empty! If you cannot proceed, explain why!",
        default="",
    )
    conclusion: Conclusion = Field(
        description=(
            "Track your progress after every turn. "
            "Set status='NOT_PROCESSED' while the section is still in progress. "
            "Set status='FINISHED' only when all questions are done — and in that case you MUST fill in score and reasoning."
        ),
        default_factory=lambda: Conclusion(),
    )


class DrawingTester:
    def __init__(
        self,
        name: str,
        model: BaseChatModel,
        middleware: list = [],
        future_state=BaseModel,
    ) -> None:
        # Get image location
        self._image_path: Path = (
            Path(__file__).parent / "drawing_data" / "lines_and_cross.png"
        )
        self.name = name
        # Create system prompt (text only — images are not allowed in system role messages)
        system_prompt = SystemMessage(content=load(self.name))
        # Create agent
        self.agent = create_agent(
            name=self.name,
            model=model,
            system_prompt=system_prompt,
            tools=[send_image_to_user, collect_user_image],
            middleware=[ModelRetryMiddleware(), ToolRetryMiddleware()],
            response_format=FollowUp,
        )

    def _populate_human_message_with_image(self, message: AnyMessage) -> AnyMessage:
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
            content_parts: list[str | dict[str, Any]] = [
                {"type": "text", "text": content}
            ]
        else:
            content_parts = cast(list[str | dict[str, Any]], list(content))

        content_parts.append(
            {
                "type": "image_url",
                "image_url": {"url": _load_image_as_base64_url(user_drawing)},
            }
        )
        return HumanMessage(content=content_parts)

    def invoke(self, state: State, config: RunnableConfig):
        answer = self.agent.invoke({"messages": state["messages"]}, config)
        structured_response: FollowUp = answer["structured_response"]
        conclusion = structured_response.conclusion
        messages = AIMessage(content=structured_response.message)
        # In case of the conclusion, exit gracefully
        if conclusion.status == "FINISHED" and not conclusion.reasoning:
            conclusion.reasoning = structured_response.message
            messages = AIMessage(
                content="Thank you! Are you ready for the next section?"
            )
        return {"agents": {self.agent.name: conclusion}, "messages": messages}
