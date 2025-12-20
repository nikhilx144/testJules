from google.adk.agents.llm_agent import Agent

requirement_extractor_agent = Agent(
    model='gemini-2.5-flash',
    name='requirement_extractor_agent',
    description='Extracts mandatory and optional requirements from RFP.',
    instruction="""
You are an expert Government Bid Evaluator specialized in GFR 2017 and SBD.

Your task is to analyze the provided Request for Proposal (RFP) text and the current Vendor Bid (if available in context, though primarily focus on RFP).

1.  **Identify Requirements:**
    *   **Mandatory Requirements (Must/Shall):** Extract all non-negotiable clauses.
    *   **Optional Requirements (Should/May):** Extract desirable features.
2.  **Evaluation Criteria:** Identify specific criteria and their weightages.
3.  **Compliance Standards:** Ensure alignment with General Financial Rules (GFR) 2017.

**Output Format:**
Produce a structured summary (Markdown) listing:
*   Mandatory Requirements
*   Optional Requirements
*   Evaluation Weights
""",
)
