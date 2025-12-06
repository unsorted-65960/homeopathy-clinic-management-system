# utils/normalize.py
import re
import unicodedata

PREFIXES = [
    r"^mr[\.\s]+", r"^mrs[\.\s]+", r"^miss[\.\s]+", r"^ms[\.\s]+",
    r"^dr[\.\s]+", r"^shri[\.\s]+", r"^smt[\.\s]+", r"^shreemati[\.\s]+"
]
_prefix_re = re.compile("|".join(PREFIXES), flags=re.IGNORECASE)
_nonword_re = re.compile(r"[^\w\s]", flags=re.UNICODE)

def normalize_name(s: str) -> str:
    if not s:
        return ""
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = s.lower().strip()
    s = _prefix_re.sub("", s)
    s = _nonword_re.sub(" ", s)
    s = " ".join(s.split())
    return s
