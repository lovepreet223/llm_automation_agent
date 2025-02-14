# Base image: Use Ubuntu for flexibility
FROM ubuntu:22.04 as base

# Set non-interactive mode for APT to avoid prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    nodejs \
    npm \
    python3.10 \
    python3-pip \
    sqlite3 \
    git \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install uv (fast package manager)
RUN pip3 install uv

# Use a dedicated builder stage for dependencies to enable caching
FROM base as builder

# Install required Python dependencies using uv (with --system)
RUN --mount=type=cache,target=/root/.cache \
    uv pip install --system --no-deps --compile \
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

# Install Prettier globally (via npm)
RUN npm install -g prettier@3.4.2

# Final image (runtime environment)
FROM base as final

# Set the working directory
WORKDIR /llm_automation_agent

# Copy installed dependencies from the builder stage
COPY --from=builder /usr/local /usr/local

# Copy application files
COPY . .

# Expose port for FastAPI
EXPOSE 8000

# Start the FastAPI server
CMD ["uvicorn", "app:main", "--host", "0.0.0.0", "--port", "8000"]
