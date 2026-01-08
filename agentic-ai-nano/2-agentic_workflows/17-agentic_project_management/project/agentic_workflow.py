# agentic_workflow.py

import os
from dotenv import load_dotenv
from workflow_agents.base_agents import ActionPlanningAgent, KnowledgeAugmentedPromptAgent, EvaluationAgent, RoutingAgent

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# load the product spec
with open("Product-Spec-Email-Router.txt", "r") as file:
    product_spec = file.read()

# Instantiate all the agents

# Action Planning Agent
knowledge_action_planning = (
    "Stories are defined from a product spec by identifying a "
    "persona, an action, and a desired outcome for each story. "
    "Each story represents a specific functionality of the product "
    "described in the specification. \n"
    "Features are defined by grouping related user stories. \n"
    "Tasks are defined for each story and represent the engineering "
    "work required to develop the product. \n"
    "A development Plan for a product contains all these components"
)
action_planning_agent = ActionPlanningAgent(
    openai_api_key,
    knowledge_action_planning
)

# Product Manager - Knowledge Augmented Prompt Agent
persona_product_manager = "You are a Product Manager, you are responsible for defining the user stories for a product."
knowledge_product_manager = (
    "Stories are defined by writing sentences with a persona, an action, and a desired outcome. "
    "The sentences always start with: As a "
    "Write several stories for the product spec below, where the personas are the different users of the product. "
    f"Product Specification: {product_spec}"
)
product_manager_knowledge_agent = KnowledgeAugmentedPromptAgent(
    openai_api_key,
    persona_product_manager,
    knowledge_product_manager
)

# Product Manager - Evaluation Agent
product_manager_persona_eval = "You are a product manager evaluation agent that evaluates user stories for clarity and completeness."
product_manager_evaluation_criteria = (
    "The answer should be user stories that follow the following structure: "
    "As a [type of user], I want [an action or feature] so that [benefit/value]."
)
product_manager_evaluation_agent = EvaluationAgent(
    openai_api_key,
    product_manager_persona_eval,
    product_manager_evaluation_criteria,
    worker_agent=product_manager_knowledge_agent,
    max_interactions=10
)

# Program Manager - Knowledge Augmented Prompt Agent
persona_program_manager = "You are a Program Manager, you are responsible for defining the features for a product."
knowledge_program_manager = "Features of a product are defined by organizing similar user stories into cohesive groups."
program_manager_knowledge_agent = KnowledgeAugmentedPromptAgent(
    openai_api_key,
    persona_program_manager,
    knowledge_program_manager
)

# Program Manager - Evaluation Agent
persona_program_manager_eval = "You are an evaluation agent that checks the answers of other worker agents."

program_manager_evaluation_criteria = (
    "The answer should be product features that follow the following structure: "
    "Feature Name: A clear, concise title that identifies the capability\n"
    "Description: A brief explanation of what the feature does and its purpose\n"
    "Key Functionality: The specific capabilities or actions the feature provides\n"
    "User Benefit: How this feature creates value for the user"
)
program_manager_evaluation_agent = EvaluationAgent(
    openai_api_key,
    persona_program_manager_eval,
    program_manager_evaluation_criteria,
    worker_agent=program_manager_knowledge_agent,
    max_interactions=10
)

# Development Engineer - Knowledge Augmented Prompt Agent
persona_dev_engineer = "You are a Development Engineer, you are responsible for defining the development tasks for a product."
knowledge_dev_engineer = "Development tasks are defined by identifying what needs to be built to implement each user story."
development_engineer_knowledge_agent = KnowledgeAugmentedPromptAgent(
    openai_api_key,
    persona_dev_engineer,
    knowledge_dev_engineer
)

# Development Engineer - Evaluation Agent
persona_dev_engineer_eval = "You are an evaluation agent that checks the answers of other worker agents."
dev_engineer_evaluation_criteria = (
    "The answer should be tasks following this exact structure: "
    "Task ID: A unique identifier for tracking purposes\n"
    "Task Title: Brief description of the specific development work\n"
    "Related User Story: Reference to the parent user story\n"
    "Description: Detailed explanation of the technical work required\n"
    "Acceptance Criteria: Specific requirements that must be met for completion\n"
    "Estimated Effort: Time or complexity estimation\n"
    "Dependencies: Any tasks that must be completed first"
)
development_engineer_evaluation_agent = EvaluationAgent(
    openai_api_key,
    persona_dev_engineer_eval,
    dev_engineer_evaluation_criteria,
    worker_agent=development_engineer_knowledge_agent,
    max_interactions=10
)


# Routing Agent
routing_agent = RoutingAgent(
    openai_api_key=openai_api_key,
    agents=[
        {
            "name": "Product Manager",
            "description": "Defines user stories for the product.",
            "func": product_manager_knowledge_agent.respond
        },
        {
            "name": "Program Manager",
            "description": "Defines features for the product.",
            "func": program_manager_knowledge_agent.respond
        },
        {
            "name": "Development Engineer",
            "description": "Defines development tasks for the product.",
            "func": development_engineer_knowledge_agent.respond
        }
    ]
)

# Job function persona support functions
def product_manager_support_function(query: str) -> str:
    response = product_manager_knowledge_agent.respond(query)
    evaluated_response = product_manager_evaluation_agent.evaluate(response)
    return evaluated_response["final_response"]

def program_manager_support_function(query: str) -> str:
    response = program_manager_knowledge_agent.respond(query)
    evaluated_response = program_manager_evaluation_agent.evaluate(response)
    return evaluated_response["final_response"]

def development_engineer_support_function(query: str) -> str:
    response = development_engineer_knowledge_agent.respond(query)
    evaluated_response = development_engineer_evaluation_agent.evaluate(response)
    return evaluated_response["final_response"]

routing_agent.agents[0]["func"] = product_manager_support_function
routing_agent.agents[1]["func"] = program_manager_support_function
routing_agent.agents[2]["func"] = development_engineer_support_function

# Run the workflow

print("\n*** Workflow execution started ***\n")
# Workflow Prompt
# ****
workflow_prompt = "What would the development tasks for this product be?"
# ****
print(f"Task to complete in this workflow, workflow prompt = {workflow_prompt}")

print("\nDefining workflow steps from the workflow prompt")
workflow_steps = action_planning_agent.extract_steps_from_prompt(workflow_prompt)
print(f"Workflow steps defined: {workflow_steps}")
completed_steps = []
for step in workflow_steps:
    print(f"\nExecuting step: {step}")
    routed_response = routing_agent.route(step)
    completed_steps.append(routed_response)
    print(f"Step result: {routed_response}")
print(f"\n*** Workflow execution completed ***\nFinal output: {completed_steps[-1]}")
