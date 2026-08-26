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

Le dossier Drive **ARTS** porte un sous-dossier par objet, numéroté de 01 à 42
dans l'ordre chronologique inverse (`NN - AAAA-MM Maison lot X - Désignation`).
Chacun contient une fiche Google Doc (identité, prix, référence de facture,
livraison, emplacement, lien vers le PDF de la facture ici) et les photos ou
documents déjà présents dans le Drive.

`data/collection.json` porte pour chaque entrée `driveFolderId`, `driveFolderName`
et `driveUrl`, plus `meta.driveRoot` pour la racine.

Les 30 PDF de factures ont été déposés dans Drive et répartis dans les dossiers
d'objets : original dans le dossier du premier lot, copie dans les autres quand
une même facture couvre plusieurs lots (Tajan ET00095181, Millon 3067-46,
Millon Belgique 20097-208, Artcurial 91483, Millon A-1193-77).

Six objets n'ont pas de facture, faute de document existant : Templum lot 379
(à recevoir), Zacke 27310 (accessible par lien dans le mail du 10/12/2024),
Eve lot 486, Le Floc'h 2022, Catawiki 2018 et Artcurial 2009 lot 56.

Le rapport CIRAM reste hébergé ici : les fiches Drive y renvoient par lien.
