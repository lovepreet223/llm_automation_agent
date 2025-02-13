# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "requests",
# ]
# ///

import requests
import json

def download_file():
    url = "https://example.com/file.txt"  # Replace with the desired file URL
    output_path = "/data/file.txt"

    try:
        print(json.dumps({"debug": "Script started. Attempting to download file."}))
        response = requests.get(url)

        if response.status_code == 200:
            print(json.dumps({"debug": "File downloaded successfully. Attempting to save file."}))
            with open(output_path, 'wb') as f:
                f.write(response.content)
            print(json.dumps({"success": f"File saved to {output_path}"}))
        else:
            print(json.dumps({"error": f"Failed to download file. Status code: {response.status_code}"}))
    except Exception as e:
        print(json.dumps({"error": f"Script failed at: {e}"}))

if __name__ == "__main__":
    download_file()