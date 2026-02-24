"""
Secrets Management Configuration for EKA-AI
Supports multiple secret backends: Environment, AWS Secrets Manager, HashiCorp Vault
"""
import os
import json
import logging
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod
from functools import lru_cache

logger = logging.getLogger(__name__)


class SecretsBackend(ABC):
    """Abstract base class for secrets backends."""
    
    @abstractmethod
    def get_secret(self, key: str) -> Optional[str]:
        """Retrieve a secret by key."""
        pass
    
    @abstractmethod
    def get_secrets(self, keys: list) -> Dict[str, Optional[str]]:
        """Retrieve multiple secrets."""
        pass


class EnvironmentSecretsBackend(SecretsBackend):
    """Secrets from environment variables (default for development)."""
    
    def __init__(self, prefix: str = ""):
        self.prefix = prefix
    
    def get_secret(self, key: str) -> Optional[str]:
        full_key = f"{self.prefix}{key}" if self.prefix else key
        return os.environ.get(full_key)
    
    def get_secrets(self, keys: list) -> Dict[str, Optional[str]]:
        return {key: self.get_secret(key) for key in keys}


class AWSSecretsManagerBackend(SecretsBackend):
    """Secrets from AWS Secrets Manager."""
    
    def __init__(self, region: str = "us-east-1", secret_name: str = "eka-ai/production"):
        self.region = region
        self.secret_name = secret_name
        self._client = None
        self._cache: Dict[str, str] = {}
    
    @property
    def client(self):
        if self._client is None:
            try:
                import boto3
                self._client = boto3.client('secretsmanager', region_name=self.region)
            except ImportError:
                logger.warning("boto3 not installed, AWS Secrets Manager unavailable")
                return None
        return self._client
    
    def _load_secrets(self):
        """Load all secrets from AWS Secrets Manager."""
        if self._cache or self.client is None:
            return
            
        try:
            response = self.client.get_secret_value(SecretId=self.secret_name)
            secret_string = response.get('SecretString', '{}')
            self._cache = json.loads(secret_string)
            logger.info(f"Loaded secrets from AWS Secrets Manager: {self.secret_name}")
        except Exception as e:
            logger.error(f"Failed to load AWS secrets: {e}")
    
    def get_secret(self, key: str) -> Optional[str]:
        self._load_secrets()
        return self._cache.get(key)
    
    def get_secrets(self, keys: list) -> Dict[str, Optional[str]]:
        self._load_secrets()
        return {key: self._cache.get(key) for key in keys}


class VaultSecretsBackend(SecretsBackend):
    """Secrets from HashiCorp Vault."""
    
    def __init__(
        self,
        url: str = "http://localhost:8200",
        token: Optional[str] = None,
        mount_point: str = "secret",
        path: str = "eka-ai"
    ):
        self.url = url
        self.token = token or os.environ.get("VAULT_TOKEN")
        self.mount_point = mount_point
        self.path = path
        self._client = None
        self._cache: Dict[str, str] = {}
    
    @property
    def client(self):
        if self._client is None:
            try:
                import hvac
                self._client = hvac.Client(url=self.url, token=self.token)
                if not self._client.is_authenticated():
                    logger.warning("Vault client not authenticated")
                    return None
            except ImportError:
                logger.warning("hvac not installed, Vault unavailable")
                return None
        return self._client
    
    def _load_secrets(self):
        """Load all secrets from Vault."""
        if self._cache or self.client is None:
            return
            
        try:
            response = self.client.secrets.kv.v2.read_secret_version(
                mount_point=self.mount_point,
                path=self.path
            )
            self._cache = response['data']['data']
            logger.info(f"Loaded secrets from Vault: {self.path}")
        except Exception as e:
            logger.error(f"Failed to load Vault secrets: {e}")
    
    def get_secret(self, key: str) -> Optional[str]:
        self._load_secrets()
        return self._cache.get(key)
    
    def get_secrets(self, keys: list) -> Dict[str, Optional[str]]:
        self._load_secrets()
        return {key: self._cache.get(key) for key in keys}


class SecretsManager:
    """
    Unified secrets manager with fallback chain.
    
    Priority order:
    1. AWS Secrets Manager (production)
    2. HashiCorp Vault (production alternative)
    3. Environment variables (development/fallback)
    """
    
    def __init__(self):
        self.backends: list[SecretsBackend] = []
        self._initialize_backends()
    
    def _initialize_backends(self):
        """Initialize backends based on environment."""
        env = os.environ.get("ENVIRONMENT", "development")
        
        if env == "production":
            # Try AWS Secrets Manager first
            if os.environ.get("AWS_REGION"):
                self.backends.append(AWSSecretsManagerBackend(
                    region=os.environ.get("AWS_REGION", "us-east-1"),
                    secret_name=os.environ.get("AWS_SECRET_NAME", "eka-ai/production")
                ))
            
            # Try Vault as alternative
            if os.environ.get("VAULT_ADDR"):
                self.backends.append(VaultSecretsBackend(
                    url=os.environ.get("VAULT_ADDR", "http://localhost:8200"),
                    mount_point=os.environ.get("VAULT_MOUNT", "secret"),
                    path=os.environ.get("VAULT_PATH", "eka-ai")
                ))
        
        # Always have environment as fallback
        self.backends.append(EnvironmentSecretsBackend())
        
        logger.info(f"Initialized {len(self.backends)} secrets backends")
    
    def get_secret(self, key: str, required: bool = False) -> Optional[str]:
        """
        Get a secret, trying backends in order.
        
        Args:
            key: Secret key to retrieve
            required: If True, raises ValueError if not found
        """
        for backend in self.backends:
            value = backend.get_secret(key)
            if value is not None:
                return value
        
        if required:
            raise ValueError(f"Required secret '{key}' not found in any backend")
        
        return None
    
    def get_secrets(self, keys: list, required: bool = False) -> Dict[str, Optional[str]]:
        """Get multiple secrets."""
        results = {}
        for key in keys:
            results[key] = self.get_secret(key, required=required)
        return results


# Global singleton
_secrets_manager: Optional[SecretsManager] = None


def get_secrets_manager() -> SecretsManager:
    """Get the global secrets manager instance."""
    global _secrets_manager
    if _secrets_manager is None:
        _secrets_manager = SecretsManager()
    return _secrets_manager


def get_secret(key: str, required: bool = False) -> Optional[str]:
    """Convenience function to get a secret."""
    return get_secrets_manager().get_secret(key, required=required)


# Required secrets for the application
REQUIRED_SECRETS = [
    "SECRET_KEY",
    "DATABASE_URL",
]

OPTIONAL_SECRETS = [
    "GEMINI_API_KEY",
    "REDIS_URL",
    "SENTRY_DSN",
    "JAEGER_ENDPOINT",
]


def validate_secrets() -> bool:
    """Validate that all required secrets are available."""
    manager = get_secrets_manager()
    
    print("\n" + "="*60)
    print("Secrets Validation")
    print("="*60)
    
    missing = []
    for key in REQUIRED_SECRETS:
        value = manager.get_secret(key)
        if value:
            print(f"✅ {key}: configured")
        else:
            print(f"❌ {key}: MISSING (required)")
            missing.append(key)
    
    for key in OPTIONAL_SECRETS:
        value = manager.get_secret(key)
        if value:
            print(f"✅ {key}: configured")
        else:
            print(f"⚠️  {key}: not set (optional)")
    
    print("="*60)
    
    if missing:
        print(f"❌ Missing required secrets: {missing}")
        return False
    else:
        print("✅ All required secrets configured")
        return True


if __name__ == "__main__":
    import sys
    success = validate_secrets()
    sys.exit(0 if success else 1)
