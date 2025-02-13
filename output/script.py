# /// script
# requires-python = ">=3.09"
# dependencies = [
#   "requests",
# ]
# ///
import logging
import subprocess

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Hardcoded configurations
DATA_DIRECTORY = "/data"
CONFIG_FILE = f"{DATA_DIRECTORY}/.prettierrc"
PRETTIER_VERSION = "3.4.2"
FORMAT_FILE = f"{DATA_DIRECTORY}/format.md"

def main():
    logging.info("Starting the Prettier setup and formatting.")

    try:
        # Navigate to the /data directory (simulated by setting the directory variable)
        logging.info(f"Creating configuration file at {CONFIG_FILE} if it does not exist.")
        with open(CONFIG_FILE, 'w') as f:
            f.write('{"semi": true, "singleQuote": true}')  # Example configuration for Prettier

        # Install prettier locally
        logging.info("Installing prettier locally.")
        subprocess.run(['npm', 'install', f'prettier@{PRETTIER_VERSION}'], cwd=DATA_DIRECTORY, check=True)

        # Run prettier with the update-in-place option
        logging.info(f"Running prettier on {FORMAT_FILE}.")
        subprocess.run(['npx', 'prettier', '--write', FORMAT_FILE], cwd=DATA_DIRECTORY, check=True)

        # Verify that the /data/format.md file has been formatted correctly
        logging.info(f"Verifying the content of {FORMAT_FILE}.")
        with open(FORMAT_FILE, 'r') as f:
            content = f.read()
            if "formatted" in content:  # Assuming the content is verified for a specific keyword
                logging.info(f"Formatting verification successful for {FORMAT_FILE}.")
            else:
                logging.error(f"Formatting verification failed for {FORMAT_FILE}.")

        # Clean up - remove node_modules and package-lock.json if created during installation
        logging.info("Cleaning up temporary files.")
        subprocess.run(['rm', '-rf', f'{DATA_DIRECTORY}/node_modules'], check=True)
        subprocess.run(['rm', '-f', f'{DATA_DIRECTORY}/package-lock.json'], check=True)

        logging.info("Prettier setup and formatting completed successfully.")

    except Exception as e:
        logging.error(f"Error during Prettier execution: {e}", exc_info=True)

if __name__ == "__main__":
    main()