from pydantic import BaseModel, Field
from typing import Optional,List
from datetime import datetime, timezone
import datetime as dt

class Payment(BaseModel) : 
    booking_id:str
    amount:Optional[float] = None
    createdAt: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updatedAt: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

class VerifyPayment(BaseModel):
    booking_id: str
    payment_id:str
    