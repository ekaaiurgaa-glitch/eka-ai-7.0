"""DDoS protection."""
from collections import defaultdict
from datetime import datetime, timedelta

class DDoSProtection:
    def __init__(self):
        self.request_counts = defaultdict(list)
        self.blocked_ips = set()
    
    async def check_request(self, ip: str) -> bool:
        now = datetime.utcnow()
        cutoff = now - timedelta(minutes=1)
        self.request_counts[ip] = [t for t in self.request_counts[ip] if t > cutoff]
        self.request_counts[ip].append(now)
        if len(self.request_counts[ip]) > 100:
            self.blocked_ips.add(ip)
            return False
        return ip not in self.blocked_ips

ddos_protection = DDoSProtection()
