from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone

class BusRegister(BaseModel) : 
    name : str
    number : str
    bus_type : str
    total_seats : int
    owner : str
    route_id: Optional[str] = None
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class BusUpdatee(BaseModel) : 
    name : Optional[str] = None
    number : Optional[str] = None
    bus_type : Optional[str] = None
    total_seats : Optional[int]= None
    owner : Optional[str] = None
    updatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))