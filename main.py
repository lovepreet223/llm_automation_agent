from fastapi import FastAPI, HTTPException, Query
import requests
import os
import json
import re
import subprocess

app = FastAPI()

AIPROXY_TOKEN = os.getenv("AIPROXY_TOKEN")  # Load API key from environment
AIPROXY_BASE_URL = "https://aiproxy.sanand.workers.dev/openai"

# Base data directory to prevent accessing files outside /data
BASE_DIR = "/data"


@app.post("/run")
async def run_task(task: str = Query(..., description="Plain English task description")):
    try:
        #For each task empty out the files
        open("output/script.py", "w").close()
        open("output/output.txt", "w").close()
        print("Getting task...")
        response = prompt("prompts/initial_prompt.txt", task)
        print("Getting Script...")
        response_script = prompt("prompts/second_prompt.txt", str(response))
        # When invalid file access is required.
        if "error" in response_script:
            raise HTTPException(status_code=400, detail=f"AIProxy Error: {response['error']}")
        # Extract the response and save into script file
        print("Starting script saving process...")
        print(response_script)
        extract_and_save_script(response_script)
        # Run the script and save the output
        print("Saving output...")
        run_script_and_save_output()

        #Running this part if error occurs or persists.
        flag = False
        while not flag:
            print("Running while loop...")
            code = str(prepare_prompt())
            up_prompt = str(response) + "\ncode + output: " + code
            up_response = prompt("prompts/third_prompt.txt", up_prompt)
            if "success" in up_response:
                flag = True
            else:
                print("Starting script saving process...")
                extract_and_save_script(response_script)
                # Run the script and save the output
                print("Saving output...")
                run_script_and_save_output()
        print("Success")


        # When no appropriate function is found.
        if "error" in response:
            raise HTTPException(status_code=400, detail=f"AIProxy Error: {response['error']}")

    except HTTPException as http_exc:
        raise http_exc  # Re-raise FastAPI-specific exceptions
    except requests.exceptions.RequestException as req_exc:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(req_exc)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/read")
async def read_file(path: str = Query(..., description="Path to the file to be read")):
    """
    Reads the content of a specified file.

    Args:
        path (str): The file path to read.

    Returns:
        HTTP 200 OK with file content if successful.
        HTTP 404 Not Found if the file does not exist.
    """
    #path = ensure_local_path(path)
    # Ensure path is relative to BASE_DIR to avoid duplication
    relative_path = os.path.relpath(path, BASE_DIR)
    safe_path = os.path.abspath(os.path.join(BASE_DIR, relative_path))

    # Security check
    if not safe_path.startswith(os.path.abspath(BASE_DIR)):
        raise HTTPException(status_code=403, detail="Access denied")

    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")

    try:
        with open(path, "r", encoding="utf-8") as file:
            content = file.read()
        return {"status": "success", "content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")

def prompt(file_path, task):
    with open(file_path, 'r', encoding='utf-8') as file:
        prompt = file.read()
    prompt = prompt.replace("{task}", task)

    response = requests.post(
        f"{AIPROXY_BASE_URL}/v1/chat/completions",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {AIPROXY_TOKEN}"
        },
        json={
            "model": "gpt-4o-mini",
            "messages": [{"role": "system", "content": prompt}]
        }
    )

    response.raise_for_status()  # Ensure we got a successful response
    raw_content = response.json()["choices"][0]["message"]["content"].strip()
    # Remove Markdown code block syntax if present
    if raw_content.startswith("```json") and raw_content.endswith("```"):
        raw_content = raw_content[7:-3].strip()  # Remove ` ```json ` and ` ``` `
    # Parse the cleaned JSON string into a Python list
    try:
        cleaned_result = json.loads(raw_content)
    except json.JSONDecodeError:
        cleaned_result = raw_content  # Fallback in case of an error
    # Return the cleaned list or string
    return {"result": cleaned_result}

def extract_and_save_script(response: dict, filename: str = "output/script.py"):
    # Extract the 'result' value
    result = response.get("result", "")
    # Use regex to extract the Python script inside the triple backticks
    match = re.search(r'```python\n(.*?)\n```', result, re.DOTALL)
    if match:
        script_content = match.group(1)
        # Save to a file
        with open(filename, "w", encoding="utf-8") as file:
            file.write(script_content)
        print(f"Script saved to {filename}")
    else:
        print("No valid Python script found in the response.")


def run_script_and_save_output(script_filename: str = "output/script.py", output_filename: str = "output/output.txt"):
    try:
        # Run the script using 'uv run script.py' command
        result = subprocess.run(["uv", "run", script_filename], capture_output=True, text=True)

        # Save the output to a file
        with open(output_filename, "w", encoding="utf-8") as file:
            file.write(result.stdout + "\n" + result.stderr)

        print(f"Output saved to {output_filename}")
    except Exception as e:
        print(f"Error running script: {e}")

def prepare_prompt(script_path = "output/script.py", output_path="output/output.txt"):
    try:
        # Read the script file
        with open(script_path, "r") as script_file:
            script_content = script_file.read()

        # Read the output file
        with open(output_path, "r") as output_file:
            output_content = output_file.read()

        # Create the JSON structure
        prompt_data = {
            "script": script_content,
            "output": output_content
        }

        # Convert to JSON format
        return json.dumps(prompt_data, indent=4)

    except FileNotFoundError as e:
        return json.dumps({"error": f"File not found: {e}"})
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {e}"})

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)