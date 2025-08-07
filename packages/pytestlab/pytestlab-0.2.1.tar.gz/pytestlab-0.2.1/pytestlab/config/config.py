from __future__ import annotations
import re
from typing import Any, List
from pydantic import BaseModel, validator

from ..errors import InstrumentParameterError, InstrumentConfigurationError
from .base import Range as NewRangeModel # Import the Pydantic Range model

# Alias for backward compatibility
# The old Config class and ChannelsConfig are removed as Pydantic handles this.
# Individual instrument configs will use List[SpecificChannelModel]

# --- DUMMY Config class for mkdocstrings compatibility ---
class Config(BaseModel):
    """
    Dummy Config class for documentation compatibility.
    This is not used in runtime code, but allows mkdocstrings to resolve
    'pytestlab.config.Config' for API docs.
    """
    pass
