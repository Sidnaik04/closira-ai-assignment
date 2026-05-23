import logging

logging.basicConfig(
    filename="logs/escalations.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
