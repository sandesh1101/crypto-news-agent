from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from agents.news_tools import (
    get_crypto_news_tool,
    get_stock_news_tool,
)
import os
from config.config import OPENAI_API_KEY

# Set OpenAI API Key as environment variable
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# Initialize the LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Define the tools
tools = [get_crypto_news_tool, get_stock_news_tool]

# Initialize the agent
news_agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)