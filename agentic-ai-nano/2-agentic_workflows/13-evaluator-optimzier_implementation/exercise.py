import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()
client = OpenAI(
    # base_url = "https://openai.vocareum.com/v1",
    api_key=os.getenv("OPENAI_API_KEY"))

MAX_RETRIES = 5

# Example user constraints
RECIPE_REQUEST = {
    "base_dish": "pasta",
    "constraints": [
        "gluten-free",
        "vegan",
        "under 500 calories per serving",
        "high protein (>15g per serving)",
        "no coconut",
        "taste must be rated 7/10 or higher"
    ]
}

class RecipeAgent:
    def run(self, request, feedback=None):
        system_message = "You are a gourmet chef creating recipes based on user constraints."

        # Construct the prompt
        constraints_text = "\n".join(f"- {c}" for c in request["constraints"])
        full_prompt = (
            f"Create a recipe for {request['base_dish']} that meets the following constraints:\n"
            f"{constraints_text}"
        )

        # Modify the prompt if feedback is provided
        if feedback:
            full_prompt += f"\n\nEvaluator feedback: {feedback}\nPlease revise accordingly."

        print(f"\n🍽️ Generating recipe with prompt:\n{full_prompt}\n")
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": full_prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    
class NutritionEvaluator:
    def run(self, recipe_text):
        print("🔍 Evaluating recipe nutrition...")
        system_message = (
            "You are a nutritionist evaluating recipes for dietary compliance. "
            "Check if the recipe meets the specified constraints and provide feedback if it does not."
        )

        eval_prompt = f"Evaluate this recipe for compliance with the user's constraints:\n\n{recipe_text}\n\nRespond with 'Approved' or provide feedback for revision."

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": eval_prompt}
            ],
            temperature=0.0
        )
        return response.choices[0].message.content.strip()
    
def main():
    recipe_agent = RecipeAgent()
    evaluator = NutritionEvaluator()

    recipe_text = ""
    feedback = None

    for attempt in range(MAX_RETRIES):
        print(f"--- Attempt #{attempt} ---")
        recipe_text = recipe_agent.run(RECIPE_REQUEST, feedback)
        evaluation = evaluator.run(recipe_text)

        print(f"\n🍴 Evaluation Result:\n{evaluation}\n")

        if evaluation.lower().startswith("approved"):
            print("\n✅ Final Approved Recipe:\n")
            print(recipe_text)
            break
        else:
            feedback = evaluation
    else:
        print("\n❌ Failed to meet constraints after max retries.")
        print("Last version of the recipe:")
        print(recipe_text)

if __name__ == "__main__":
    main()