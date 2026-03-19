from langchain.agents import create_agent
from pydantic import BaseModel, Field
from typing import Literal
from langchain.chat_models import BaseChatModel
from langchain_core.runnables import RunnableConfig
from langchain.messages import AIMessage
from .local_system_prompt.load import load

from .state_definition import State
from langgraph.graph import END


class StartTest(BaseModel):
    message: str = Field(
        description="You have to use this channel to speak to the user. It should never be empty! If you cannot proceed, explain why!",
        default="",
    )
    patient_test_readiness: bool = Field(
        description="Readiness of the user to start the test", default=False
    )


class IntakeAgent:
    def __init__(
        self,
        model: BaseChatModel,
        middleware: list = [],
        sub_name_and_output_list: list = [],
    ):
        self.state_name = "init_state"
        self.name = "intake"
        self.agent = create_agent(
            name=self.name,
            model=model,
            tools=[],
            system_prompt=load(self.name),
            middleware=[],
            response_format=StartTest,
        )
        self.subagents = sub_name_and_output_list

    def switcher(self, state: State) -> str:
        # If the decision was not to proceed yet, end
        if state["to_proceed"] == False:
            return END
        # Basic, increment one up
        for agent_name, output in state["agents"].items():
            if output.status != "FINISHED":
                return agent_name
        return END

    def init_state(self, state: State, config: RunnableConfig) -> dict | State:
        # Proceed with setting up the rest
        if not state["agents"]:
            return {
                "agents": {
                    name: output_format()
                    for name, _, output_format, _ in self.subagents
                },
                "to_proceed": False,
            }
        return state

    def invoke(self, state: State, config: RunnableConfig):
        if state["to_proceed"] == True:
            return state
        answer = self.agent.invoke({"messages": state["messages"]}, config)
        structured_answer: StartTest = answer["structured_response"]
        new_state = state.copy()
        new_state["to_proceed"] = structured_answer.patient_test_readiness
        new_state["messages"] = AIMessage(content=structured_answer.message)
        return new_state
