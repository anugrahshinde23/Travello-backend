from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
import datetime as dt


# 🔥 CREATE TRIP
class TripCreate(BaseModel):
    bus_id: str
    route_id: Optional[str] = None
    date: dt.date
    departure_time: dt.time
    arrival_time: dt.time
    price: float
    total_seats: Optional[int] = None
    available_seats: Optional[int] = None
    isActive: bool = True

    createdAt: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updatedAt: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    class Config:
        from_attributes = True


# 🔥 SEARCH TRIP
class SearchTrip(BaseModel):
    from_city_id: str
    to_city_id: str
    date: dt.date

    class Config:
        from_attributes = True


# 🔥 UPDATE TRIP (PATCH)
class UpdateTrip(BaseModel):
    date: Optional[dt.date] = None
    departure_time: Optional[dt.time] = None
    arrival_time: Optional[dt.time] = None
    price: Optional[float] = None

    class Config:
        from_attributes = True