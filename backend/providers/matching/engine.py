from rapidfuzz import fuzz
from .normalizer import normalize_text
from providers.matching.track import UniversalTrack
import re

""" Concept for matching """
# So your scoring must reflect:
# 95-100 → Confident same recording, auto match into new playlist
# 80-94 → Very safe substitution, give user few strong suggestions, (high confidence match)
# 65-79 → Related but different recording, Weak match
# <65 → Conflict / do not auto-match, reject, no match
# In the middle 2 tiers, user will be showed suggestions, for their song, but there should be difference, think about it. 


# ---------- VERSION CONSTANTS ----------

STUDIO = "studio"
MINOR_VARIANT = "minor_variant"
LIVE = "live"
ACOUSTIC = "acoustic"
REMIX = "remix"
EXTENDED = "extended"
INTERNET_VARIANT = "internet_variant"
EDIT = "edit"
COVER = "cover"

VERSION_KEYWORDS = {
    REMIX: ["remix", "vip", "bootleg", "flip", "rework", "mashup","remake", "refix", "edit remix", "club remix", "festival remix"],
    LIVE: ["live", "live version", "live at", "session","unplugged", "mtv unplugged", "concert version", "concert"],
    ACOUSTIC: ["acoustic", "acoustic version","stripped", "stripped down", "piano version"],
    EDIT: ["edit", "radio edit", "clean", "explicit","short edit", "album edit"],
    EXTENDED: ["extended", "extended mix","club mix", "original mix","long version"],
    MINOR_VARIANT: ["remastered","anniversary edition","deluxe edition","demo", "anniversary", "deluxe"],
    INTERNET_VARIANT: ["slowed","sped up","nightcore","phonk","8d","bass boosted","lofi","lo-fi"],
    COVER: ["cover","tribute","karaoke"]
}


# ==============================
# Version Score Matrix
# ==============================

VERSION_SCORE_MATRIX = {

    # Perfect same-type matches
    (STUDIO, STUDIO): 100,
    (LIVE, LIVE): 90,   # reduced from 100, because it could be 2 different live versions, will have to tackle later.
    (REMIX, REMIX): 90, # reduced from 100, because it could be 2 different remixrs, will have to tackle later.
    (ACOUSTIC, ACOUSTIC): 100,
    (EXTENDED, EXTENDED): 100,
    (MINOR_VARIANT, MINOR_VARIANT): 95,
    (INTERNET_VARIANT, INTERNET_VARIANT): 100,

    (STUDIO, MINOR_VARIANT): 95,
    (STUDIO, LIVE): 65,
    (STUDIO, ACOUSTIC): 65,
    (STUDIO, REMIX): 65,
    (STUDIO, EXTENDED): 65,
    (STUDIO, EDIT): 95,
    (STUDIO, INTERNET_VARIANT): 70,
    (LIVE, REMIX): 60,
    (LIVE, INTERNET_VARIANT): 55,
    (REMIX, INTERNET_VARIANT): 55,
    (COVER, STUDIO): 50.0
}

# ---------- VERSION DETECTION ----------

def get_version_tag(normalized_title: str) -> str:
    for tag, keywords in VERSION_KEYWORDS.items():
        for keyword in keywords:
            if re.search(rf"\b{re.escape(keyword)}\b", normalized_title):
                return tag
    return STUDIO


# ---------- CORE TITLE EXTRACTION ----------

def extract_core_title(normalized_title: str) -> str:
    """ Remove version keywords but ONLY for base comparison. """
    all_keywords = [word for words in VERSION_KEYWORDS.values() for word in words]
    all_keywords.sort(key=len, reverse=True)

    for word in all_keywords:
        normalized_title = re.sub(rf"\b{re.escape(word)}\b","",normalized_title)

    normalized_title = re.sub(r"[-_()\[\]]", " ", normalized_title)
    return " ".join(normalized_title.split())

def analyze_title(title: str) -> dict:
    normalized = normalize_text(title)
    version = get_version_tag(normalized)
    core = extract_core_title(normalized)

    return {
        "original": title,
        "normalized": normalized,
        "version": version,
        "core": core
    }


# ---------- MATCH ENGINE ----------

def get_match_score(source, candidate) -> float:

    # 1️⃣ ISRC GOD MODE
    if source.isrc and candidate.isrc and source.isrc == candidate.isrc:
        return 100.0

    # 2️⃣ Analyze titles properly (normalize + tag + core)
    src_data = analyze_title(source.title)
    can_data = analyze_title(candidate.title)

    src_tag = src_data["version"]
    can_tag = can_data["version"]

    src_core = src_data["core"]
    can_core = can_data["core"]

    # 3️⃣ Fuzzy
    title_fuzzy = fuzz.token_set_ratio(src_core, can_core)
    artist_fuzzy = fuzz.token_sort_ratio(source.primary_artist(),candidate.primary_artist())

    # 4️⃣ Early fallback
    if title_fuzzy < 85 or artist_fuzzy < 80:
        raw_score = (title_fuzzy * 0.6) + (artist_fuzzy * 0.4)
        return min(raw_score, 65.0)

    # 5️⃣ Version Matrix
    pair = (src_tag, can_tag)

    if pair in VERSION_SCORE_MATRIX:
        return float(VERSION_SCORE_MATRIX[pair])

    rev_pair = (can_tag, src_tag)
    if rev_pair in VERSION_SCORE_MATRIX:
        return float(VERSION_SCORE_MATRIX[rev_pair])

    if src_tag == can_tag:
        return 95.0 if src_tag == STUDIO else 90.0

    return 65.0