import os
from dotenv import load_dotenv
from workflow_agents.base_agents import AugmentedPromptAgent

# Load environment variables from .env file
load_dotenv()

# Retrieve OpenAI API key from environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")

prompt = "What is the capital of France?"
persona = "You are a college professor; your answers always start with: 'Dear students,'"

augmented_agent = AugmentedPromptAgent(
    openai_api_key=openai_api_key,
    persona=persona
)

augmented_agent_response = augmented_agent.respond(prompt)

# Print the agent's response
print(augmented_agent_response)

# - What knowledge the agent likely used to answer the prompt.
# - How the system prompt specifying the persona affected the agent's response.

# The agent likely used general knowledge about world capitals to answer the prompt.
# The system prompt specifying the persona influenced the answer starting with "Dear students," as a college professor would.
