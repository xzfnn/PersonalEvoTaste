"""Centralised logging configuration.

We expose a ``get_logger`` helper so that library code never calls
``logging.basicConfig`` itself (which would interfere with applications
embedding this library).
"""
from __future__ import annotations

import logging
import os
from typing import Optional

_DEFAULT_FORMAT = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"
_CONFIGURED = False


def _configure_root(level: int) -> None:
    global _CONFIGURED
    if _CONFIGURED:
        return
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(_DEFAULT_FORMAT))
    root = logging.getLogger("personal_evotaste")
    root.addHandler(handler)
    root.setLevel(level)
    root.propagate = False
    _CONFIGURED = True


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Return a namespaced logger, configuring it lazily on first use."""
    level_name = os.getenv("PERSONAL_EVOTASTE_LOG", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    _configure_root(level)
    if name is None:
        return logging.getLogger("personal_evotaste")
    if not name.startswith("personal_evotaste"):
        name = f"personal_evotaste.{name}"
    return logging.getLogger(name)
