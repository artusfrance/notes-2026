# Collection — inventaire des achats en vente publique

Inventaire reconstitué à partir des e-mails Gmail (factures, bordereaux d'adjudication,
notifications d'adjudication Drouot/Zacke, correspondance avec les transporteurs),
plus une petite application web pour consulter les pièces, leur emplacement dans
l'appartement et le lien vers la facture d'origine.

## Lancer l'application

```sh
cd art-collection
python3 -m http.server 8000
# puis ouvrir http://localhost:8000
```

(Un simple double-clic sur `index.html` ne fonctionne pas : le navigateur bloque la
lecture de `data/collection.json` en `file://`.)

## Contenu

- `data/collection.json` — le jeu de données : une entrée par lot ou par facture,
  avec maison de vente, vente, lot, prix, référence de facture et identifiant du fil
  Gmail correspondant.
- `index.html` / `app.js` / `styles.css` — l'application (recherche, filtres par maison,
  catégorie, année et pièce de l'appartement ; fiche détaillée ; lien vers la facture Gmail).
- `invoices/` — les factures et bordereaux d'adjudication (30 PDF) extraits des e-mails,
  avec un `README.md` qui dit à quelle vente chaque fichier correspond. La fiche d'une
  pièce ouvre directement sa facture.
- `photos/` — déposez `photos/<id>.jpg` (l'`id` de l'entrée dans le JSON) pour que la
  photo s'affiche automatiquement sur la fiche.
- `tools/extract_invoice.py` — extrait les pièces jointes d'un message Gmail récupéré au
  format RAW (c'est ainsi que les factures ont été versées).
- `tools/build_artifact.py` — fabrique la page publiée chez Claude à partir de
  `artifact-template.html`, du jeu de données et des photos.
- `data/notices.json` — les notices détaillées, fusionnées dans `collection.json`.

## Emplacements dans l'appartement

Les emplacements et notes saisis dans l'application sont enregistrés dans le
`localStorage` du navigateur (donc sur cet appareil uniquement). Le bouton
« Exporter emplacements (JSON) » produit un fichier `emplacements.json` à reverser dans
`data/collection.json` pour les figer dans le dépôt.

## Limites connues

- Six entrées restent incomplètes (`confidence: "a_verifier"`, champ `todo`) : la Galerie
  Zacke facture par lien vers son extranet plutôt qu'en pièce jointe, et Catawiki, Le Floc'h
  et Bonino n'ont envoyé aucun détail de lot.
- **Photos** : les sites des maisons de vente restent inaccessibles depuis la session
  (zacke.at, millon.com, tajan.com, auction.de, artcurial.com sont bloqués par la politique
  réseau). Les huit photos présentes viennent du Google Drive de la collection ; les autres
  pièces attendent une photo dans `photos/<id>.jpg`.
- Chaque entrée porte une `notice` : période, iconographie, technique et provenance. Le texte
  propre à l'objet vient de la facture ou de la notice de lot ; le contexte historique est
  signalé comme tel dans `data/notices.json`.
- Les achats antérieurs à 2013 et les achats réglés hors e-mail (galeries, ventes de gré
  à gré) ne sont pas exhaustifs.
- Les frais de transport et d'assurance ne sont pas comptés comme des œuvres ; ils sont
  mentionnés dans le champ `delivery` ou listés dans `aVerifier`.

## Miroir Google Drive

Le dossier Drive **ARTS** porte un sous-dossier par objet, numéroté dans l'ordre
chronologique inverse (`NN - AAAA-MM Maison lot X - Désignation`). Chacun contient
une fiche Google Doc, la ou les factures, et les photos.

`data/collection.json` porte pour chaque entrée `driveFolderId`, `driveFolderName`,
`driveUrl` et `driveDocs` (la liste des pièces, avec leur lien direct), plus
`meta.driveRoot` pour la racine.

Les numéros suivent l'ordre chronologique : une date corrigée ou un objet inséré
oblige à renuméroter les dossiers concernés. Le nom canonique est recalculé par le
script de construction à partir de `saleDate`, `house`, `lot` et de la désignation
courte conservée dans `driveFolderName`.

## Poids de la page publiée

La plateforme refuse une page de plus de 16 Mo et le gabarit refuse de se
réenregistrer au-delà de 12 Mo. `tools/build_artifact.py` vise nettement en
dessous :

- **rien n'est embarqué qui puisse être lié.** Factures, rapports et catalogues
  vivent dans Drive ou dans ce dépôt ; la fiche porte des liens. Sortir le PDF du
  rapport CIRAM a rendu 2,3 Mo à lui seul.
- **les photos s'adaptent.** Le script essaie les paliers de `PRESETS`, du plus
  généreux (1200 px, qualité 78) au plus économe (600 px, qualité 60), et retient
  le premier dont le total tient dans `PHOTO_BUDGET` (6 Mo). La page rétrécit donc
  d'elle-même à mesure que la collection grandit, sans intervention.
- **la construction échoue** si la page dépasse `HARD_LIMIT` (11 Mo), et prévient
  au-delà de `WARN_LIMIT` (8 Mo). Chaque construction annonce la marge restante
  en nombre de photos.

Au 27 août 2026 : 35 entrées, 3,6 Mo, 18 photos, 48 documents liés.

Les objets sortis de la collection — offerts, revendus, acquis pour un tiers —
ne sont pas détruits : leur dossier Drive est déplacé sous « ZZ - Hors collection »,
leurs factures restant des justificatifs d'achat.
