#!/usr/bin/env python3
"""
Generate a small synthetic dataset for QuickCommand.

- 7 intents
- Parameterized templates
- Optional ASR-style noise (insert/delete/substitute)

Usage:
  python scripts/generate_dataset.py --out data/dataset.jsonl --per-class 100 --noise 0.15
"""

import os, json, argparse, random, re

INTENTS = [
    "move", "altitude", "rotate", "hover", "takeoff", "land", "emergency_stop"
]

# Simple vocab for parameterization
DIRECTIONS = ["left", "right", "forward", "back"]
METERS = [str(m) for m in [1,2,3,4,5,6,7,8,9,10]]
SECONDS = [str(s) for s in [1,2,3,4,5,10,15]]
DEGREES = [str(d) for d in [15,30,45,60,90,120,180]]

# Templates per intent (a few variations for each)
TEMPLATES = {
    "move": [
        "move {dir} {n} meters",
        "go {dir} {n} meters",
        "shift {dir} by {n} meters",
    ],
    "altitude": [
        "go up {n} meters",
        "go down {n} meters",
        "ascend {n} meters",
        "descend {n} meters",
    ],
    "rotate": [
        "rotate {dir} {deg} degrees",
        "yaw {dir} {deg} degrees",
        "turn {dir} {deg} degrees",
    ],
    "hover": [
        "hover here for {s} seconds",
        "hold position for {s} seconds",
        "stay still for {s} seconds",
        "hover now",
    ],
    "takeoff": [
        "take off now",
        "arm and take off",
        "lift off",
    ],
    "land": [
        "land now",
        "land gently",
        "descend and land",
    ],
    "emergency_stop": [
        "abort mission immediately",
        "stop now emergency",
        "kill motion now",
        "emergency stop",
    ],
}

NOISE_TOKENS = ["uh", "please", "now", "quick", "okay", "um"]

def inject_noise(text: str, noise_rate: float) -> str:
    """ASR-style noise: random insert/delete/substitute tokens."""
    if noise_rate <= 0:
        return text
    tokens = text.split()
    new_tokens = []
    for t in tokens:
        r = random.random()
        if r < noise_rate/3:
            # deletion: skip this token
            continue
        elif r < 2*noise_rate/3:
            # substitution
            new_tokens.append(random.choice(NOISE_TOKENS))
        else:
            # keep original
            new_tokens.append(t)
            # occasional insertion
            if random.random() < noise_rate/4:
                new_tokens.append(random.choice(NOISE_TOKENS))
    # light cleanup for double spaces
    out = re.sub(r"\s+", " ", " ".join(new_tokens)).strip()
    return out if out else text  # never return empty

def sample_utterance(intent: str) -> str:
    tpl = random.choice(TEMPLATES[intent])
    if intent == "move":
        return tpl.format(dir=random.choice(DIRECTIONS), n=random.choice(METERS))
    if intent == "altitude":
        updown = random.choice(["up", "down"])
        return tpl.replace("{n}", random.choice(METERS)).replace("go up", f"go {updown}")
    if intent == "rotate":
        dir_lr = random.choice(["left", "right"])
        return tpl.format(dir=dir_lr, deg=random.choice(DEGREES))
    if intent == "hover":
        # some templates don't need seconds
        if "{s}" in tpl:
            return tpl.format(s=random.choice(SECONDS))
        return tpl
    # simple templates:
    return tpl

def make_records(per_class: int, noise_rate: float):
    for intent in INTENTS:
        for _ in range(per_class):
            clean = sample_utterance(intent)
            noisy = inject_noise(clean, noise_rate)
            yield {"text": noisy, "label": intent}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True, help="Output JSONL path")
    p.add_argument("--per-class", type=int, default=100, help="Examples per class")
    p.add_argument("--noise", type=float, default=0.15, help="ASR-style noise rate (0..0.5)")
    args = p.parse_args()

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    count = 0
    with open(args.out, "w", encoding="utf-8") as f:
        for rec in make_records(args.per_class, max(0.0, min(args.noise, 0.5))):
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            count += 1
    print(f"Wrote {count} examples to {args.out}")

if __name__ == "__main__":
    random.seed(42)
    main()
