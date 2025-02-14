# Use Ubuntu as base image
FROM ubuntu:22.04

# Install required packages
RUN apt-get update && apt-get install -y \
    curl \
    python3 \
    python3-pip \
    sqlite3 \
    git \
    ffmpeg \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Install uv (Python package manager) and necessary Python dependencies
RUN pip3 install uv && uv pip install \
    requests \
    numpy \
    pandas \
    duckdb \
    pillow \
    scipy \
    tiktoken \
    gitpython \
    beautifulsoup4 \
    selenium \
    markdown \
    fastapi \
    uvicorn \
    ffmpeg-python

# Install Prettier globally via npm
RUN npm install -g prettier@3.4.2

# Set working directory
WORKDIR /llm_automation_agent

# Copy application files
COPY . .

# Expose port for FastAPI
EXPOSE 8000

# Start the FastAPI server
CMD ["uvicorn", "app:main", "--host", "0.0.0.0", "--port", "8000"]