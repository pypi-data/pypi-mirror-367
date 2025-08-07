import logging

def setup_logger():
    """Configure global logger"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('main.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

# Configure logger when module is imported
setup_logger() 