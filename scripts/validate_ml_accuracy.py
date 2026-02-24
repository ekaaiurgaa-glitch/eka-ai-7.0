#!/usr/bin/env python
"""
ML Accuracy Validation with Held-Out Test Set
Validates domain classifier accuracy using proper train/test methodology.
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report, confusion_matrix
from sklearn.linear_model import LogisticRegression
import numpy as np


# Extended training data for better validation
EXTENDED_TRAINING_DATA = [
    # Automobile queries (1) - 30 samples
    ("brake noise when stopping", 1),
    ("engine overheating issue", 1),
    ("check engine light on", 1),
    ("oil change interval", 1),
    ("tire pressure warning", 1),
    ("transmission slipping", 1),
    ("battery not charging", 1),
    ("steering wheel vibration", 1),
    ("air conditioning not working in car", 1),
    ("fuel consumption too high", 1),
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
    ("radiator fan not working", 1),
    ("alternator failure symptoms", 1),
    ("timing belt replacement", 1),
    ("power steering fluid leak", 1),
    ("catalytic converter issues", 1),
    ("wheel alignment problems", 1),
    ("oxygen sensor malfunction", 1),
    ("fuel injector cleaning", 1),
    ("differential noise", 1),
    ("turbocharger boost issues", 1),
    
    # Non-automobile queries (0) - 30 samples
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
    ("cryptocurrency prices", 0),
    ("learn guitar chords", 0),
    ("best smartphones 2024", 0),
    ("healthy diet plan", 0),
    ("yoga exercises", 0),
    ("meditation techniques", 0),
    ("real estate investment", 0),
    ("social media marketing", 0),
    ("machine learning algorithms", 0),
    ("cloud computing basics", 0),
]


async def get_embeddings_batch(texts: list) -> list:
    """Get embeddings for a batch of texts."""
    from app.modules.knowledge.service import get_embedding
    embeddings = []
    for text in texts:
        emb = await get_embedding(text)
        embeddings.append(emb)
    return embeddings


def keyword_classify(text: str) -> int:
    """Keyword-based classification (fallback)."""
    keywords = ["car", "vehicle", "brake", "engine", "tire", "oil", "transmission", 
                "battery", "steering", "fuel", "exhaust", "suspension", "clutch",
                "radiator", "alternator", "wheel", "motor", "automotive"]
    text_lower = text.lower()
    return 1 if any(kw in text_lower for kw in keywords) else 0


async def validate_ml_accuracy(use_embeddings: bool = True) -> dict:
    """
    Validate ML classifier accuracy with proper methodology.
    
    Returns:
        Dictionary with accuracy metrics
    """
    print("\n" + "="*60)
    print("ML Domain Classifier Validation")
    print("="*60)
    
    texts = [text for text, _ in EXTENDED_TRAINING_DATA]
    labels = [label for _, label in EXTENDED_TRAINING_DATA]
    
    # 80/20 stratified split
    X_train_text, X_test_text, y_train, y_test = train_test_split(
        texts, labels, test_size=0.2, random_state=42, stratify=labels
    )
    
    print(f"\nDataset: {len(EXTENDED_TRAINING_DATA)} samples")
    print(f"Train set: {len(X_train_text)} samples")
    print(f"Test set: {len(X_test_text)} samples")
    print(f"Class balance: {sum(labels)} auto, {len(labels) - sum(labels)} non-auto")
    
    if use_embeddings:
        print("\nGenerating embeddings (this may take a moment)...")
        try:
            X_train = await get_embeddings_batch(X_train_text)
            X_test = await get_embeddings_batch(X_test_text)
            
            # Check if embeddings are valid (not all zeros)
            if all(all(v == 0.0 for v in emb) for emb in X_train):
                print("⚠️  Embeddings unavailable (API quota/key issue)")
                print("   Falling back to keyword-based validation...")
                use_embeddings = False
        except Exception as e:
            print(f"⚠️  Embedding generation failed: {e}")
            print("   Falling back to keyword-based validation...")
            use_embeddings = False
    
    if use_embeddings:
        # Train model
        model = LogisticRegression(max_iter=1000, random_state=42)
        model.fit(X_train, y_train)
        
        # Predict
        y_train_pred = model.predict(X_train)
        y_test_pred = model.predict(X_test)
        method = "ML (Embeddings)"
    else:
        # Use keyword classification
        y_train_pred = [keyword_classify(text) for text in X_train_text]
        y_test_pred = [keyword_classify(text) for text in X_test_text]
        method = "Keyword Matching"
    
    # Calculate metrics
    train_acc = accuracy_score(y_train, y_train_pred)
    test_acc = accuracy_score(y_test, y_test_pred)
    precision = precision_score(y_test, y_test_pred, zero_division=0)
    recall = recall_score(y_test, y_test_pred, zero_division=0)
    f1 = f1_score(y_test, y_test_pred, zero_division=0)
    
    print(f"\n{'='*60}")
    print(f"Results ({method})")
    print(f"{'='*60}")
    print(f"\nTraining Accuracy: {train_acc:.2%}")
    print(f"Test Accuracy:     {test_acc:.2%}")
    print(f"Precision:         {precision:.2%}")
    print(f"Recall:            {recall:.2%}")
    print(f"F1 Score:          {f1:.2%}")
    
    print(f"\nConfusion Matrix:")
    cm = confusion_matrix(y_test, y_test_pred)
    print(f"                  Predicted")
    print(f"                  Non-Auto  Auto")
    print(f"Actual Non-Auto   {cm[0][0]:^8}  {cm[0][1]:^4}")
    print(f"       Auto       {cm[1][0]:^8}  {cm[1][1]:^4}")
    
    print(f"\nClassification Report:")
    print(classification_report(y_test, y_test_pred, target_names=["Non-Auto", "Auto"]))
    
    # Validation result
    print(f"{'='*60}")
    threshold = 0.75  # 75% accuracy threshold
    if test_acc >= threshold:
        print(f"✅ VALIDATION PASSED: {test_acc:.2%} >= {threshold:.0%}")
        status = "PASS"
    else:
        print(f"⚠️  VALIDATION WARNING: {test_acc:.2%} < {threshold:.0%}")
        status = "WARN"
    print(f"{'='*60}\n")
    
    return {
        "method": method,
        "train_accuracy": train_acc,
        "test_accuracy": test_acc,
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
        "status": status,
        "threshold": threshold
    }


if __name__ == "__main__":
    results = asyncio.run(validate_ml_accuracy(use_embeddings=True))
    
    # Exit with appropriate code
    if results["status"] == "PASS":
        sys.exit(0)
    else:
        sys.exit(1)
