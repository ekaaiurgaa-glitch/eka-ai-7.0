import asyncio
import json
import logging
from datetime import datetime, date
import aio_pika
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from app.db.session import AsyncSessionLocal
from app.subscriptions.models import UsageAggregate
from app.core.config import settings

logger = logging.getLogger(__name__)

class UsageAggregator:
    def __init__(self):
        self.batch = []
        self.batch_lock = asyncio.Lock()
        self.rabbitmq_url = settings.RABBITMQ_URL

    async def connect(self):
        self.connection = await aio_pika.connect_robust(self.rabbitmq_url)
        self.channel = await self.connection.channel()
        # Set QoS to handle backpressure on our end
        await self.channel.set_qos(prefetch_count=100)
        self.queue = await self.channel.declare_queue("usage.events", durable=True)

    async def start(self):
        await self.connect()
        logger.info("Usage aggregator started.")
        
        # Start the consumer
        await self.queue.consume(self.process_message)
        
        # Start the batch flusher
        asyncio.create_task(self.flush_batch_periodically())

    async def process_message(self, message: aio_pika.abc.AbstractIncomingMessage):
        async with message.process():
             # Check queue depth for backpressure warning
            if self.queue.declaration_result.message_count > 10000:
                logger.warning("High queue depth on usage.events: %s messages", self.queue.declaration_result.message_count)
            
            payload = json.loads(message.body.decode())
            async with self.batch_lock:
                self.batch.append(payload)

    async def flush_batch_periodically(self):
        while True:
            await asyncio.sleep(30)
            await self.flush_batch()

    async def flush_batch(self):
        async with self.batch_lock:
            if not self.batch:
                return
            items_to_process = self.batch.copy()
            self.batch.clear()
            
        async with AsyncSessionLocal() as session:
            try:
                # Group by tenant_id and event_type internally, or just emit upsert queries
                
                for item in items_to_process:
                    tenant_id = item["tenant_id"]
                    event_type = item["event_type"]
                    tokens = item.get("tokens_consumed", 0)
                    storage = item.get("storage_bytes", 0)
                    billing_cycle_start = item.get("billing_cycle_start", date.today().replace(day=1))
                    
                    stmt = insert(UsageAggregate).values(
                        tenant_id=tenant_id,
                        billing_cycle_start=billing_cycle_start,
                        total_tokens_consumed=tokens,
                        total_storage_bytes=storage,
                        total_operator_actions=1 if event_type == "operator_action" else 0,
                        total_job_cards_created=1 if event_type == "job_card_create" else 0,
                        total_mg_calculations=1 if event_type == "mg_calculation" else 0,
                        total_api_requests=1,
                        last_updated=datetime.utcnow()
                    )
                    
                    stmt = stmt.on_conflict_do_update(
                        index_elements=['tenant_id', 'billing_cycle_start'],
                        set_={
                            "total_tokens_consumed": UsageAggregate.total_tokens_consumed + stmt.excluded.total_tokens_consumed,
                            "total_storage_bytes": UsageAggregate.total_storage_bytes + stmt.excluded.total_storage_bytes,
                            "total_operator_actions": UsageAggregate.total_operator_actions + stmt.excluded.total_operator_actions,
                            "total_job_cards_created": UsageAggregate.total_job_cards_created + stmt.excluded.total_job_cards_created,
                            "total_mg_calculations": UsageAggregate.total_mg_calculations + stmt.excluded.total_mg_calculations,
                            "total_api_requests": UsageAggregate.total_api_requests + stmt.excluded.total_api_requests,
                            "last_updated": datetime.utcnow()
                        }
                    )
                    
                    await session.execute(stmt)
                
                await session.commit()
            except Exception as e:
                logger.error(f"Error flushing batch: {e}")
                await session.rollback()

async def run_aggregator():
    aggregator = UsageAggregator()
    await aggregator.start()
    
    # Keep running
    await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(run_aggregator())
