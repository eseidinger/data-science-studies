# Test script for DirectPromptAgent class

import os
from dotenv import load_dotenv
from workflow_agents.base_agents import DirectPromptAgent

# Load environment variables from .env file
load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
prompt = "What is the Capital of France?"

direct_agent = DirectPromptAgent(openai_api_key=openai_api_key)
direct_agent_response = direct_agent.respond(prompt)

# Print the response from the agent
print(direct_agent_response)

print("The agent likely used its pre-trained knowledge base, which includes general world knowledge up to its training cutoff date, to answer the prompt.")
