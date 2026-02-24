from sqlalchemy.orm import as_declarative, declared_attr
from sqlalchemy import Column, String
import uuid

@as_declarative()
class Base:
    id: any
    __name__: str

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

class TenantMixin:
    @declared_attr
    def tenant_id(cls):
        return Column(String, nullable=False, index=True)

# You can also add other mixins here, for example for created_at and updated_at timestamps.
class TimestampMixin:
    @declared_attr
    def created_at(cls):
        from sqlalchemy import DateTime, func
        return Column(DateTime, default=func.now(), nullable=False)

    @declared_attr
    def updated_at(cls):
        from sqlalchemy import DateTime, func
        return Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
