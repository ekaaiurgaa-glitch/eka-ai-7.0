from sqlalchemy import Column, Integer, String, Float, Enum as SAEnum
from app.db.base import Base, TenantMixin, TimestampMixin
import enum


class GSTCategory(str, enum.Enum):
    gst_5 = "5"
    gst_12 = "12"
    gst_18 = "18"
    gst_28 = "28"


class Part(Base, TenantMixin, TimestampMixin):
    __tablename__ = "parts"
    id = Column(Integer, primary_key=True, index=True)
    part_number = Column(String, index=True, nullable=False)
    description = Column(String, nullable=False)
    hsn_code = Column(String, nullable=False)
    unit_price = Column(Float, nullable=False)
    gst_rate = Column(Float, default=18.0)


class LaborRate(Base, TenantMixin, TimestampMixin):
    __tablename__ = "labor_rates"
    id = Column(Integer, primary_key=True, index=True)
    service_type = Column(String, nullable=False)      # e.g. "brake_service", "engine_overhaul"
    city = Column(String, default="default")           # city-specific rates
    rate_per_hour = Column(Float, nullable=False)
    estimated_hours = Column(Float, default=1.0)
