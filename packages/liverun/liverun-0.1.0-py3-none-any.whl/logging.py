from __future__ import annotations

import logging

LOGGER = logging.getLogger(__name__)


def configure_default_logging() -> None:
    """
    Configure a sensible default logging handler/level if the root logger has no handlers.

    This ensures logs appear when running the module directly, without forcing configuration
    on library consumers who may configure logging themselves.
    """
    root_logger = logging.getLogger()
    if not root_logger.handlers:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        )
