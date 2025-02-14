# Use Ubuntu as base image
FROM ubuntu:22.04 as base

# Set non-interactive mode to prevent prompts
ENV DEBIAN_FRONTEND=noninteractive

# Update system packages and install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    python3.10 \
    python3-pip \
    sqlite3 \
    git \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install latest Node.js LTS from Nodesource
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs

# Verify installation
RUN node -v && npm -v

# Install uv (Python package manager)
RUN pip3 install uv

# Use a dedicated builder stage for dependencies
FROM base as builder

# Install Python dependencies using uv (with --system flag)
RUN --mount=type=cache,target=/root/.cache \
    uv pip install --system --compile \
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

# Final runtime image
FROM base as final

# Set working directory
WORKDIR /llm_automation_agent

# Copy installed dependencies from builder stage
COPY --from=builder /usr/local /usr/local

# Copy application files
COPY . .

# Expose port for FastAPI
EXPOSE 8000

# Start the FastAPI server
CMD ["uvicorn", "app:main", "--host", "0.0.0.0", "--port", "8000"]
