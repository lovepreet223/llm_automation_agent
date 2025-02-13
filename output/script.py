# /// script
# requires-python = ">=3.09"
# dependencies = [
#   "subprocess",
# ]
# ///
import subprocess
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Hardcoded commands and paths
DATA_DIR = "/data"
NPM_INSTALL_COMMAND = "npm install -g prettier@3.4.2"
PRETTIER_COMMAND = "prettier --write format.md"

def navigate_and_install():
    logging.info("Navigating to the /data directory and installing Prettier.")
    try:
        os.chdir(DATA_DIR)
        subprocess.run(NPM_INSTALL_COMMAND, check=True, shell=True)
        logging.info("Successfully installed Prettier.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error during npm installation: {e}", exc_info=True)
        return False
    return True

def format_markdown():
    logging.info("Running Prettier to format format.md.")
    try:
        subprocess.run(PRETTIER_COMMAND, check=True, shell=True)
        logging.info("Successfully formatted format.md.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error during Prettier formatting: {e}", exc_info=True)

if __name__ == "__main__":
    if navigate_and_install():
        format_markdown()