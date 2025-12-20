import streamlit as st
import asyncio
import re
from google.adk.events.event import Event
import sys
import os
import PyPDF2

# Add the directory containing the agent modules to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from root_agent.agent import run_bid_evaluation
from google.adk.runners import InMemoryRunner
from google.genai import types

st.set_page_config(page_title="Autonomous Bid Evaluation System", layout="wide")

st.title("🏛️ Autonomous AI-Powered Government Bid Evaluation System")

# Sidebar
st.sidebar.header("1. Upload RFP")
rfp_file = st.sidebar.file_uploader("Upload RFP (PDF)", type=["pdf"])
rfp_text = ""

if rfp_file:
    try:
        pdf_reader = PyPDF2.PdfReader(rfp_file)
        for page in pdf_reader.pages:
            rfp_text += page.extract_text() or ""
    except Exception as e:
        st.error(f"Error reading RFP PDF: {e}")

st.sidebar.header("2. Upload Vendor Bids")
bid_files = st.sidebar.file_uploader("Upload Bids (Max 5 PDFs)", type=["pdf"], accept_multiple_files=True)
vendor_bids = []
if bid_files:
    if len(bid_files) > 5:
        st.error("Max 5 vendor bids allowed.")
    else:
        for f in bid_files:
            try:
                text = ""
                pdf_reader = PyPDF2.PdfReader(f)
                for page in pdf_reader.pages:
                    text += page.extract_text() or ""
                vendor_bids.append({"name": f.name.split('.')[0], "text": text})
            except Exception as e:
                st.error(f"Error reading Bid PDF {f.name}: {e}")

def extract_score(text):
    match = re.search(r"Overall Score:\s*(\d+)/100", text)
    if match:
        return int(match.group(1))
    return 0

if st.button("🚀 Start Evaluation"):
    if not rfp_text or not vendor_bids:
        st.error("Please upload RFP and Bids (PDFs).")
    elif len(bid_files) > 5:
        st.error("Max 5 vendor bids allowed.")
    else:
        st.info("Initializing Agents...")

        async def run_and_capture():
            # Get the parallel agent from the orchestrator
            parallel_agent = await run_bid_evaluation(rfp_text, vendor_bids)

            # Use InMemoryRunner to handle context and execution
            runner = InMemoryRunner(agent=parallel_agent)

            accumulators = {} # agent_name -> text
            status = st.empty()

            try:
                # We need to trigger the execution.
                # ParallelAgent typically responds to a user message to start.
                # We'll send a "Start" message.

                async for event in runner.run_async(
                    user_id="user",
                    session_id="session",
                    new_message=types.Content(parts=[types.Part(text="Start Evaluation")])
                ):
                    if isinstance(event, Event):
                        # Attempt to identify source agent.
                        source = getattr(event, 'source', None)
                        if not source:
                            source = getattr(event, 'author', None)

                        # Only capture from report generators
                        if source and str(source).startswith("report_gen_"):
                            if source not in accumulators:
                                accumulators[source] = ""

                            if event.content and event.content.parts:
                                for part in event.content.parts:
                                    if part.text:
                                        accumulators[source] += part.text

                            status.text(f"Processing report for {source}...")
            except Exception as e:
                st.error(f"Execution Error: {e}")
            finally:
                await runner.close()

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
