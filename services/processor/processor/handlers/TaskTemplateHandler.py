from typing import Any

import ayon_api
from nxtools import logging


class TaskTemplate:
    pass


def process_event(event: dict, settings: dict) -> None:
    logging.info(f"{event = }")
    logging.info(f"{settings = }")
