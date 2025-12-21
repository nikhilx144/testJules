FROM python:3.12-slim

# Set environment variables
# PYTHONUNBUFFERED=1 ensures that Python output is sent straight to terminal (e.g. your container logs)
# without being first buffered and that you can see the output of your application (e.g. django logs) in real time.
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install system dependencies if needed (e.g. for potential future pdf tools, though PyPDF2 is pure python)
# RUN apt-get update && apt-get install -y build-essential curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose the port Streamlit will run on
EXPOSE 8080

# Run Streamlit
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8080", "--server.address=0.0.0.0"]
