# Use the official Python 3.11 base image
FROM python:3.11-slim

# Set environment variables to avoid prompts during install
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy the local folder contents into the container
COPY . .

# Install Torch dependencies
RUN pip install --no-cache-dir \
  torch==2.7.0 \
  torchaudio==2.7.0 \
  torchvision==0.22.0 \
  --index-url https://download.pytorch.org/whl/cpu

RUN pip install build

RUN python -m build

RUN pip install -e .

RUN pip install streamlit

EXPOSE 8501

# Command to run the Streamlit app
CMD ["streamlit", "run", "app.py"]
