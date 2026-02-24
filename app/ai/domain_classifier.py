import pickle
import numpy as np
from typing import List
from sklearn.linear_model import LogisticRegression
from app.modules.knowledge.service import get_embedding

# Training data: 1=automobile, 0=non-automobile
TRAINING_DATA = [
    # Automobile queries (1)
    ("brake noise when stopping", 1),
    ("engine overheating issue", 1),
    ("check engine light on", 1),
    ("oil change interval", 1),
    ("tire pressure warning", 1),
    ("transmission slipping", 1),
    ("battery not charging", 1),
    ("steering wheel vibration", 1),
    ("air conditioning not working", 1),
    ("fuel consumption high", 1),
    ("spark plug replacement", 1),
    ("coolant leak under car", 1),
    ("brake pad replacement cost", 1),
    ("car won't start", 1),
    ("exhaust smoke black", 1),
    ("suspension noise over bumps", 1),
    ("clutch pedal hard", 1),
    ("windshield wiper not working", 1),
    ("headlight bulb replacement", 1),
    ("car pulls to one side", 1),
    
    # Non-automobile queries (0)
    ("what is the weather today", 0),
    ("write a poem about love", 0),
    ("calculate 18% GST on 10000", 0),
    ("best pizza recipe", 0),
    ("how to learn python", 0),
    ("stock market trends", 0),
    ("movie recommendations", 0),
    ("book a flight ticket", 0),
    ("translate to spanish", 0),
    ("solve math equation", 0),
    ("create a presentation", 0),
    ("send email to client", 0),
    ("schedule a meeting", 0),
    ("write a business plan", 0),
    ("design a logo", 0),
    ("play music", 0),
    ("tell me a joke", 0),
    ("what is quantum physics", 0),
    ("history of world war", 0),
    ("cooking instructions", 0),
]


class DomainClassifier:
    def __init__(self):
        self.model = None
        self._keywords = ["car", "vehicle", "brake", "engine", "tire", "oil", "transmission", 
                         "battery", "steering", "fuel", "exhaust", "suspension", "clutch"]
    
    async def train(self):
        """Train the classifier on embedding vectors."""
        print("Training domain classifier...")
        X, y = [], []
        for text, label in TRAINING_DATA:
            embedding = await get_embedding(text)
            X.append(embedding)
            y.append(label)
        
        self.model = LogisticRegression(max_iter=1000)
        self.model.fit(X, y)
        
        # Save model
        with open("models/domain_classifier.pkl", "wb") as f:
            pickle.dump(self.model, f)
        print(f"Model trained with {len(X)} samples, accuracy: {self.model.score(X, y):.2%}")
    
    def _load_model(self):
        """Load trained model from disk."""
        try:
            with open("models/domain_classifier.pkl", "rb") as f:
                return pickle.load(f)
        except FileNotFoundError:
            return None
    
    def _keyword_fallback(self, query: str) -> bool:
        """Fallback to keyword matching if model unavailable."""
        query_lower = query.lower()
        return any(kw in query_lower for kw in self._keywords)
    
    async def is_automobile_query(self, query: str) -> bool:
        """Classify query as automobile-related or not."""
        if not self.model:
            self.model = self._load_model()
        
        if not self.model:
            return self._keyword_fallback(query)
        
        embedding = await get_embedding(query)
        prediction = self.model.predict([embedding])[0]
        return prediction == 1


# Global instance
_classifier = DomainClassifier()


async def is_automobile_query(query: str) -> bool:
    """Public API for domain classification."""
    return await _classifier.is_automobile_query(query)


async def train_classifier():
    """Train and save the classifier."""
    await _classifier.train()
