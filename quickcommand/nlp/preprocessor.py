
# QuickCommand NLP preprocessor (minimal stub)
# - Normalizes text
# - Extracts simple parameters (meters, degrees, seconds, direction)

import re

DIRS = ["left", "right", "forward", "back", "backward", "up", "down"]

def normalize(text: str) -> str:
    t = text.lower().strip()
    t = re.sub(r"[^\w\s]", " ", t)      # drop punctuation
    t = re.sub(r"\s+", " ", t)          # collapse spaces
    return t

def extract_params(text: str) -> dict:
    t = normalize(text)
    params = {}
    m = re.search(r"\b(\d+)\s*(m|meter|meters)\b", t)
    if m: params["meters"] = int(m.group(1))
    d = re.search(r"\b(\d+)\s*(deg|degree|degrees)\b", t)
    if d: params["degrees"] = int(d.group(1))
    s = re.search(r"\b(\d+)\s*(s|sec|secs|second|seconds)\b", t)
    if s: params["seconds"] = int(s.group(1))
    for d in DIRS:
        if re.search(rf"\b{d}\b", t):
            params["direction"] = d
            break
    return params
