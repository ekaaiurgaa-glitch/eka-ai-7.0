from sqlalchemy import Column, Integer, String, JSON, Float, Date, DateTime, Numeric, Boolean, ForeignKey, func, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base, TenantMixin, TimestampMixin
import uuid

class MGProposal(Base, TenantMixin, TimestampMixin):
    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, index=True)
    proposal_json = Column(JSON)
    monthly_mg = Column(Float)

class MGFormula(Base, TimestampMixin):
    __tablename__ = "mg_formulas"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    make = Column(String, nullable=False)
    model = Column(String, nullable=False)
    fuel_type = Column(String, nullable=False)
    annual_base_cost_inr = Column(Numeric(12, 2), nullable=False)
    parts_pct = Column(Numeric(5, 2), nullable=False, default=65.0)
    labor_pct = Column(Numeric(5, 2), nullable=False, default=35.0)
    valid_from = Column(Date, nullable=False, default=func.current_date())
    valid_to = Column(Date, nullable=True)

class CityIndex(Base):
    __tablename__ = "city_indices"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    city = Column(String, nullable=False, unique=True)
    tier = Column(String, nullable=False)
    multiplier = Column(Numeric(4, 2), nullable=False)

class MGContract(Base, TenantMixin, TimestampMixin):
    __tablename__ = "mg_contracts"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    vehicle_id = Column(UUID(as_uuid=True), nullable=False)
    customer_id = Column(UUID(as_uuid=True), nullable=False)
    risk_level = Column(String, nullable=False)
    monthly_fee_inr = Column(Numeric(10, 2), nullable=False)
    risk_buffer_pct = Column(Numeric(5, 2), nullable=False)
    annual_estimate_inr = Column(Numeric(12, 2), nullable=False)
    status = Column(String, nullable=False, default="active")
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    termination_reason = Column(String, nullable=True)

class ReserveAccount(Base):
    __tablename__ = "mg_reserve_accounts"
    tenant_id = Column(UUID(as_uuid=True), primary_key=True)
    total_reserve_balance = Column(Numeric(14, 2), nullable=False, default=0)
    last_updated = Column(DateTime, default=func.now())

class ReserveTransaction(Base, TimestampMixin):
    __tablename__ = "mg_reserve_transactions"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    tenant_id = Column(UUID(as_uuid=True), nullable=False)
    mg_contract_id = Column(UUID(as_uuid=True), ForeignKey("mg_contracts.id"), nullable=True)
    transaction_type = Column(String, nullable=False)
    amount_inr = Column(Numeric(10, 2), nullable=False)
    reason = Column(String, nullable=True)

class ReconciliationReport(Base):
    __tablename__ = "mg_reconciliation_reports"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    tenant_id = Column(UUID(as_uuid=True), nullable=False)
    report_month = Column(Date, nullable=False)
    total_mg_revenue = Column(Numeric(14, 2), nullable=False)
    total_actual_cost = Column(Numeric(14, 2), nullable=False)
    net_surplus_deficit = Column(Numeric(14, 2), nullable=False)
    reserve_balance_eom = Column(Numeric(14, 2), nullable=False)
    contracts_count = Column(Integer, nullable=False)
    overrun_contracts = Column(Integer, nullable=False, default=0)
    report_pdf_url = Column(String, nullable=True)
    generated_at = Column(DateTime, default=func.now())
