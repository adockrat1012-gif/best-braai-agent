"""Finds free, commercial-use braai photos. Falls back to generated fire artwork."""
import io
import json
import math
import os
import random
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFilter

UA = {"User-Agent": "best-braai-social-agent/1.0"}
TIMEOUT = 30


def _pexels(query, key):
    r = requests.get("https://api.pexels.com/v1/search", timeout=TIMEOUT,
                     headers={"Authorization": key, **UA},
                     params={"query": query, "per_page": 40, "orientation": "portrait"})
    r.raise_for_status()
    return [{"id": f"pexels-{p['id']}", "url": p["src"]["large2x"],
             "credit": f"Photo by {p['photographer']} on Pexels"} for p in r.json().get("photos", [])]


def _pixabay(query, key):
    r = requests.get("https://pixabay.com/api/", timeout=TIMEOUT, headers=UA,
                     params={"key": key, "q": query, "image_type": "photo", "per_page": 50,
                             "safesearch": "true", "min_width": 1080})
    r.raise_for_status()
    return [{"id": f"pixabay-{h['id']}", "url": h["largeImageURL"],
             "credit": f"Image by {h['user']} on Pixabay"} for h in r.json().get("hits", [])]


def _openverse(query, _key=None):
    r = requests.get("https://api.openverse.org/v1/images/", timeout=TIMEOUT, headers=UA,
                     params={"q": query, "license_type": "commercial", "page_size": 40,
                             "mature": "false", "size": "large"})
    r.raise_for_status()
    return [{"id": f"openverse-{x['id']}", "url": x["url"],
             "credit": f"\"{x.get('title') or 'Photo'}\" by {x.get('creator') or 'unknown'} "
                       f"({(x.get('license') or '').upper()} {x.get('license_version') or ''})".strip()}
            for x in r.json().get("results", [])]


def _sources():
    out = []
    if os.getenv("PEXELS_API_KEY"):
        out.append(("pexels", _pexels, os.environ["PEXELS_API_KEY"]))
    if os.getenv("PIXABAY_API_KEY"):
        out.append(("pixabay", _pixabay, os.environ["PIXABAY_API_KEY"]))
    out.append(("openverse", _openverse, None))
    return out


def _download(url):
    r = requests.get(url, timeout=60, headers=UA)
    r.raise_for_status()
    img = Image.open(io.BytesIO(r.content)).convert("RGB")
    if min(img.size) < 700:
        raise ValueError("image too small")
    return img


def fetch_images(queries, count, history_path: Path, seed: int):
    """Returns `count` (PIL.Image, credit) pairs, never reusing a photo from history."""
    used = set(json.loads(history_path.read_text())) if history_path.exists() else set()
    rng = random.Random(seed)
    results = []
    for name, fn, key in _sources():
        for q in queries:
            if len(results) >= count:
                break
            try:
                candidates = [c for c in fn(q, key) if c["id"] not in used]
            except Exception as e:  # noqa: BLE001 - any source failure just moves on
                print(f"  [{name}] search '{q}' failed: {e}")
                continue
            rng.shuffle(candidates)
            for c in candidates[:6]:
                try:
                    results.append((_download(c["url"]), c["credit"]))
                    used.add(c["id"])
                    print(f"  [{name}] {q!r} -> {c['id']}")
                    break
                except Exception as e:  # noqa: BLE001
                    print(f"  [{name}] download failed: {e}")
        if len(results) >= count:
            break

    while len(results) < count:
        print("  no photo found, generating fire artwork instead")
        results.append((generate_fire_art(seed + len(results)), ""))

    history_path.write_text(json.dumps(sorted(used)))
    return results


def generate_fire_art(seed: int, size=(1080, 1920)) -> Image.Image:
    """Procedural glowing coals & flames, used when no photo can be fetched."""
    rng = random.Random(seed)
    w, h = size
    img = Image.new("RGB", size, (12, 8, 6))
    glow = Image.new("RGB", size, (0, 0, 0))
    g = ImageDraw.Draw(glow)
    # Warm glow from the bottom
    for i in range(60):
        r = int(h * 0.9 * (1 - i / 60))
        c = (int(200 * i / 60) + 30, int(70 * i / 60), int(10 * i / 60))
        g.ellipse([w / 2 - r * 1.2, h - r * 0.6, w / 2 + r * 1.2, h + r * 0.6], fill=c)
    glow = glow.filter(ImageFilter.GaussianBlur(60))
    img = Image.blend(img, glow, 0.9)
    d = ImageDraw.Draw(img)
    # Coals
    for _ in range(140):
        x, y = rng.uniform(0, w), rng.uniform(h * 0.78, h)
        r = rng.uniform(25, 70)
        heat = rng.random()
        d.ellipse([x - r, y - r * 0.6, x + r, y + r * 0.6],
                  fill=(int(60 + 195 * heat), int(20 + 110 * heat ** 2), int(10 * heat)))
    # Flames
    flames = Image.new("RGBA", size, (0, 0, 0, 0))
    f = ImageDraw.Draw(flames)
    for _ in range(26):
        x0 = rng.uniform(w * 0.05, w * 0.95)
        height = rng.uniform(h * 0.15, h * 0.45)
        width = rng.uniform(50, 130)
        pts = []
        for t in range(0, 41):
            tt = t / 40
            yy = h * 0.85 - height * tt
            ww = width * math.sin(math.pi * (1 - tt) ** 0.7) * (1 - tt * 0.3)
            pts.append((x0 + ww + 25 * math.sin(tt * 6 + x0), yy))
        for t in range(40, -1, -1):
            tt = t / 40
            yy = h * 0.85 - height * tt
            ww = width * math.sin(math.pi * (1 - tt) ** 0.7) * (1 - tt * 0.3)
            pts.append((x0 - ww + 25 * math.sin(tt * 6 + x0), yy))
        col = rng.choice([(255, 120, 20, 110), (255, 170, 40, 100), (255, 80, 10, 120)])
        f.polygon(pts, fill=col)
    flames = flames.filter(ImageFilter.GaussianBlur(14))
    img = Image.alpha_composite(img.convert("RGBA"), flames)
    d = ImageDraw.Draw(img)
    # Sparks
    for _ in range(220):
        x, y = rng.uniform(0, w), rng.uniform(0, h * 0.8)
        r = rng.uniform(1, 4)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, rng.randint(150, 230), 80, rng.randint(80, 230)))
    return img.convert("RGB")
