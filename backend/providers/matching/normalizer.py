import re
import unicodedata

VERSION_KEYWORDS = [
    "remaster", "live", "version", "edit", "deluxe",
    "mono", "stereo", "acoustic"
]

def normalize_text(text: str) -> str:
    if not text:
        return ""

    # Unicode normalization
    text = unicodedata.normalize("NFKD", text)

    # Lowercase
    text = text.lower().strip()

    # Remove version keywords inside brackets
    text = remove_version_keywords(text)

    # Remove special characters
    text = re.sub(r"[^\w\s]", "", text)

    # Remove extra spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def remove_version_keywords(text: str) -> str:
    pattern = r"\((.*?)\)"
    matches = re.findall(pattern, text)

    for match in matches:
        for keyword in VERSION_KEYWORDS:
            if keyword in match:
                text = text.replace(f"({match})", "")
                break

    return text