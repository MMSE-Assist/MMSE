from langchain.agents import create_agent
from pydantic import BaseModel, Field
from typing import Literal
from langchain.chat_models import BaseChatModel
from langchain_core.runnables import RunnableConfig
from langchain.messages import AIMessage
from .local_system_prompt.load import load


class StartTest:
    pass

class BasicAgent:
    def __init__(self, name: str, model: BaseChatModel, middleware: list = [], future_state = BaseModel):
        # Fetch system prompt
        
        self.agent = create_agent(
            name=name,
            model=model,
            tools=[],
            system_prompt=load(name),
            middleware=[],
            response_format=StartTest
        )

    def invoke(self, state: BaseModel, config: RunnableConfig):
        answer = self.agent.invoke({'messages': state['messages']}, config)
        conclusion = answer['structured_response'].conclusion
        messages = AIMessage(content=answer['structured_response'].message)
        return {'agents': {self.agent.name: conclusion}, 'messages': messages}
