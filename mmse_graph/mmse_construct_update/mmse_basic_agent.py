from langchain.agents import create_agent
from pydantic import BaseModel, Field
from typing import Literal
from langchain.chat_models import BaseChatModel
from langchain_core.runnables import RunnableConfig
from langchain.messages import AIMessage
from .local_system_prompt.load import load
from .state_definition import State


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


class BasicAgent:
    def __init__(
        self,
        name: str,
        model: BaseChatModel,
        middleware: list = [],
        future_state=BaseModel,
    ):
        # Fetch system prompt

        self.agent = create_agent(
            name=name,
            model=model,
            tools=[],
            system_prompt=load(name),
            middleware=[],
            response_format=FollowUp,
        )

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
