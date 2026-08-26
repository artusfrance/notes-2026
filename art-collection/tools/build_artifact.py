#!/usr/bin/env python3
"""Injecte data/collection.json dans artifact-template.html.

Usage : build_artifact.py <fichier-de-sortie.html>

La page publiée porte son propre état : chaque entrée du JSON devient un objet
avec ses champs d'inventaire plus `location`, `notes` et `photo`, que la page
met à jour et réenregistre elle-même via la capacité « artifact ».
"""
import base64
import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KEYS = ["id", "title", "category", "origin", "house", "city", "sale", "saleDate", "lot",
        "price", "currency", "priceNote", "invoiceRef", "invoiceNote", "delivery",
        "confidence", "todo", "lotUrl", "invoiceFile", "notice", "photoSource", "science", "reports"]
PHOTO_MAX = 1200
PHOTO_QUALITY = 78


def photo_data_uri(name):
    """Encode photos/<name> en data URI, à la taille où la page reste légère."""
    path = ROOT / "photos" / name
    if not path.exists():
        return ""
    from PIL import Image
    img = Image.open(path).convert("RGB")
    scale = min(1.0, PHOTO_MAX / max(img.size))
    if scale < 1:
        img = img.resize((round(img.width * scale), round(img.height * scale)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=PHOTO_QUALITY, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def main():
    out = Path(sys.argv[1])
    data = json.loads((ROOT / "data" / "collection.json").read_text())

    items = []
    for src in data["items"]:
        item = {k: src[k] for k in KEYS if src.get(k) not in (None, "", [])}
        item["price"] = src.get("price")
        item["thread"] = src.get("gmailThreadId")
        item["location"] = src.get("location", "")
        item["notes"] = src.get("notes", "")
        photos = src.get("photos") or []
        item["photo"] = photo_data_uri(photos[0]) if photos else ""
        items.append(item)

    state = {"version": 1, "updated": data["meta"]["generated"], "items": items}
    payload = json.dumps(state, ensure_ascii=False).replace("<", "\\u003c")

    html = (ROOT / "artifact-template.html").read_text()
    assert "__STATE__" in html, "marqueur __STATE__ absent du gabarit"
    out.write_text(html.replace("__STATE__", payload))
    print(f"{out} — {len(items)} entrées, {len(out.read_text())} caractères")


if __name__ == "__main__":
    main()
