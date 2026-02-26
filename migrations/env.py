from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool, create_engine
from alembic import context
import os
import sys

# Ensure the app directory is in the path
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), "..")))

config = context.config
fileConfig(config.config_file_name)

from app.db.base import Base
# Explicitly import all models for autogenerate support
from app.db.models import Tenant, User, AuditLog, Role
from app.subscriptions.models import SubscriptionPlan, TenantSubscription, UsageAggregate, OverageLedger
from app.modules.vehicles.model import Vehicle
from app.modules.job_cards.model import JobCard, Estimate, JobSummary
from app.modules.invoices.model import Invoice
from app.modules.catalog.model import Part, LaborRate
from app.modules.knowledge.model import KnowledgeChunk
from app.modules.mg_engine.model import MGFormula, CityIndex
from app.modules.operator.model import OperatorPreview, OperatorExecution

target_metadata = Base.metadata

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    # Directly create a synchronous engine for SQLite
    engine = create_engine("sqlite+pysqlite:///./eka_ai.db")
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
