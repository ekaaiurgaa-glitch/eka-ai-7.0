"""Anti-abuse mechanisms."""
from collections import defaultdict
from datetime import datetime, timedelta

class AntiAbuse:
    def __init__(self):
        self.action_counts = defaultdict(list)
    
    async def detect_token_farming(self, tenant_id: str) -> bool:
        now = datetime.utcnow()
        cutoff = now - timedelta(hours=1)
        self.action_counts[tenant_id] = [t for t in self.action_counts[tenant_id] if t > cutoff]
        if len(self.action_counts[tenant_id]) > 1000:
            return True
        self.action_counts[tenant_id].append(now)
        return False

anti_abuse = AntiAbuse()
