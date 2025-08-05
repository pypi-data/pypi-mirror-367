import logging

# Function to configure logging.
def configure_logging() -> logging.getLogger:
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    
    # Custom formatter to print only the message.
    formatter = logging.Formatter('%(message)s')
    handler.setFormatter(formatter)
    
    # Clear existing handlers to avoid duplicate messages.
    if logger.hasHandlers():
        logger.handlers.clear()
    
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    
    return logger
