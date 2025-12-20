
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

## Setup & Authentication

You do **not** need to use `adk create` if you are using this code directly. However, you must configure authentication and project details.

### 1. Configure Environment Variables
The code includes `.env` files in each agent directory. You must update them with your Google Cloud Project ID.

**Manual Update:**
Open `.env` in each agent folder and set:
```
GOOGLE_CLOUD_PROJECT=your-actual-project-id
```

**Or using sed (Linux/Mac):**
```bash
find . -name ".env" -exec sed -i 's/YOUR_PROJECT_ID/your-actual-project-id/g' {} +
```

### 2. Authentication
This system uses Vertex AI, so you need Application Default Credentials (ADC).

Run the following command in your terminal:
```bash
gcloud auth application-default login
```
(Note: `gcloud auth login` alone is often insufficient for Python client libraries; `application-default` is recommended.)

## Running the System

1.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the Streamlit App:**
    ```bash
    streamlit run streamlit_app.py
    ```

## Deployment (Cloud Run)

1.  **Build the container:**
    ```bash
    gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/bid-eval-system
    ```

2.  **Deploy:**
    ```bash
    gcloud run deploy bid-eval-system --image gcr.io/YOUR_PROJECT_ID/bid-eval-system --platform managed --allow-unauthenticated
    ```
