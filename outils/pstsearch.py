import sys, re, json, pypff, datetime
pst = sys.argv[1]; out = sys.argv[2]
kw = re.compile(r"vesgre|inond|crue|d[ée]bord|batardeau|pompe de relevage|fausse rivi|rivi[èe]re|berge|syndicat|gemapi|catastrophe naturelle|polyexpert|sinistre|mairie de bourdonn|houdanais|moulin de boyauville|vanne|bief", re.I)
f = pypff.file(); f.open(pst)
root = f.get_root_folder()
hits = []; n = 0
def walk(folder, path):
    global n
    for i in range(folder.number_of_sub_messages):
        try: m = folder.get_sub_message(i)
        except Exception: continue
        n += 1
        if n % 2000 == 0: print("...", n, "messages lus,", len(hits), "trouvés", flush=True)
        subj = m.subject or ""; 
        try: body = m.plain_text_body
        except Exception: body = None
        if body is None:
            try: body = m.html_body
            except Exception: body = None
        if isinstance(body, bytes):
            body = body.decode("utf-8", "ignore") if b"\xc3" in body else body.decode("cp1252", "ignore")
        body = body or ""
        text = subj + "\n" + body
        if kw.search(text):
            try: d = m.delivery_time or m.client_submit_time
            except Exception: d = None
            atts = []
            try:
                for a in range(m.number_of_attachments):
                    at = m.get_attachment(a)
                    try: atts.append(at.name)
                    except Exception: atts.append("?")
            except Exception: pass
            hits.append({"folder": path, "date": d.isoformat() if d else None, "from": m.sender_name, "subject": subj, "att": atts, "body": re.sub(r"\s+"," ", body)[:3000]})
    for j in range(folder.number_of_sub_folders):
        sf = folder.get_sub_folder(j); walk(sf, path + "/" + (sf.name or ""))
walk(root, "")
hits.sort(key=lambda h: h["date"] or "")
json.dump(hits, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("messages scanned:", n, "hits:", len(hits))
