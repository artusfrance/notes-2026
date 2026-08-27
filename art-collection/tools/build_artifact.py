#!/usr/bin/env python3
"""Injecte data/collection.json dans artifact-template.html.

Usage : build_artifact.py <fichier-de-sortie.html>

La page publiée porte son propre état : chaque entrée du JSON devient un objet
avec ses champs d'inventaire plus `location`, `notes` et `photo`, que la page
met à jour et réenregistre elle-même via la capacité « artifact ».

Les documents — factures, rapports, catalogues — ne sont pas embarqués : la
fiche porte des liens vers le dossier Google Drive de l'objet et vers chaque
pièce. Seules les photos et les pages de rapport annexées pèsent sur la page,
et leur encodage s'adapte pour tenir dans PHOTO_BUDGET.
"""
import base64
import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KEYS = ["id", "title", "category", "origin", "house", "city", "sale", "saleDate", "lot",
        "price", "currency", "priceNote", "invoiceRef", "invoiceNote", "delivery",
        "confidence", "todo", "lotUrl", "notice", "photoSource", "science",
        "driveUrl", "driveDocs", "reportUrl", "acquisition", "valuation"]

# Budgets. La limite dure de la plateforme est de 16 Mo ; le gabarit refuse de
# se réenregistrer au-delà de 12 Mo. On vise nettement en dessous pour laisser
# la collection grandir.
PHOTO_BUDGET = 6_000_000      # octets de photos, une fois encodées en base64
HARD_LIMIT = 11_000_000       # caractères ; au-delà, la construction échoue
WARN_LIMIT = 8_000_000

# Du plus généreux au plus économe. Le premier palier qui tient est retenu.
PRESETS = [(1200, 78), (1000, 75), (900, 72), (800, 70), (700, 66), (600, 60)]


def encode_photo(name, max_px, quality):
    """photos/<name> en data URI, redimensionnée au palier demandé."""
    path = ROOT / "photos" / name
    if not path.exists():
        return ""
    from PIL import Image
    img = Image.open(path).convert("RGB")
    scale = min(1.0, max_px / max(img.size))
    if scale < 1:
        img = img.resize((round(img.width * scale), round(img.height * scale)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=quality, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def pick_preset(names):
    """Le palier le plus généreux dont le total tient dans PHOTO_BUDGET."""
    for max_px, quality in PRESETS:
        photos = {n: encode_photo(n, max_px, quality) for n in names}
        total = sum(len(v) for v in photos.values())
        if total <= PHOTO_BUDGET or (max_px, quality) == PRESETS[-1]:
            return (max_px, quality), photos, total
    raise AssertionError("palier introuvable")


def page_data_uri(name):
    """Page de rapport rendue en image, embarquée dans la page publiée."""
    path = ROOT / "reports" / "pages" / name
    if not path.exists():
        return ""
    return "data:image/jpeg;base64," + base64.b64encode(path.read_bytes()).decode()


def main():
    out = Path(sys.argv[1])
    data = json.loads((ROOT / "data" / "collection.json").read_text())

    firsts = [src["photos"][0] for src in data["items"] if src.get("photos")]
    (max_px, quality), photos, photo_total = pick_preset(firsts)

    items = []
    for src in data["items"]:
        item = {k: src[k] for k in KEYS if src.get(k) not in (None, "", [])}
        item["price"] = src.get("price")
        item["thread"] = src.get("gmailThreadId")
        item["location"] = src.get("location", "")
        item["notes"] = src.get("notes", "")
        first = (src.get("photos") or [None])[0]
        item["photo"] = photos.get(first, "") if first else ""
        pages = src.get("reportPages") or []
        item["reportPages"] = [page_data_uri(p) for p in pages]
        items.append(item)

    state = {"version": 1, "updated": data["meta"]["generated"], "items": items}
    payload = json.dumps(state, ensure_ascii=False).replace("<", "\\u003c")

    html = (ROOT / "artifact-template.html").read_text()
    assert "__STATE__" in html, "marqueur __STATE__ absent du gabarit"
    page = html.replace("__STATE__", payload)

    size = len(page)
    if size > HARD_LIMIT:
        sys.exit(f"ERREUR : page de {size/1e6:.1f} Mo, au-dessus de la limite de "
                 f"{HARD_LIMIT/1e6:.0f} Mo. Réduire PHOTO_BUDGET, ou sortir des pages "
                 f"de rapport vers Drive.")
    out.write_text(page)

    docs = sum(len(s.get("driveDocs") or []) for s in data["items"])
    print(f"{out} — {len(items)} entrées, {size/1e6:.2f} Mo")
    print(f"  photos : {len(firsts)} à {max_px} px / qualité {quality} — {photo_total/1e6:.2f} Mo")
    print(f"  documents liés (non embarqués) : {docs}")
    if size > WARN_LIMIT:
        print(f"  ATTENTION : au-dessus du seuil de confort de {WARN_LIMIT/1e6:.0f} Mo.")
    else:
        marge = (HARD_LIMIT - size) / max(photo_total / max(len(firsts), 1), 1)
        print(f"  marge : environ {int(marge)} photos supplémentaires avant la limite.")


if __name__ == "__main__":
    main()
