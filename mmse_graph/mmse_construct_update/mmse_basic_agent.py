from langchain.agents import create_agent
from pydantic import BaseModel, Field
from typing import Literal
from langchain.chat_models import BaseChatModel
from langchain_core.runnables import RunnableConfig
from langchain.messages import AIMessage
from .local_system_prompt.load import load


Status = Literal['NOT_PROCESSED', 'PROCESSING', 'COME_BACK_LATER', 'FINISHED']


class Conclusion(BaseModel):
    status: Status = Field(description="Define your current status", default="NOT_PROCESSED")
    reasoning: str = Field(description="Final reasoning about the chosen score", default="")
    score: int = Field(description="Given score to the answer of the user", default=-1)

class FollowUp(BaseModel):
    message: str = Field(description="You have to use this channel to speak to the user. It should never be empty! If you cannot proceed, explain why!", default="")
    conclusion: Conclusion = Field(
        description=("When all questions have been asked and answered, share your final score and reasoning here"),
        default_factory=lambda: Conclusion()
    )

class BasicAgent:
    def __init__(self, name: str, model: BaseChatModel, middleware: list = [], future_state = BaseModel):
        # Fetch system prompt
        
        self.agent = create_agent(
            name=name,
            model=model,
            tools=[],
            system_prompt=load(name),
            middleware=[],
            response_format=FollowUp
        )

    def invoke(self, state: BaseModel, config: RunnableConfig):
        answer = self.agent.invoke({'messages': state['messages']}, config)
        conclusion: Conclusion = answer['structured_response'].conclusion
        # Set status if not set yet
        if conclusion.status == 'NOT_PROCESSED':
            conclusion.status = 'PROCESSING'
        elif conclusion.status == 'PROCESSING' and conclusion.score != -1:
            conclusion.status = "FINISHED"
        messages = AIMessage(content=answer['structured_response'].message)
        return {'agents': {self.agent.name: conclusion}, 'messages': messages}
