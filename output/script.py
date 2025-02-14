# /// script
# requires-python = ">=3.09"
# dependencies = [
#   "uv",
# ]
# ///
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def check_uv_installed():
    logging.info("Checking if 'uv' is installed.")
    result = subprocess.run(['pip', 'show', 'uv'], capture_output=True, text=True)
    if result.returncode != 0:
        logging.warning("'uv' not found, attempting to install.")
        install_uv()
    else:
        logging.info("'uv' is already installed.")

def install_uv():
    try:
        subprocess.run(['pip', 'install', 'uv'], check=True)
        logging.info("'uv' installed successfully.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to install 'uv': {e}", exc_info=True)

def download_script():
    logging.info("Downloading the script from the specified URL.")
    try:
        subprocess.run(['curl', '-O', 'https://raw.githubusercontent.com/sanand0/tools-in-data-science-public/tds-2025-01/project-1/datagen.py'], check=True)
        logging.info("Script downloaded successfully.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error downloading the script: {e}", exc_info=True)

def run_script():
    logging.info("Running the downloaded script.")
    try:
        subprocess.run(['uv', 'run', 'datagen.py', '24f2006061@ds.study.iitm.ac.in'], check=True)
        logging.info("Script executed successfully.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error executing the script: {e}", exc_info=True)

if __name__ == "__main__":
    check_uv_installed()
    download_script()
    run_script()