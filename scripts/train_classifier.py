#!/usr/bin/env python
"""Train the ML domain classifier."""
import asyncio
from app.ai.domain_classifier import train_classifier

if __name__ == "__main__":
    print("Training ML domain classifier...")
    asyncio.run(train_classifier())
    print("Training complete! Model saved to models/domain_classifier.pkl")
