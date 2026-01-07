import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables and initialize OpenAI client
load_dotenv()
client = OpenAI(
    # base_url = "https://openai.vocareum.com/v1",
    api_key=os.getenv("OPENAI_API_KEY"))

# --- Helper Function for API Calls ---
def call_openai(system_prompt, user_prompt, model="gpt-3.5-turbo"):
    """Simple wrapper for OpenAI API calls."""
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0
    )
    return response.choices[0].message.content


# --- Agents for Different Retail Tasks ---

def product_researcher_agent(query):
    """Product researcher agent gathers product information."""
    system_prompt = """You are a product research agent for a retail company. Your task is to provide 
    structured information about products, market trends, and competitor pricing."""
    
    user_prompt = f"Research this product thoroughly: {query}"
    return call_openai(system_prompt, user_prompt)


def customer_analyzer_agent(query):
    """Customer analyzer agent processes customer data and feedback."""
    system_prompt = """You are a customer analysis agent. Your task is to analyze customer feedback, 
    preferences, and purchasing patterns."""
    
    user_prompt = f"Analyze customer behavior for: {query}"
    return call_openai(system_prompt, user_prompt)


def pricing_strategist_agent(query, product_data=None, customer_data=None):
    """Pricing strategist agent recommends optimal pricing."""
    system_prompt = """You are a pricing strategist agent. Your task is to recommend optimal pricing 
    strategies based on product research and customer analysis."""
    
    # TODO: Implement this function
    # It should use product_data and customer_data to inform the pricing strategy
    user_prompt = f"Based on the following data, recommend a pricing strategy for: {query}\n\nProduct Data: {product_data}\n\nCustomer Data: {customer_data}"
    return call_openai(system_prompt, user_prompt)


# --- Routing Agent with LLM-Based Task Determination ---
def routing_agent(query, *args):
    """Routing agent that determines which agent to use based on the query."""
    
    # TODO: Implement the routing agent
    # 1. Use an LLM to analyze the query and determine the correct task type
    # 2. Route the query to the appropriate agent
    # 3. Return the results from the chosen agent
    system_prompt = """You are a routing agent that determines which specialized agent to use based on the user's query.
    The available agents are:
    1. Product Researcher Agent: Gathers product information and market trends.
    2. Customer Analyzer Agent: Analyzes customer feedback and purchasing patterns.
    3. Pricing Strategist Agent: Recommends optimal pricing strategies based on product and customer data.
    Based on the user's query, decide which agent is best suited to handle the request.
    
    Output only the name of the agent (e.g., 'Product Researcher Agent') without any additional text."""

    user_prompt = f"Given the query: '{query}', which agent should handle this task? Respond with the agent name only."
    agent_choice_name = call_openai(system_prompt, user_prompt).strip()
    agent_functions = {
        "Product Researcher Agent": product_researcher_agent,
        "Customer Analyzer Agent": customer_analyzer_agent,
        "Pricing Strategist Agent": pricing_strategist_agent
    }
    if agent_choice_name in agent_functions:
        print(f"--- Routing query to {agent_choice_name}... ---")
        if agent_choice_name == "Pricing Strategist Agent":
            # For Pricing Strategist, we need to gather data from the other two agents first
            product_data = product_researcher_agent(query)
            customer_data = customer_analyzer_agent(query)
            return pricing_strategist_agent(query, product_data, customer_data)
        else:
            return agent_functions[agent_choice_name](query)
    else:
        return f"Error: Could not find an agent named '{agent_choice_name}'. Please check the routing prompt."

# --- Example Usage ---
if __name__ == "__main__":
    # Example queries
    queries = [
        "What are the specifications and current market trends for wireless earbuds?",
        "What do customers think about our premium coffee brand?",
        "What should be the optimal price for our new organic skincare line?"
    ]
    
    # Process each query
    for query in queries:
        print(f"\nQuery: {query}")
        print("\nProcessing...")
        
        # TODO: Use the routing agent to process the query
        result = routing_agent(query)
        print("\nResult:\n", result)
