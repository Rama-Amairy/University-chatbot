import logging
import os, sys
import traceback

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.append(root_dir)

LOG_DIR = f"{root_dir}/log"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

LOG_FILE = os.path.join(LOG_DIR, "app.log")

# Configure Logger
logging.basicConfig(
    level=logging.DEBUG,  # Capture DEBUG and above messages
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),  # Log to file
        logging.StreamHandler()         # Log to console
    ]
)

logger = logging.getLogger("RamiChatBot")

def log_info(message):
    """Logs informational messages."""
    logger.info(message)

def log_debug(message):
    """Logs warnings."""
    logger.debug(message)
    
def log_warning(message):
    """Logs warnings."""
    logger.warning(message)

def log_error(message: str):
    """Logs errors with traceback and sends an alert."""
    # Capture and append the current traceback
    tb = traceback.format_exc()
    full_message = f"{message}\nTraceback:\n{tb}" if tb.strip() != 'NoneType: None' else message

    logger.error(full_message)


# Example usage
if __name__ == "__main__":
    log_info("Application started.")
    log_debug("This is a warning message.")
    log_error("This is a test error alert.")