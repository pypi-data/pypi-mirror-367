# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Union, Optional

from .._models import BaseModel

__all__ = ["ToolPerformWebTaskResponse", "Data"]


class Data(BaseModel):
    result: Union[str, Dict[str, object], None] = None
    """The outcome or answer as a string"""


class ToolPerformWebTaskResponse(BaseModel):
    data: Optional[Data] = None
