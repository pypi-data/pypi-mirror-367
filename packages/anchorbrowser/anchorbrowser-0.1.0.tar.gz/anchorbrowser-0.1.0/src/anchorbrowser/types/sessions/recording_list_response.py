# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from ..._models import BaseModel

__all__ = ["RecordingListResponse", "Data", "DataData", "DataDataItem"]


class DataDataItem(BaseModel):
    id: Optional[str] = None
    """Unique identifier for the recording"""

    created_at: Optional[datetime] = None
    """Timestamp when the recording was created"""

    duration: Optional[str] = None
    """Duration of the recording"""

    file_link: Optional[str] = None
    """URL to access the recording file"""

    is_primary: Optional[bool] = None
    """Indicates if this is the primary recording"""

    size: Optional[float] = None
    """Size of the recording file in bytes"""

    suggested_file_name: Optional[str] = None
    """Suggested filename for the recording"""


class DataData(BaseModel):
    count: Optional[int] = None
    """Total number of video recordings"""

    items: Optional[List[DataDataItem]] = None


class Data(BaseModel):
    data: Optional[DataData] = None


class RecordingListResponse(BaseModel):
    data: Optional[Data] = None
