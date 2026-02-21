from pydantic import BaseModel, Field
from datetime import datetime, timezone, date, time
from typing import Optional


class TripCreate(BaseModel):
    bus_id : str
    route_id: Optional[str] = None
    date: date
    departure_time: time
    arrival_time:time
    price:float
    total_seats: Optional[int] = None
    available_seats: Optional[int] = None
    isActive: bool = True
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SearchTrip(BaseModel):
    from_city_id: str
    to_city_id: str
    date:date