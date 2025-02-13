from fastapi import FastAPI, HTTPException, Query
import requests
import os
import json
import re
import subprocess
import base64

app = FastAPI()

AIPROXY_TOKEN = os.getenv("AIPROXY_TOKEN")  # Load API key from environment
AIPROXY_BASE_URL = "https://aiproxy.sanand.workers.dev/openai"
use_openai_api = False

# Base data directory to prevent accessing files outside /data
BASE_DIR = "/data"


@app.post("/run")
async def run_task(task: str = Query(..., description="Plain English task description")):
    try:
        #For each task empty out the files
        open("output/script.py", "w").close()
        open("output/output.txt", "w").close()
        print("Getting tasks...")
        #print(task)
        response = prompt("prompts/initial_prompt.txt", str(task), use_openai_api=use_openai_api)
        print("Checking file permissions...")
        #print(response)
        file_permissions = prompt("prompts/file_rules.txt", str(response), use_openai_api=use_openai_api)
        #print(file_permissions)
        if "error" in file_permissions.get("result", {}):
            error_message = file_permissions["result"]["error"]
            raise HTTPException(status_code=400, detail=f"AIProxy Error: {error_message}")
        print("Getting Script...")
        response_script = prompt("prompts/second_prompt.txt", str(response['result']), use_openai_api=use_openai_api)
        # When invalid file access is required.
        if "error" in response_script.get("result", {}):
            error_message = response_script["result"]["error"]
            raise HTTPException(status_code=400, detail=f"AIProxy Error: {error_message}")
        # Extract the response and save into script file
        print("Starting script saving process...")
        #print(response_script)
        extract_and_save_script(response_script)
        # Run the script and save the output
        print("Running Script and Saving output...")
        run_script_and_save_output()

        #Running this part if error occurs or persists.
        flag = False
        while not flag:
            print("Running while loop...")
            print("Checking Output of the Script...")
            output = prepare_prompt("output/output.txt")
            up_response = prompt("prompts/output_check.txt", str(output), use_openai_api=use_openai_api)
            print(up_response)
            if "success" in up_response.get("result", {}):
                flag = True
            else:
                script = prepare_prompt("output/script.py")
                up_prompt = {"task": response,
                             "script": script,
                             "output": output}
                up_prompt = json.dumps(up_prompt, indent=4)
                print(up_prompt)
                up_response = prompt("prompts/third_prompt.txt", str(up_prompt), use_openai_api=True)
                print("Starting script saving process...")
                extract_and_save_script(response_script)
                # Run the script and save the output
                print("Saving output...")
                run_script_and_save_output()
        print("Success")

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


def prompt(file_path, task, use_openai_api=False):
    """
    Send the request to prompt and parses the response.
    :param file_path: file that contains the prompt.
    :param task: task as passed by the user.
    :param use_openai_api: whether to use openai API or not
    :return: returns the response of the LLM.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        prompt = file.read()
    prompt = prompt.replace("{task}", task)

    if use_openai_api:
        api_url = "https://api.openai.com/v1/chat/completions"
        api_key = OPENAI_API_KEY  # Ensure this is set
    else:
        api_url = f"{AIPROXY_BASE_URL}/v1/chat/completions"
        api_key = AIPROXY_TOKEN  # Ensure this is set

    response = requests.post(
        api_url,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        },
        json={
            "model": "gpt-4o-mini",
            "messages": [{"role": "system", "content": prompt}]
        }
    )

    response.raise_for_status()  # Ensure we got a successful response
    raw_content = response.json()["choices"][0]["message"]["content"]
    # Remove Markdown code block syntax if present
    if raw_content.startswith("```python") and raw_content.endswith("```"):
        raw_content = base64.b64encode(raw_content.encode()).decode()
        return {"result": raw_content}
    # Parse the cleaned JSON string into a Python list
    elif raw_content.startswith("```json") and raw_content.endswith("```"):
        raw_content = raw_content[7:-3].strip()  # Remove ` ```json ` and ` ``` `
        # Parse the cleaned JSON string into a Python list
        try:
            raw_content = json.loads(raw_content)
            return {"result": json.dumps(raw_content)}
        except json.JSONDecodeError as e:
            raw_content = raw_content  # Fallback in case of an error
            return {"error": "Invalid JSON format"}  # Handle errors properly

    # If the format is unknown, return an error
    if not isinstance(raw_content, str):
        raw_content = json.dumps(raw_content)  # Convert dict to JSON string

    return {"result": raw_content}  # Now it should return properly formatted JSON


def extract_and_save_script(response: dict, filename: str = "output/script.py"):
    """
    Parses the code and saves into the file.
    :param response: code response from the LLM
    :param filename: Where the file needs to be saved
    :return: It returns nothing but saves the python code to the file.
    """
    # Extract the 'result' value
    #result = response.get("result", "")
    result = base64.b64decode(response["result"]).decode()
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
    """
    Runs the script and saves the output of the script to the file.
    :param script_filename: script path that needed to be run.
    :param output_filename: output file in which the output of the script is saved.
    :return: returns nothing just saves the output.
    """
    try:
        # Run the script using 'uv run script.py' command
        result = subprocess.run(["uv", "run", script_filename], capture_output=True, text=True)

        # Save the output to a file
        with open(output_filename, "w", encoding="utf-8") as file:
            file.write(result.stdout + "\n" + result.stderr)

        print(f"Output saved to {output_filename}")
    except Exception as e:
        print(f"Error running script: {e}")


def prepare_prompt(file_path):
    """
    Takes the file as input and return its content.
    :param file_path: file whose content needed to be returned
    :return: content of the file.
    """
    try:
        # Read the output file
        with open(file_path, "r") as output_file:
            output_content = output_file.read()

        # Create the JSON structure
        prompt_data = {
            "data": output_content,
        }

        # Convert to JSON format
        return prompt_data

    except FileNotFoundError as e:
        return json.dumps({"error": f"File not found: {e}"})
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {e}"})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
