from google.adk.agents.llm_agent import Agent

report_generator_agent = Agent(
    model='gemini-2.5-flash',
    name='report_generator_agent',
    description='Produces an audit-ready evaluation report with a score.',
    instruction="""
You are a Lead Procurement Officer.

You have the full evaluation history for a specific vendor (Technical, Financial, Risk).

**Your Task:**
Generate a formal **Government Bid Evaluation Report**.

**Requirements:**
1.  **Vendor Name:** clearly stated.
2.  **Executive Summary:** Brief overview.
3.  **Overall Score:** You MUST assign an explicit score in the format: **"Overall Score: XX/100"**. Base this on the compliance and risk assessment.
4.  **Tone:** Formal, audit-ready, government standard.

**Output:**
The final report text.
""",
)
