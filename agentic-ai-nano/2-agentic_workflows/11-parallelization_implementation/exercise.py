import os
from openai import OpenAI
from dotenv import load_dotenv
import threading

# Load environment variables and initialize OpenAI client
load_dotenv()
client = OpenAI(
    # base_url = "https://openai.vocareum.com/v1",
    api_key=os.getenv("OPENAI_API_KEY"))

# Shared dict for thread-safe collection of agent outputs
agent_outputs = {}

# Example contract text (in a real application, this would be loaded from a file)
contract_text = """
CONSULTING AGREEMENT

This Consulting Agreement (the "Agreement") is made effective as of January 1, 2025 (the "Effective Date"), by and between ABC Corporation, a Delaware corporation ("Client"), and XYZ Consulting LLC, a California limited liability company ("Consultant").

1. SERVICES. Consultant shall provide Client with the following services: strategic business consulting, market analysis, and technology implementation advice (the "Services").

2. TERM. This Agreement shall commence on the Effective Date and shall continue for a period of 12 months, unless earlier terminated.

3. COMPENSATION. Client shall pay Consultant a fee of $10,000 per month for Services rendered. Payment shall be made within 30 days of receipt of Consultant's invoice.

4. CONFIDENTIALITY. Consultant acknowledges that during the engagement, Consultant may have access to confidential information. Consultant agrees to maintain the confidentiality of all such information.

5. INTELLECTUAL PROPERTY. All materials developed by Consultant shall be the property of Client. Consultant assigns all right, title, and interest in such materials to Client.

6. TERMINATION. Either party may terminate this Agreement with 30 days' written notice. Client shall pay Consultant for Services performed through the termination date.

7. GOVERNING LAW. This Agreement shall be governed by the laws of the State of Delaware.

8. LIMITATION OF LIABILITY. Consultant's liability shall be limited to the amount of fees paid by Client under this Agreement.

9. INDEMNIFICATION. Client shall indemnify Consultant against all claims arising from use of materials provided by Client.

10. ENTIRE AGREEMENT. This Agreement constitutes the entire understanding between the parties and supersedes all prior agreements.

IN WITNESS WHEREOF, the parties have executed this Agreement as of the date first above written.
"""

# TODO: Implement these agent classes

class LegalTermsChecker:
    """Agent that checks for problematic legal terms and clauses in contracts."""
    def run(self, contract_text):
        # TODO: Implement this method to analyze legal terms
        system_prompt = "You are a legal expert specializing in contract law. Identify any problematic or unusual legal terms and clauses in the provided contract text."
        user_prompt = f"Analyze the following contract text for problematic legal terms:\n\n{contract_text}"
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7
        )
        agent_outputs["legal_terms"] = response.choices[0].message.content

class ComplianceValidator:
    """Agent that validates regulatory and industry compliance of contracts."""
    def run(self, contract_text):
        # TODO: Implement this method to check compliance
        system_prompt = "You are a compliance expert specializing in regulatory and industry standards. Evaluate the provided contract text for compliance issues."
        user_prompt = f"Analyze the following contract text for regulatory and industry compliance:\n\n{contract_text}"
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7
        )
        agent_outputs["compliance"] = response.choices[0].message.content

class FinancialRiskAssessor:
    """Agent that assesses financial risks and liabilities in contracts."""
    def run(self, contract_text):
        # TODO: Implement this method to evaluate financial risks
        system_prompt = "You are a financial risk expert specializing in contract liabilities. Assess the provided contract text for financial risks and liabilities."
        user_prompt = f"Analyze the following contract text for financial risks and liabilities:\n\n{contract_text}"
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7
        )
        agent_outputs["financial_risks"] = response.choices[0].message.content

class SummaryAgent:
    """Agent that synthesizes findings from all specialized agents."""
    def run(self, contract_text, inputs):
        # TODO: Implement this method to create a comprehensive summary
        combined_prompt = (
            f"The contract text is as follows:\n\n{contract_text}\n\n"
            f"The findings from the specialized agents are:\n"
            f"- Legal Terms Checker: {inputs['legal_terms']}\n\n"
            f"- Compliance Validator: {inputs['compliance']}\n\n"
            f"- Financial Risk Assessor: {inputs['financial_risks']}\n\n"
            "Please provide a comprehensive summary of the contract analysis."
        )
        system_prompt = "You are a contract analysis expert skilled at synthesizing insights from various domains."
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": combined_prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content

# Main function to run all agents in parallel
def analyze_contract(contract_text):
    """Run all agents in parallel and summarize their findings."""
    # TODO: Implement parallel execution of agents
    # 1. Create agent instances
    # 2. Run them in parallel using threading
    # 3. Collect their outputs
    # 4. Generate a summary using the SummaryAgent
    # 5. Return the final analysis
    legal_agent = LegalTermsChecker()
    compliance_agent = ComplianceValidator()
    financial_agent = FinancialRiskAssessor()
    summary_agent = SummaryAgent()
    threads = [
        threading.Thread(target=legal_agent.run, args=(contract_text,)),
        threading.Thread(target=compliance_agent.run, args=(contract_text,)),
        threading.Thread(target=financial_agent.run, args=(contract_text,))
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    final_summary = summary_agent.run(contract_text, agent_outputs)
    return final_summary

if __name__ == "__main__":
    print("Enterprise Contract Analysis System")
    print("Analyzing contract...")
    
    # TODO: Call the analyze_contract function and print results
    final_analysis = analyze_contract(contract_text)
    print("\n=== FINAL CONTRACT ANALYSIS ===\n")
    print(final_analysis)