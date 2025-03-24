import logging

import factory  # noqa

from app.logs import get_logger

test_logger = get_logger("test", logging.WARNING)
