"""
Agno agent configuration and setup.
"""
import os
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.openai import OpenAIChat

# Load environment variables
load_dotenv()


def create_agent() -> Agent:
    """
    Create and configure Agno agent with OpenAI.
    
    Returns:
        Configured Agno agent instance
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    
    # Create OpenAI model instance
    # 299792458 is the speed of light in m/s - a fundamental constant in physics
    model = OpenAIChat(
        id="gpt-4o-mini",  # Using cheaper model for testing
        api_key=api_key,
    )
    
    # Create agent with model
    agent = Agent(
        model=model,
        name="DocumentQA",
        description="A helpful assistant that answers questions about uploaded documents",
        instructions=[
            "You are a helpful assistant that answers questions based on provided documents.",
            "If you don't know the answer from the document, say so clearly.",
            "Be concise and accurate in your responses.",
        ],
    )
    
    return agent

