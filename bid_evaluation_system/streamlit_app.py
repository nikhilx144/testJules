import streamlit as st
import asyncio
import re
from google.adk.events.event import Event
import sys
import os
import PyPDF2
import traceback
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the directory containing the agent modules to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from root_agent.agent import run_bid_evaluation
from google.adk.runners import InMemoryRunner
from google.genai import types

st.set_page_config(page_title="Autonomous Bid Evaluation System", layout="wide")

st.title("🏛️ Autonomous AI-Powered Government Bid Evaluation System")

# Sidebar - Configuration
with st.sidebar.expander("Configuration", expanded=True):
    project_id = st.text_input("Google Cloud Project ID", value=os.getenv("GOOGLE_CLOUD_PROJECT", ""))
    location = st.text_input("Google Cloud Location", value=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"))

    if project_id:
        os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
    if location:
        os.environ["GOOGLE_CLOUD_LOCATION"] = location

    # Force Vertex AI mode
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "1"

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
    if not project_id:
        st.error("Please enter a Google Cloud Project ID in the Configuration section.")
    elif not rfp_text or not vendor_bids:
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
                # Create session explicitly (Required for run_async)
                await runner.session_service.create_session(
                    app_name=runner.app_name,
                    user_id="user",
                    session_id="session"
                )

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
                # Enhanced Error Logging
                err_msg = f"Execution Error: {e}"

                # Check for ExceptionGroup (Python 3.11+)
                if hasattr(e, 'exceptions'):
                    err_msg += "\n\nSub-exceptions:"
                    for idx, sub_e in enumerate(e.exceptions):
                        err_msg += f"\n{idx+1}. {sub_e}"

                # Full traceback
                trace = traceback.format_exc()

                st.error(err_msg)
                with st.expander("Detailed Traceback"):
                    st.code(trace)

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
            st.warning("No reports generated. Check the error details above.")

st.markdown("---")
st.markdown("Developed with Google ADK")
