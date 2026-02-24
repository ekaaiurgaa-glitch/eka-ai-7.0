import asyncio
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from app.ai.domain_classifier import TRAINING_DATA, DomainClassifier
from app.modules.knowledge.service import get_embedding

async def validate():
    print("Validating ML classifier with train/test split...")
    
    # Prepare data
    texts = [text for text, _ in TRAINING_DATA]
    labels = [label for _, label in TRAINING_DATA]
    
    # 80/20 split
    X_train_text, X_test_text, y_train, y_test = train_test_split(
        texts, labels, test_size=0.2, random_state=42, stratify=labels
    )
    
    # Get embeddings
    print("Generating embeddings...")
    X_train = [await get_embedding(text) for text in X_train_text]
    X_test = [await get_embedding(text) for text in X_test_text]
    
    # Train
    classifier = DomainClassifier()
    from sklearn.linear_model import LogisticRegression
    classifier.model = LogisticRegression(max_iter=1000)
    classifier.model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = classifier.model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\n{'='*50}")
    print(f"Test Set Accuracy: {accuracy:.2%}")
    print(f"{'='*50}\n")
    print(classification_report(y_test, y_pred, target_names=["Non-Auto", "Auto"]))
    
    return accuracy

if __name__ == "__main__":
    accuracy = asyncio.run(validate())
    if accuracy >= 0.85:
        print(f"✅ PASS: {accuracy:.2%} >= 85%")
    else:
        print(f"❌ FAIL: {accuracy:.2%} < 85%")
        exit(1)
