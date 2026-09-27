"""Regenerate web-sized gallery images from originals in raw/art/ (NN.jpg + index.json).

Usage: python3 scripts/make_art.py
Writes public/images/art/NN.jpg (1800px) and NN_thumb.jpg (700px), and src/data/art.json.
Add a new painting by dropping raw/art/13.jpg and appending {"file": "13.jpg", "title": "..."} to raw/art/index.json.
"""
import json, pathlib
from PIL import Image, ImageOps

ROOT = pathlib.Path(__file__).resolve().parent.parent
RAW, OUT = ROOT / "raw" / "art", ROOT / "public" / "images" / "art"
OUT.mkdir(parents=True, exist_ok=True)
meta = json.load(open(RAW / "index.json"))
out = []
for m in meta:
    fn = pathlib.Path(m["file"]).name
    im = ImageOps.exif_transpose(Image.open(RAW / fn)).convert("RGB")
    base = fn.split(".")[0]
    for w, suffix in [(1800, ""), (700, "_thumb")]:
        r = im.copy(); r.thumbnail((w, w * 2))
        r.save(OUT / f"{base}{suffix}.jpg", quality=82, optimize=True, progressive=True)
    out.append({"file": fn, "title": m.get("title", ""), "src": f"/images/art/{base}.jpg",
                "thumb": f"/images/art/{base}_thumb.jpg", "width": im.width, "height": im.height})
json.dump(out, open(ROOT / "src" / "data" / "art.json", "w"), indent=2, ensure_ascii=False)
print("wrote", len(out), "images")
