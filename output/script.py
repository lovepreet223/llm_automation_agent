# /// script
# requires-python = ">=3.9"
# dependencies = [
#   "uv",
# ]
# ///
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Hardcoded email argument for the script
EMAIL_ARG = "24f2006061@ds.study.iitm.ac.in"
DATAGEN_URL = "https://raw.githubusercontent.com/sanand0/tools-in-data-science-public/tds-2025-01/project-1/datagen.py"

def check_uv_installed():
    logging.info("Checking if 'uv' is installed.")
    result = subprocess.run(['pip', 'show', 'uv'], capture_output=True, text=True)
    return result.returncode == 0

def install_uv():
    logging.info("'uv' is not installed, installing now.")
    result = subprocess.run(['pip', 'install', 'uv'], capture_output=True, text=True)
    if result.returncode != 0:
        logging.error(f"Failed to install 'uv': {result.stderr}")
        exit(1)

def download_datagen_script():
    logging.info("Downloading datagen.py")
    result = subprocess.run(['curl', '-O', DATAGEN_URL], capture_output=True, text=True)
    if result.returncode != 0:
        logging.error(f"Failed to download datagen.py: {result.stderr}")
        exit(1)

def run_datagen_script():
    logging.info("Running datagen.py.")
    result = subprocess.run(['uv', 'run', 'datagen.py', EMAIL_ARG], capture_output=True, text=True)
    if result.returncode != 0:
        logging.error(f"Failed to run datagen.py: {result.stderr}")
        exit(1)
    logging.info("Successfully completed execution of datagen.py.")

if __name__ == "__main__":
    try:
        if not check_uv_installed():
            install_uv()
        download_datagen_script()
        run_datagen_script()
    except Exception as e:
        logging.error(f"An error occurred during execution: {e}", exc_info=True)