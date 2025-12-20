import streamlit as st
import asyncio
import re
from google.adk.types import ModelGenMsgEvent
import sys
import os

# Add the directory containing the agent modules to sys.path
# This makes 'root_agent', 'requirement_extractor_agent', etc. importable as top-level modules.
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from root_agent.agent import run_bid_evaluation
from google.adk.agents.invocation_context import InvocationContext

st.set_page_config(page_title="Autonomous Bid Evaluation System", layout="wide")

st.title("🏛️ Autonomous AI-Powered Government Bid Evaluation System")

# Sidebar
st.sidebar.header("1. Upload RFP")
rfp_file = st.sidebar.file_uploader("Upload RFP", type=["txt"])
rfp_text = rfp_file.read().decode("utf-8") if rfp_file else ""

st.sidebar.header("2. Upload Vendor Bids")
bid_files = st.sidebar.file_uploader("Upload Bids", type=["txt"], accept_multiple_files=True)
vendor_bids = []
if bid_files:
    for f in bid_files:
        vendor_bids.append({"name": f.name.split('.')[0], "text": f.read().decode("utf-8")})

def extract_score(text):
    match = re.search(r"Overall Score:\s*(\d+)/100", text)
    if match:
        return int(match.group(1))
    return 0

if st.button("🚀 Start Evaluation"):
    if not rfp_text or not vendor_bids:
        st.error("Please upload RFP and Bids.")
    else:
        st.info("Initializing Agents...")

        async def run_and_capture():
            parallel_agent = await run_bid_evaluation(rfp_text, vendor_bids)
            ctx = InvocationContext()

            accumulators = {} # agent_name -> text

            # Use columns for logs if needed, or just status
            status = st.empty()

            try:
                # Iterate over the async generator
                async for event in parallel_agent.run_async(ctx):
                    if isinstance(event, ModelGenMsgEvent):
                        # Attempt to identify source agent.
                        # We try both 'source' and 'agent_name' attributes.
                        source = getattr(event, 'source', None)
                        if not source:
                            source = getattr(event, 'agent_name', None)

                        # Only capture from report generators
                        if source and str(source).startswith("report_gen_"):
                            if source not in accumulators:
                                accumulators[source] = ""
                            accumulators[source] += event.text
                            status.text(f"Processing report for {source}...")

            except Exception as e:
                st.error(f"Execution Error: {e}")

            return accumulators

        # Run the loop
        raw_reports = asyncio.run(run_and_capture())

        if raw_reports:
            st.success("Evaluation Complete!")

            # Process Results
            results_data = []
            for agent_name, report_text in raw_reports.items():
                v_name = agent_name.replace("report_gen_", "").replace("_", " ")
                score = extract_score(report_text)
                results_data.append({"Vendor": v_name, "Score": score, "Report": report_text})

            # Sort
            results_data.sort(key=lambda x: x["Score"], reverse=True)

            # Display Ranking
            st.subheader("🏆 Vendor Ranking")
            st.dataframe(results_data)

            # Downloadable Reports
            st.subheader("📄 Detailed Reports")
            for res in results_data:
                with st.expander(f"{res['Vendor']} - Score: {res['Score']}/100"):
                    st.markdown(res['Report'])
                    st.download_button(
                        label=f"Download Report ({res['Vendor']})",
                        data=res['Report'],
                        file_name=f"{res['Vendor']}_Evaluation_Report.md",
                        mime="text/markdown"
                    )
        else:
            st.warning("No reports generated. If this is a test without valid credentials, this is expected.")

st.markdown("---")
st.markdown("Developed with Google ADK")
