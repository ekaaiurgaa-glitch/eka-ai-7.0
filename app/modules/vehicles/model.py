from sqlalchemy import Column, Integer, String, Enum as SAEnum
from app.db.base import Base, TenantMixin, TimestampMixin
import enum


class FuelTypeEnum(str, enum.Enum):
    petrol = "petrol"
    diesel = "diesel"
    electric = "electric"
    hybrid = "hybrid"


class Vehicle(Base, TenantMixin, TimestampMixin):
    id = Column(Integer, primary_key=True, index=True)
    plate_number = Column(String, index=True)
    make = Column(String, nullable=False)
    model = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    fuel_type = Column(SAEnum(FuelTypeEnum), nullable=False)
    vin = Column(String, unique=True, index=True, nullable=True)
    owner_name = Column(String, nullable=True)
    monthly_km = Column(Integer, default=1000)
