"""API Gateway configuration."""
from typing import Dict


class APIGatewayConfig:
    def __init__(self):
        self.rate_limits = {
            "free": {"requests_per_minute": 10},
            "basic": {"requests_per_minute": 60},
            "pro": {"requests_per_minute": 300},
            "enterprise": {"requests_per_minute": 1000}
        }
    
    def get_rate_limit(self, plan: str) -> int:
        return self.rate_limits.get(plan, {}).get("requests_per_minute", 10)


gateway_config = APIGatewayConfig()
