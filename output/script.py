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

# Hardcoded variables
CHECK_UV_CMD = ["pip", "show", "uv"]
INSTALL_UV_CMD = ["pip", "install", "uv"]
SCRIPT_URL = "https://raw.githubusercontent.com/sanand0/tools-in-data-science-public/tds-2025-01/project-1/datagen.py"
DOWNLOAD_SCRIPT_CMD = ["curl", "-O", SCRIPT_URL]
RUN_SCRIPT_CMD = ["python", "datagen.py", "24f2006061@ds.study.iitm.ac.in"]

def check_and_install_uv():
    logging.info("Checking if 'uv' package is installed.")
    try:
        subprocess.run(CHECK_UV_CMD, check=True)
        logging.info("The 'uv' package is already installed.")
    except subprocess.CalledProcessError:
        logging.warning("'uv' package is not installed. Installing now...")
        try:
            subprocess.run(INSTALL_UV_CMD, check=True)
            logging.info("Successfully installed 'uv' package.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Error installing 'uv': {e}", exc_info=True)
            return False
    return True

def download_and_run_script():
    try:
        logging.info("Downloading the script from the provided URL.")
        subprocess.run(DOWNLOAD_SCRIPT_CMD, check=True)
        logging.info("Successfully downloaded the script.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error downloading script: {e}", exc_info=True)
        return
    
    try:
        logging.info("Running the downloaded script.")
        subprocess.run(RUN_SCRIPT_CMD, check=True)
        logging.info("Script executed successfully.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error running the script: {e}", exc_info=True)

if __name__ == "__main__":
    if check_and_install_uv():
        download_and_run_script()