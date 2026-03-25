import logging
import os

def setup_logger():
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file = os.path.join(log_dir, "master_system.log")
    
    # Create a custom logger
    logger = logging.getLogger("OnboardingSystem")
    logger.setLevel(logging.INFO)

    # If the logger already has handlers, don't add them again (prevents duplicate logs)
    if not logger.handlers:
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # File Handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Stream Handler (Terminal)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    return logger

# Initialize it
logger = setup_logger()