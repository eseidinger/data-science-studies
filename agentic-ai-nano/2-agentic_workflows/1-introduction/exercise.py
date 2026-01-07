"""
Program Management Knowledge Agent - Starter Code

This program demonstrates two approaches to answering program management questions:
1. Using hardcoded knowledge
2. Using an LLM API

Complete the TODOs to build your knowledge agent.
"""

from openai import OpenAI
import os
import dotenv

# TODO: Initialize the OpenAI client if API key is available
# Hint: Use os.getenv() to get the API key from environment variables

dotenv.load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
llm_client = None
if api_key:
    llm_client = OpenAI(api_key=api_key)

def get_hardcoded_answer(question):
    """
    Return answers to program management questions using hardcoded knowledge.
    
    Args:
        question (str): The question about program management
        
    Returns:
        str: The answer to the question
    """
    # TODO: Convert question to lowercase for easier matching
    question_lower = question.lower()
    
    # TODO: Implement responses for at least 5 common program management questions
    # Include questions about: Gantt charts, Agile, sprints, critical path, and milestones
    if "gantt chart" in question_lower:
        return "A Gantt chart is a visual representation of a project schedule, showing tasks over time."
    elif "agile" in question_lower:
        return "Agile is a project management methodology that emphasizes flexibility, collaboration, and customer feedback."
    elif "sprint" in question_lower:
        return "A sprint is a set period during which specific work has to be completed and made ready for review in Agile methodology."
    elif "critical path" in question_lower:
        return "The critical path is the sequence of stages determining the minimum time needed for an operation."
    elif "milestone" in question_lower:
        return "A milestone is a significant point or event in a project timeline that marks the completion of a major phase."
    
    # TODO: Add a default response for questions not in your knowledge base
    return "I'm sorry, I don't have an answer for that question at the moment."

def get_llm_answer(question):
    """
    Get answers to program management questions using an LLM API.
    
    Args:
        question (str): The question about program management
        
    Returns:
        str: The answer from the LLM
    """
    # TODO: Check if the LLM client is initialized
    if llm_client is None:
        return "LLM API key not found. Please set the OPENAI_API_KEY environment variable."
    
    # TODO: Implement the API call to get an answer from the LLM
    # Use a system message to specify that the LLM should act as a program management expert
    
    try:
        response = llm_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a knowledgeable program management expert."},
                {"role": "user", "content": question}
            ]
        )
    # TODO: Add error handling for API calls
    except Exception as e:
        return f"Error fetching answer from LLM: {e}"

    return response.choices[0].message.content

# Demo function to compare both approaches
def compare_answers(question):
    """Compare answers from both approaches for a given question."""
    print(f"\nQuestion: {question}")
    print("-" * 50)
    
    # TODO: Get and display the hardcoded answer
    hardcoded_answer = get_hardcoded_answer(question)
    print(f"Hardcoded Answer:\n{hardcoded_answer}")
    print("-" * 50)
    
    # TODO: Get and display the LLM answer (or a placeholder message)
    llm_answer = get_llm_answer(question)
    print(f"LLM Answer:\n{llm_answer}")
    
    print("=" * 50)

# Demo with sample questions
if __name__ == "__main__":
    print("PROGRAM MANAGEMENT KNOWLEDGE AGENT DEMO")
    print("=" * 50)
    
    # TODO: Create a list of sample program management questions
    sample_questions = [
        "What is a Gantt chart?",
        "What is Agile?",
        "What is the difference between a program and a project?",
        "What is a sprint?",
        "What is the critical path?"
    ]
    
    # TODO: Loop through the questions and compare answers
    for question in sample_questions:
        compare_answers(question)