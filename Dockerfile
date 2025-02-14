# Use the official Python image as a base image
FROM python:3.10

# Install required packages
RUN apt-get update && apt-get install -y \
    curl \
    python3 \
    python3-pip \
    sqlite3 \
    git \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - && \
    apt-get install -y nodejs

# Install uv (Python package manager) and necessary Python dependencies
RUN pip3 install uv
RUN pip3 install requests numpy pandas duckdb pillow scipy \
    tiktoken gitpython beautifulsoup4 selenium markdown \
    fastapi uvicorn ffmpeg-python


# Install Prettier globally via npm
RUN npm install -g prettier@3.4.2

# Set working directory
WORKDIR /llm_automation_agent

# Copy application files
COPY . .

# Expose port for FastAPI
EXPOSE 8000

# Start the FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]