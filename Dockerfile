# Use the official Python image as a base image
FROM python:3.10

# Set the working directory in the container
WORKDIR /llm_automation_agent

# Copy the entire application into the container
COPY . .

# Install dependencies directly in the Dockerfile
RUN pip install --no-cache-dir fastapi uvicorn requests uv

# Expose the port FastAPI runs on
EXPOSE 8000

# Command to run the FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
