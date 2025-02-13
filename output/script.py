# /// script
# requires-python = ">=3.09"
# dependencies = [
#   "uv",
# ]
# ///
import os
import subprocess
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def check_and_install_uv():
    logging.info("Checking if 'uv' is installed.")
    try:
        result = subprocess.run(['pip', 'show', 'uv'], capture_output=True, text=True)
        if result.returncode != 0:
            logging.info("'uv' is not installed. Installing now...")
            subprocess.run(['pip', 'install', 'uv'], check=True)
            logging.info("'uv' has been successfully installed.")
        else:
            logging.info("'uv' is already installed.")
    except Exception as e:
        logging.error(f"Error while checking or installing 'uv': {e}")

def download_script():
    url = "https://raw.githubusercontent.com/sanand0/tools-in-data-science-public/tds-2025-01/project-1/datagen.py"
    logging.info("Downloading the Python script.")
    try:
        subprocess.run(['curl', '-O', url], check=True)
        logging.info("Python script downloaded successfully.")
    except Exception as e:
        logging.error(f"Error downloading the Python script: {e}")

def make_script_executable():
    logging.info("Making the script executable.")
    try:
        subprocess.run(['chmod', '+x', 'datagen.py'], check=True)
        logging.info("Script is now executable.")
    except Exception as e:
        logging.error(f"Error making the script executable: {e}")

def run_script():
    email_address = "24f2006061@ds.study.iitm.ac.in"
    logging.info("Running the downloaded script.")
    try:
        subprocess.run(['python', 'datagen.py', email_address], check=True)
        logging.info("Script executed successfully.")
    except Exception as e:
        logging.error(f"Error running the script: {e}")

if __name__ == "__main__":
    check_and_install_uv()
    download_script()
    make_script_executable()
    run_script()