const STORE_KEY = 'collection-emplacements-v1';
const GMAIL = id => `https://mail.google.com/mail/u/0/#all/${id}`;

let items = [];
let meta = {};
let local = load();

function load() {
  try { return JSON.parse(localStorage.getItem(STORE_KEY)) || {}; }
  catch { return {}; }
}
function save() {
  try { localStorage.setItem(STORE_KEY, JSON.stringify(local)); return true; }
  catch { return false; }
}
function merged(item) {
  const over = local[item.id] || {};
  return { ...item, location: over.location ?? item.location ?? '', notes: over.notes ?? item.notes ?? '' };
}
function money(item) {
  if (item.price == null) return '—';
  const symbol = item.currency === 'GBP' ? '£' : '€';
  return `${item.price.toLocaleString('fr-FR')} ${symbol}`;
}
function year(item) {
  return (item.saleDate || '').slice(0, 4);
}

fetch('data/collection.json')
  .then(r => r.json())
  .then(data => {
    meta = data.meta || {};
    items = data.items || [];
    buildFilters();
    render();
  })
  .catch(() => {
    document.getElementById('summary').textContent =
      "Impossible de charger data/collection.json — lancez un serveur local : python3 -m http.server 8000";
  });

function buildFilters() {
  fill('house', [...new Set(items.map(i => i.house))].sort());
  fill('category', [...new Set(items.map(i => i.category))].sort());
  fill('year', [...new Set(items.map(year))].sort().reverse());
  refreshRooms();
  ['q', 'house', 'category', 'year', 'room'].forEach(id =>
    document.getElementById(id).addEventListener('input', render));
  document.getElementById('export').addEventListener('click', exportLocations);
  document.getElementById('close').addEventListener('click', closePanel);
  document.getElementById('scrim').addEventListener('click', closePanel);
}
function fill(id, values) {
  const sel = document.getElementById(id);
  values.forEach(v => {
    if (!v) return;
    const o = document.createElement('option');
    o.value = v; o.textContent = v;
    sel.appendChild(o);
  });
}
function refreshRooms() {
  const sel = document.getElementById('room');
  const current = sel.value;
  sel.innerHTML = '<option value="">Tous les emplacements</option>';
  const rooms = [...new Set(items.map(i => merged(i).location).filter(Boolean))].sort();
  fill('room', rooms);
  const nl = document.createElement('option');
  nl.value = '__none__'; nl.textContent = 'Sans emplacement';
  sel.appendChild(nl);
  sel.value = current;
}

function render() {
  const q = document.getElementById('q').value.trim().toLowerCase();
  const house = document.getElementById('house').value;
  const category = document.getElementById('category').value;
  const yr = document.getElementById('year').value;
  const room = document.getElementById('room').value;

  const shown = items.map(merged).filter(i => {
    if (house && i.house !== house) return false;
    if (category && i.category !== category) return false;
    if (yr && year(i) !== yr) return false;
    if (room === '__none__' && i.location) return false;
    if (room && room !== '__none__' && i.location !== room) return false;
    if (!q) return true;
    return [i.title, i.house, i.sale, i.lot, i.origin, i.invoiceRef, i.location, i.notes]
      .filter(Boolean).join(' ').toLowerCase().includes(q);
  }).sort((a, b) => (b.saleDate || '').localeCompare(a.saleDate || ''));

  const grid = document.getElementById('grid');
  grid.innerHTML = '';
  shown.forEach(i => grid.appendChild(card(i)));
  document.getElementById('empty').hidden = shown.length > 0;

  const placed = items.map(merged).filter(i => i.location).length;
  document.getElementById('summary').textContent =
    `${items.length} entrées · ${shown.length} affichées · ${placed} localisées · ` +
    `${items.filter(i => i.confidence === 'a_verifier').length} à compléter depuis les factures PDF`;
}

function card(i) {
  const el = document.createElement('article');
  el.className = 'card';
  el.tabIndex = 0;

  const thumb = document.createElement('div');
  thumb.className = 'thumb';
  const img = document.createElement('img');
  img.alt = i.title;
  img.loading = 'lazy';
  img.src = `photos/${i.id}.jpg`;
  img.onerror = () => { thumb.textContent = 'photo à ajouter'; };
  thumb.appendChild(img);

  const body = document.createElement('div');
  body.className = 'card-body';
  const h = document.createElement('h3');
  h.textContent = i.title;
  const m = document.createElement('p');
  m.className = 'meta';
  m.textContent = `${i.house} · ${fmtDate(i.saleDate)}${i.lot ? ' · lot ' + i.lot : ''} · ${money(i)}`;
  const tags = document.createElement('div');
  tags.className = 'tags';
  tags.appendChild(tag(i.category));
  if (i.location) tags.appendChild(tag(i.location, 'room'));
  if (i.confidence === 'a_verifier') tags.appendChild(tag('à compléter', 'todo'));

  body.append(h, m, tags);
  el.append(thumb, body);
  el.addEventListener('click', () => openPanel(i.id));
  el.addEventListener('keydown', e => { if (e.key === 'Enter') openPanel(i.id); });
  return el;
}
function tag(text, cls) {
  const s = document.createElement('span');
  s.className = 'tag' + (cls ? ' ' + cls : '');
  s.textContent = text;
  return s;
}
function fmtDate(d) {
  if (!d) return '—';
  const [y, m, day] = d.split('-');
  return `${day}/${m}/${y}`;
}

function openPanel(id) {
  const i = merged(items.find(x => x.id === id));
  const body = document.getElementById('panelBody');
  body.innerHTML = '';

  const h = document.createElement('h2');
  h.textContent = i.title;
  const sub = document.createElement('p');
  sub.className = 'meta';
  sub.textContent = `${i.house} — ${i.city}`;

  if (i.notice) {
    const notice = document.createElement('p');
    notice.className = 'notice';
    notice.textContent = i.notice;
    body.appendChild(notice);
  }

  const dl = document.createElement('dl');
  const rows = [
    ['Vente', i.sale],
    ['Date', fmtDate(i.saleDate)],
    ['Lot', i.lot],
    ['Prix', money(i)],
    ['Détail prix', i.priceNote],
    ['Facture', i.invoiceRef],
    ['Note facture', i.invoiceNote],
    ['Description', i.origin],
    ['Livraison', i.delivery],
    ['Analyse scientifique', i.science],
    ['À faire', i.todo],
  ];
  rows.forEach(([k, v]) => {
    if (!v || v === '—') return;
    const dt = document.createElement('dt'); dt.textContent = k;
    const dd = document.createElement('dd'); dd.textContent = v;
    dl.append(dt, dd);
  });

  body.append(h, sub, dl);

  const links = document.createElement('div');
  links.style.display = 'grid';
  links.style.gap = '4px';
  const link = (href, text) => {
    const a = document.createElement('a');
    a.href = href;
    a.target = '_blank';
    a.rel = 'noopener';
    a.textContent = text;
    links.appendChild(a);
  };
  if (i.invoiceFile) link(`invoices/${i.invoiceFile}`, 'Ouvrir la facture (PDF) →');
  (i.reports || []).forEach(r => link(`reports/${r}`, 'Ouvrir le rapport scientifique (PDF) →'));
  if (i.lotUrl) link(i.lotUrl, 'Voir la fiche du lot chez la maison de vente →');
  if (i.gmailThreadId) link(GMAIL(i.gmailThreadId), 'Ouvrir le fil Gmail →');
  body.appendChild(links);

  const locLabel = document.createElement('label');
  locLabel.textContent = "Emplacement dans l'appartement";
  const loc = document.createElement('input');
  loc.value = i.location;
  loc.placeholder = 'Ex. Salon — mur cheminée';
  const noteLabel = document.createElement('label');
  noteLabel.textContent = 'Notes personnelles';
  const note = document.createElement('textarea');
  note.value = i.notes;
  const status = document.createElement('p');
  status.className = 'saved';

  const persist = () => {
    local[i.id] = { location: loc.value.trim(), notes: note.value.trim() };
    status.textContent = save() ? 'Enregistré sur cet appareil' : 'Stockage indisponible dans ce navigateur';
    refreshRooms();
    render();
  };
  loc.addEventListener('change', persist);
  note.addEventListener('change', persist);

  const hint = document.createElement('p');
  hint.className = 'note';
  hint.textContent = "Photos : déposez un fichier photos/" + i.id + ".jpg pour l'afficher sur la fiche.";

  body.append(locLabel, loc, noteLabel, note, status, hint);
  document.getElementById('panel').hidden = false;
  document.getElementById('scrim').hidden = false;
}
function closePanel() {
  document.getElementById('panel').hidden = true;
  document.getElementById('scrim').hidden = true;
}

function exportLocations() {
  const payload = items.map(merged).map(i => ({
    id: i.id, title: i.title, location: i.location, notes: i.notes
  }));
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'emplacements.json';
  a.click();
  URL.revokeObjectURL(url);
}
