from pydantic import BaseModel, Field
from typing import Optional,List
from datetime import datetime, timezone
import datetime as dt



class Booking(BaseModel):
    trip_id: str
    seats: List[str]
    payment_id:Optional[str] = None
    ticket_url : Optional[str] = None
    ticket_no : Optional[str] = None
    createdAt: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updatedAt: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )