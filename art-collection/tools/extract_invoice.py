#!/usr/bin/env python3
"""Extrait les pièces jointes d'un message Gmail récupéré au format RAW.

Usage : extract_invoice.py <fichier-json-du-tool-result> <dossier-de-sortie> [prefixe]

Le fichier d'entrée est la réponse JSON de Gmail get_message(messageFormat=RAW) :
le champ `raw` contient le message MIME complet encodé en base64url.
"""
import base64
import email
import json
import re
import sys
from pathlib import Path

KEEP_EXT = (".pdf",)  # les factures ; le type MIME annoncé varie (souvent octet-stream)


def slug(text):
    return re.sub(r"[^A-Za-z0-9._-]+", "-", text).strip("-")[:80]


def main():
    src, outdir = Path(sys.argv[1]), Path(sys.argv[2])
    prefix = sys.argv[3] if len(sys.argv) > 3 else ""
    outdir.mkdir(parents=True, exist_ok=True)

    payload = json.loads(src.read_text())
    raw = base64.urlsafe_b64decode(payload["raw"] + "=" * (-len(payload["raw"]) % 4))
    msg = email.message_from_bytes(raw)

    saved = []
    for part in msg.walk():
        if part.get_content_maintype() == "multipart":
            continue
        name = part.get_filename()
        if not name or not name.lower().endswith(KEEP_EXT):
            continue
        data = part.get_payload(decode=True)
        if not data or len(data) < 4000:  # ignore les logos de signature
            continue
        target = outdir / slug(f"{prefix}{name}" if prefix else name)
        target.write_bytes(data)
        saved.append((target.name, len(data)))

    for name, size in saved:
        print(f"{name}\t{size // 1024} Ko")
    if not saved:
        print("aucune pièce jointe exploitable")


if __name__ == "__main__":
    main()
