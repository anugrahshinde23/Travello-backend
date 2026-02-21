from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Optional

class Cities(BaseModel) : 
    name: str
    state: str
    country: str
    code: str
    slug: str
    isActive : bool = True
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CityUpdate(BaseModel):
    name : Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    code: Optional[str] = None
    slug: Optional[str] = None
    isActive: Optional[bool] = True
    updatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Routes(BaseModel):
    source_city_id:str
    destination_city_id: str
    distance: float
    duration: float
    isActive: bool = True
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RoutesUpdate(BaseModel):
    source_city_id: Optional[str] = None
    destination_city_id: Optional[str] = None
    distance: Optional[float] = None
    duration: Optional[float] = None
    isActive: Optional[bool] = None
    updatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
