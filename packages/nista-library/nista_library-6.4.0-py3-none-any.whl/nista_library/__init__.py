"""Nista Library

A client library for accessing nista.io
"""

import logging
import sys

import structlog

from .nista_connetion import KeyringNistaConnection, NistaConnection, StaticTokenNistaConnection, ReferenceTokenNistaConnection
from .nista_credential_manager import NistaCredentialManager
from .nista_data_point import NistaDataPoint
from .nista_data_points import NistaDataPoints

logging.basicConfig(
    format="%(message)s",
    stream=sys.stdout,
    level=logging.INFO,
)

structlog.configure(
    processors=[
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M.%S"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.dev.ConsoleRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)
