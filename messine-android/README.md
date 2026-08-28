# Collection de Messine — application Android

Réplique sur téléphone de l'inventaire « Collection de Messine » : les 46 pièces,
leurs photos et leurs fiches, avec un lien direct vers le dossier Google Drive de
chaque objet.

## Récupérer l'APK

Aucun Android Studio n'est nécessaire. À chaque modification poussée, GitHub
Actions construit l'APK :

1. Onglet **Actions** du dépôt → exécution « APK Collection de Messine »
2. Section **Artifacts** en bas → télécharger `collection-de-messine-apk`
3. Décompresser, transférer `collection-de-messine.apk` sur le téléphone
4. L'ouvrir ; Android demandera d'autoriser l'installation depuis cette source

L'APK est signé avec la clé de debug : suffisant pour une installation directe,
mais il ne pourra pas être publié sur le Play Store en l'état.

## Ce que fait l'application

- **Hors-ligne intégral.** Données, photos et polices sont embarquées. L'application
  ne déclare **aucune permission**, pas même l'accès au réseau.
- **Liens Drive.** Chaque fiche renvoie au dossier Drive de l'objet et à ses pièces
  (factures, notices, rapports), plus le fil Gmail d'origine. Ces liens sont confiés
  au système, qui les ouvre dans Google Drive ou le navigateur — déjà authentifiés.
  Aucun document n'est stocké dans l'application.
- **Recherche et filtres** par titre, maison de vente, catégorie, année.
- **Deux vues** : fiches groupées (année, emplacement, maison) et tableau
  récapitulatif avec totaux en euros.
- **Annotations personnelles** — emplacement dans l'appartement, valeur estimée,
  source de la valeur, notes. Elles restent **sur le téléphone** (`localStorage`)
  et ne sont pas renvoyées vers l'artifact.

## Structure

```
messine-android/
├── app/src/main/
│   ├── assets/
│   │   ├── app.html          l'inventaire (interface et logique)
│   │   ├── collection.json   les 46 pièces
│   │   ├── photos/           36 photos
│   │   └── fonts/            Newsreader + IBM Plex Sans (hors-ligne)
│   ├── java/fr/messine/collection/MainActivity.kt
│   └── res/                  thème clair/sombre, icône
└── build.gradle.kts
```

La coque native est volontairement mince : elle sert les assets sous une origine
`https` locale via `WebViewAssetLoader` — nécessaire pour que `fetch()` et
`localStorage` fonctionnent — intercepte le bouton retour pour fermer la fiche
ouverte, et redirige tout lien externe vers l'application compétente.

## Mettre à jour l'inventaire

Les données proviennent de l'artifact « Collection de Messine ». Pour les
rafraîchir, remplacer `assets/collection.json` (et les fichiers de `assets/photos/`,
nommés `<id>.jpg`), puis pousser : l'APK est reconstruit automatiquement.

## Construire en local

Nécessite le SDK Android (via Android Studio ou `sdkmanager`) :

```sh
cd messine-android
./gradlew assembleRelease
# app/build/outputs/apk/release/app-release.apk
```
