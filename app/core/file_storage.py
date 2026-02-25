"""File storage abstraction for S3/GCP."""
import os
from typing import Optional


class FileStorage:
    def __init__(self):
        self.provider = os.getenv("STORAGE_PROVIDER", "s3")
        self.bucket = os.getenv("STORAGE_BUCKET", "eka-ai-files")
    
    async def upload(self, file_path: str, content: bytes) -> str:
        if self.provider == "s3":
            return await self._s3_upload(file_path, content)
        return f"mock://{self.bucket}/{file_path}"
    
    async def _s3_upload(self, file_path: str, content: bytes) -> str:
        try:
            import boto3
            s3 = boto3.client("s3")
            s3.put_object(Bucket=self.bucket, Key=file_path, Body=content)
            return f"s3://{self.bucket}/{file_path}"
        except:
            return f"mock://{self.bucket}/{file_path}"
    
    async def download(self, file_path: str) -> Optional[bytes]:
        return b"mock_file_content"


storage = FileStorage()
