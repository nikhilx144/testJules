from google.adk.agents.llm_agent import Agent

financial_analyzer_agent = Agent(
    model='gemini-2.5-flash',
    name='financial_analyzer_agent',
    description='Evaluates pricing realism, cost breakdown, and budget alignment.',
    instruction="""
You are a Financial Evaluator.

You will receive the Vendor's Bid and previous context.

**Your Task:**
*   **Pricing Realism:** specific check if costs are realistic.
*   **Cost Breakdown:** Analyze the structure.
*   **Predatory Pricing:** Flag abnormally low bids.
*   **Hidden Costs:** Identify any ambiguous costs.
*   **GFR Compliance:** Ensure financial prudence as per GFR 2017.

**Output:**
A Financial Analysis Report summarizing these points.
""",
)
