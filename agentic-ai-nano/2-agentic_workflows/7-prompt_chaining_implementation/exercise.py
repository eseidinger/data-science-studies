import os
from openai import OpenAI  # type: ignore
from dotenv import load_dotenv  # type: ignore
import json

# Load environment variables and initialize OpenAI client
load_dotenv()
client = OpenAI(
    # base_url="https://openai.vocareum.com/v1",
    api_key=os.getenv("OPENAI_API_KEY"))

def call_openai(system_prompt, user_prompt, model="gpt-3.5-turbo"):
    """Simple wrapper for OpenAI API calls"""
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0
    )
    return response.choices[0].message.content

def feedstock_analyst_agent(feedstock_name):
    # Analyze the hydrocarbon feed
    system_prompt = """You are a chemical engineer specializing in hydrocarbon feedstock analysis.
    Provide a detailed analysis of the given feedstock including composition, properties, and potential challenges.
    """
    user_prompt = f"Analyze the following feedstock: {feedstock_name}"
    print(f"Feedstock Analyst agent analyzing: {feedstock_name}")
    return call_openai(system_prompt, user_prompt)

def distillation_planner_agent(feedstock_analysis):
    # Allocate through distillation tower
    system_prompt = """You are a process engineer specializing in distillation planning.
    Based on the feedstock analysis, create a distillation plan that outlines the separation of components.
    """
    user_prompt = f"""Create a distillation plan based on this feedstock analysis:
    {feedstock_analysis}
    """
    print("Distillation Planner agent creating plan.")
    return call_openai(system_prompt, user_prompt)

def market_analyst_agent(product_list):
    # Analyze market conditions
    system_prompt = """You are a market analyst specializing in hydrocarbon products.
    Provide insights on current market conditions, demand, and pricing for the given products.
    """
    user_prompt = f"Analyze the market for these products: {product_list}"
    print("Market Analyst agent analyzing market conditions.")
    return call_openai(system_prompt, user_prompt)

def production_optimizer_agent(distillation_plan, market_data):
    # Recommend a production plan
    system_prompt = """You are a production optimization specialist.
    Using the distillation plan and market data, recommend an optimal production plan to maximize profitability.
    Output the list in the format:
    {
        "products": ["Product A", "Product B", ...]
    }
    """
    user_prompt = f"""Based on the following distillation plan and market data, recommend a production plan:
    Distillation Plan:
    {distillation_plan}
    Market Data:
    {market_data}
    """
    print("Production Optimizer agent recommending production plan.")
    response = call_openai(system_prompt, user_prompt)
    # Extract product list from response
    product_list = json.loads(response)["products"]
    return product_list

def run_agent_chain(feedstock_name):
    """Run the full agent chain for hydrocarbon feedstock processing"""
    print(f"\nStarting agent chain for feedstock: '{feedstock_name}'")
    
    # Step 1: Feedstock Analysis
    feedstock_analysis = feedstock_analyst_agent(feedstock_name)
    print("\nFeedstock analysis complete!")
    
    # Step 2: Distillation Planning
    distillation_plan = distillation_planner_agent(feedstock_analysis)
    print("\nDistillation planning complete!")
    
    # Step 3: Market Analysis
    market_data = market_analyst_agent("List of potential hydrocarbon products")
    print("\nMarket analysis complete!")
    
    # Step 4: Production Optimization
    product_list = production_optimizer_agent(distillation_plan, market_data)
    print("\nProduction optimization complete!")
    
    # Print results
    print("\n===== FEEDSTOCK ANALYSIS =====")
    print(feedstock_analysis)
    
    print("\n===== DISTILLATION PLAN =====")
    print(distillation_plan)
    
    print("\n===== MARKET DATA =====")
    print(market_data)
    
    print("\n===== RECOMMENDED PRODUCTS =====")
    print(product_list)
    
    return {
        "feedstock_analysis": feedstock_analysis,
        "distillation_plan": distillation_plan,
        "market_data": market_data,
        "recommended_products": product_list
    }

# Run the example
if __name__ == "__main__":
    run_agent_chain("Light Crude Oil")
