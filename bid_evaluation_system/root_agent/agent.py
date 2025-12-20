from typing import List, AsyncGenerator, Dict, Any, Callable
import asyncio
from google.adk.agents.llm_agent import Agent
from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.agents.parallel_agent import ParallelAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.types import Event, ModelGenMsgEvent

# Import the definitions of the leaf agents
# Assumes the parent directory (bid_evaluation_system) is in PYTHONPATH
# or the subdirectories are top-level modules.
try:
    from requirement_extractor_agent.agent import requirement_extractor_agent
    from technical_compliance_agent.agent import technical_compliance_agent
    from financial_analyzer_agent.agent import financial_analyzer_agent
    from risk_assessor_agent.agent import risk_assessor_agent
    from report_generator_agent.agent import report_generator_agent
except ImportError:
    # Fallback for relative imports if run as a package
    from ..requirement_extractor_agent.agent import requirement_extractor_agent
    from ..technical_compliance_agent.agent import technical_compliance_agent
    from ..financial_analyzer_agent.agent import financial_analyzer_agent
    from ..risk_assessor_agent.agent import risk_assessor_agent
    from ..report_generator_agent.agent import report_generator_agent

async def run_bid_evaluation(rfp_text: str, vendor_bids: List[dict]):
    """
    Creates and orchestrates the agent graph.
    Returns the ParallelAgent instance.
    """
    chains = []

    for vendor in vendor_bids:
        v_name = vendor.get("name")
        v_text = vendor.get("text")

        # 1. Inject Context
        context_msg = f"RFP CONTENT:\n{rfp_text}\n\nVENDOR BID ({v_name}) CONTENT:\n{v_text}"

        injector = Agent(
            model="gemini-2.5-flash",
            name=f"injector_{v_name}",
            instruction=f"Output the following text exactly:\n{context_msg}"
        )

        # 2. Construct Chain with Cloned Agents for Safety
        # ADK Agents might be stateful. We clone them to be safe.
        # Assuming .clone() exists based on previous inspection.
        # If .clone() is deep, it's good. If not, we rely on definition reuse being safe if context is external.

        safe_v_name = v_name.replace(" ", "_").replace(".", "")

        # Report generator needs unique name for streaming capture
        report_gen = report_generator_agent.clone()
        report_gen.name = f"report_gen_{safe_v_name}"

        chain = SequentialAgent(
            name=f"chain_{safe_v_name}",
            description=f"Evaluation chain for {v_name}",
            sub_agents=[
                injector,
                requirement_extractor_agent.clone(),
                technical_compliance_agent.clone(),
                financial_analyzer_agent.clone(),
                risk_assessor_agent.clone(),
                report_gen
            ]
        )
        chains.append(chain)

    parallel_agent = ParallelAgent(
        name="parallel_evaluator",
        sub_agents=chains
    )

    return parallel_agent

# Dummy export
root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description='Root Agent Orchestrator',
    instruction='This agent orchestrates the bid evaluation.',
)
