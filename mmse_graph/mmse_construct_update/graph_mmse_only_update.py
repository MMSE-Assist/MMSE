# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from dotenv import load_dotenv
import os
import logging

# Add State dependencies
from langgraph.graph.message import add_messages
from pydantic import BaseModel

# Add Basic agent
from .mmse_basic_agent import BasicAgent, Conclusion

from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_neo4j import Neo4jSaver
from neo4j import GraphDatabase
from langchain.agents import create_agent
from langchain.agents.middleware import ToolRetryMiddleware
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, StateGraph, START
from langchain.messages import AnyMessage
from langgraph.checkpoint.memory import InMemorySaver

from langfuse import get_client
from langfuse.langchain import CallbackHandler

import sys 
from typing import Annotated
from typing_extensions import TypedDict


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

#################
### variables ###
#################

env_var_file = "vars.local.env"

def load_env_variables():
    """Load environment variables from vars.env file and return configuration"""
    #########################
    ### get env variables ###
    #########################
    load_dotenv(env_var_file, override=True)  # This line brings all environment variables from vars.env into os.environ

    assert os.environ['NVIDIA_API_KEY'] is not None, "Make sure you have your NVIDIA_API_KEY exported as a environment variable!"
    nvidia_api_key = os.getenv("NVIDIA_API_KEY", None)

    assert os.environ['AGENT_LLM_MODEL'] is not None, "Make sure you have your AGENT_LLM_MODEL exported as a environment variable!"
    llm_model = os.getenv("AGENT_LLM_MODEL", None)

    assert os.environ['AGENT_LLM_BASE_URL'] is not None, "Make sure you have your AGENT_LLM_BASE_URL exported as a environment variable!"
    base_url = os.getenv("AGENT_LLM_BASE_URL", None)

    nemo_guardrails_config_path = os.getenv("NEMO_GUARDRAILS_CONFIG_PATH", None)

    # Langfuse credentials
    langfuse_public_key = os.getenv("LANGFUSE_PUBLIC_KEY", None)
    langfuse_secret_key = os.getenv("LANGFUSE_SECRET_KEY", None)
    langfuse_base_url = os.getenv("LANGFUSE_BASE_URL", None)
    langfuse_prompt_name = os.getenv("LANGFUSE_PROMPT_NAME", "patient-intake-initial")
    langfuse_prompt_label = os.getenv("LANGFUSE_PROMPT_LABEL", "production")

    # Neo4j credentials
    neo4j_uri = os.getenv("NEO4J_URI", "").strip()
    neo4j_username = os.getenv("NEO4J_USERNAME", "neo4j").strip()
    neo4j_password = os.getenv("NEO4J_PASSWORD", "").strip()

    return {
        'nvidia_api_key': nvidia_api_key,
        'llm_model': llm_model,
        'base_url': base_url,
        'nemo_guardrails_config_path': nemo_guardrails_config_path,
        'langfuse_public_key': langfuse_public_key,
        'langfuse_secret_key': langfuse_secret_key,
        'langfuse_base_url': langfuse_base_url,
        'langfuse_prompt_name': langfuse_prompt_name,
        'langfuse_prompt_label': langfuse_prompt_label,
        'neo4j_uri': neo4j_uri,
        'neo4j_username': neo4j_username,
        'neo4j_password': neo4j_password,
    }

########################
### Define the tools ###
########################

#@tool
#def print_gathered_patient_info():
#    pass

def get_agents_with_types_and_schema() -> list:
    agents = [
        ('orientation_time', BasicAgent, Conclusion),
        ('orientation_place', BasicAgent, Conclusion),
        ('registration', BasicAgent, Conclusion),
        ('attention_calculation', BasicAgent, Conclusion),
        ('recall', BasicAgent, Conclusion),
        ('naming', BasicAgent, Conclusion),
        ('repetition', BasicAgent, Conclusion),
        ('three_stage_command', BasicAgent, Conclusion),
        ('reading', BasicAgent, Conclusion),
        ('writing', BasicAgent, Conclusion),
        ('drawing', BasicAgent, Conclusion),
    ]
    return agents

def switcher(state: State) -> str:
    # Basic, increment one up
    for agent_name, output in state['agents'].items():
        if output.status != 'FINISHED':
            return agent_name
    return END

def merge_agents(left: dict, right: dict) -> dict:
    return {**left, **right}

class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    agents: Annotated[dict, merge_agents]

class InitAgent:
    def __init__(self) -> None:
        self.name = "init"
    def init_agents(self, state: State) -> dict:
        if not state['agents']:
            return {
                'agents': {name: output_format() for name, _, output_format in get_agents_with_types_and_schema()}
            }
        return state


class MmseAgent:
    def __init__(self, model, prompts, callbacks= None):
        self.agent = create_agent(
            model=model, 
            tools=[], 
            system_prompt=prompts,
            middleware=[ToolRetryMiddleware()]) # AgentMiddleware() to add later
        self.callbacks = callbacks

    def _set_callbacks_if_needed(self, config: RunnableConfig):
        if self.callbacks:
            logging.info("Added langfuse callback in graph!")
            config['callbacks'] = self.callbacks
        
    async def ainvoke(self, state: State, config: RunnableConfig):
        self._set_callbacks_if_needed(config)
        return self.agent.ainvoke(state, config)
    
    def invoke(self, state: State, config: RunnableConfig):
        self._set_callbacks_if_needed(config)
        return self.agent.invoke(state, config)

def create_mmse_graph():
    """Create and return a fresh instance of the intake graph"""
    # Reload environment variables from vars.env
    env_config = load_env_variables()
    
    # Create fresh LLM instance with reloaded config
    assistant_llm = ChatNVIDIA(
        model=env_config['llm_model'], 
        base_url=env_config['base_url']
    )
    # Open a langfuse connection
    langfuse = get_client()
    langfuse_handler = CallbackHandler()
    
    # Get langfuse prompts
    #agent_prompts = langfuse.get_prompt(env_config['langfuse_prompt_name']).prompt
    #logging.info(f"{agent_prompts[0]['content']}")

    # Create a fresh StateGraph builder
    builder = StateGraph(State)
    
    # Define nodes: these do the work
    init = InitAgent()
    builder.add_node(init.name, init.init_agents)
    builder.add_edge(START, init.name)
    #switch_table = {}
    for name, agent_type, output_format in get_agents_with_types_and_schema():
        builder.add_node(name, agent_type(name, assistant_llm, [], State).invoke)
        #switch_table[name] = name
    #builder.add_conditional_edges(init.name, switcher, switch_table)
    builder.add_conditional_edges(init.name, switcher)
    #builder.add_node("start_node", MmseAgent(assistant_llm, "Be nice").invoke)
    #builder.add_edge(START, "start_node")
    graph = builder.compile(checkpointer=InMemorySaver())

    logging.info("Graph built successfully")
    return graph
