from deepagents import create_deep_agent
from langfuse import get_client
from langchain.chat_models import BaseChatModel

research_subagent = {
    "name": "research-agent",
    "description": "Used to research more in depth questions",
    "system_prompt": "You are a great researcher",
    "tools": [internet_search],
    "model": "openai:gpt-5.2",  # Optional override, defaults to main agent model
}
subagents = [research_subagent]

def create_sub_agent(langfuse_resource_name: str, model: BaseChatModel, middleware: list = []) -> dict:
    # Fetch the prompt
    langfuse = get_client()
    agent_prompts = langfuse.get_prompt(langfuse_resource_name + "_prompt").prompt
    agent_description = langfuse.get_prompt(langfuse_resource_name + "_description").prompt
    # Construct agent
    agent = {
        "name": langfuse_resource_name,
        "description": agent_description[0]['content'],
        "system_prompt": agent_prompts[0]['content'],
        "model": model,
        "middleware": middleware,
        "interrupt_on": 
    }
    return agent

def create