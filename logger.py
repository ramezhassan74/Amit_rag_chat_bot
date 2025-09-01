import logging


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

def my_function():
    logger.info("Function started")
    logger.warning("This is a warning")
    logger.error("Something went wrong")

my_function()
