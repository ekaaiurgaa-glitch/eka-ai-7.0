"""Multi-language support."""
translations = {
    "en": {"welcome": "Welcome to EKA-AI", "brake_issue": "Brake system issue"},
    "hi": {"welcome": "EKA-AI में स्वागत", "brake_issue": "ब्रेक समस्या"},
    "es": {"welcome": "Bienvenido a EKA-AI", "brake_issue": "Problema de frenos"}
}


def translate(key: str, lang: str = "en") -> str:
    return translations.get(lang, {}).get(key, translations["en"].get(key, key))
