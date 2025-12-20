
# Autonomous AI-Powered Government Bid Evaluation System

This project is an autonomous bid evaluation system built with the Google Agent Development Kit (ADK) and Gemini 2.5 Flash. It evaluates multiple vendor bids against a single RFP using a multi-agent workflow.

## Structure

*   `root_agent/`: The orchestrator agent.
*   `requirement_extractor_agent/`: Extracts requirements from RFP.
*   `technical_compliance_agent/`: Checks technical compliance.
*   `financial_analyzer_agent/`: Analyzes financial aspects.
*   `risk_assessor_agent/`: Assesses risks.
*   `report_generator_agent/`: Generates the final scored report.
*   `streamlit_app.py`: The user interface.

## Creation Commands (ADK)

The following commands were used to create the agents:

```bash
adk create requirement_extractor_agent
adk create technical_compliance_agent
adk create financial_analyzer_agent
adk create risk_assessor_agent
adk create report_generator_agent
adk create root_agent
```

(Interactive inputs were provided: Model: `gemini-2.5-flash`, Backend: `Vertex AI`, Project ID: `<your-project-id>`, Region: `us-central1`)

## Deployment (Cloud Run)

1.  **Build the container:**
    ```bash
    gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/bid-eval-system
    ```

2.  **Deploy:**
    ```bash
    gcloud run deploy bid-eval-system --image gcr.io/YOUR_PROJECT_ID/bid-eval-system --platform managed --allow-unauthenticated
    ```

## Running Locally

1.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

2.  Run the app:
    ```bash
    streamlit run streamlit_app.py
    ```
