"""mTLS Configuration - TDD Section 6.1"""
import ssl
import os
from datetime import datetime, timedelta
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization


def generate_service_certificate(service_name: str, validity_hours: int = 24):
    """Generate short-lived service certificate (24-hour rotation)"""
    
    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    
    # Generate certificate
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "IN"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Karnataka"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "Bangalore"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Go4Garage"),
        x509.NameAttribute(NameOID.COMMON_NAME, service_name),
    ])
    
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.utcnow()
    ).not_valid_after(
        datetime.utcnow() + timedelta(hours=validity_hours)
    ).add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName(service_name),
            x509.DNSName(f"{service_name}.eka-ai.svc.cluster.local"),
        ]),
        critical=False,
    ).sign(private_key, hashes.SHA256())
    
    return private_key, cert


def create_ssl_context(cert_path: str, key_path: str, ca_path: str) -> ssl.SSLContext:
    """Create SSL context for mTLS"""
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile=cert_path, keyfile=key_path)
    context.load_verify_locations(cafile=ca_path)
    context.verify_mode = ssl.CERT_REQUIRED
    return context


class MTLSConfig:
    def __init__(self):
        self.cert_dir = os.getenv("MTLS_CERT_DIR", "/etc/eka-ai/certs")
        self.service_name = os.getenv("SERVICE_NAME", "eka-service")
    
    def get_ssl_context(self) -> ssl.SSLContext:
        cert_path = f"{self.cert_dir}/{self.service_name}.crt"
        key_path = f"{self.cert_dir}/{self.service_name}.key"
        ca_path = f"{self.cert_dir}/ca.crt"
        
        if not all(os.path.exists(p) for p in [cert_path, key_path, ca_path]):
            # Generate if not exists
            private_key, cert = generate_service_certificate(self.service_name)
            
            os.makedirs(self.cert_dir, exist_ok=True)
            
            with open(key_path, "wb") as f:
                f.write(private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            
            with open(cert_path, "wb") as f:
                f.write(cert.public_bytes(serialization.Encoding.PEM))
        
        return create_ssl_context(cert_path, key_path, ca_path)


mtls_config = MTLSConfig()
