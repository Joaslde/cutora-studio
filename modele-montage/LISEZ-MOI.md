# Modèle de montage de départ

Le générateur qui transforme **le style de la personne** (`choix.json` de la page de choix) et **un plan de montage**
(`plan.json`) en un projet HyperFrames complet, vérifié, prêt à montrer. Il garantit que la vidéo ressemble à ce que la
personne a vu et choisi sur la page : mêmes polices, mêmes couleurs, même façon de faire apparaître le texte, mêmes
sous-titres, mêmes transitions, même vocabulaire de motion design.

```powershell
cd <projet>/build
python <skill>/modele-montage/build.py plan.json
cd ../montage ; npx hyperframes check
```

Fichiers : `build.py` (le générateur), `kit.css` et `kit.js` (le vocabulaire visuel et les animations, les mêmes que la
page de choix), `plan-exemple.json` (un plan complet à copier).

## Le plan

| Clé | Rôle |
|---|---|
| `style` | Chemin du `choix.json` du style choisi |
| `projet` | Dossier HyperFrames à écrire (créé par `npx hyperframes init` avant) |
| `largeur`, `hauteur`, `duree` | 1080 x 1920 (vertical) ou 1920 x 1080 ; durée totale en secondes |
| `voix` | Voix traitée (-16 LUFS), dans `assets/voice/` |
| `mots` | Mots de la voix avec leurs instants **sur la timeline coupée** (`text`/`start`/`end` ou `texte`/`debut`/`fin`) : sous-titres |
| `camera` | Le rush dérushé et traité : `src`, `ratio` (largeur / hauteur du rush), `cadrage` (point du rush à garder au centre en plein visage, de 0 à 1), `debut_media` facultatif |
| `musique` | `src`, `volume` (0,15 à 0,25), `fondu` de fin |
| `scenes` | Le découpage (voir ci-dessous) |
| `sfx` | Bruitages : `src`, `t` (instant), `volume`, `duree` |

Chaque scène : `debut`, `fin`, `page`, et selon la page `titre`, `motion`, `media`.

| `page` | Ce qu'on voit |
|---|---|
| `partage` | Motion design en haut, caméra en carte arrondie en bas (à droite en 16:9), sous-titres entre les deux |
| `visage` | Caméra plein cadre, sous-titres au niveau du torse ; `titre` et `motion` facultatifs |
| `motion` | Motion design plein cadre, caméra cachée |
| `media` | Un B-roll (`media`) plein cadre, avec voile de lisibilité |

`titre` : `faible` (petits mots, police normale), `fort` (police forte), `cle` (mot mis en valeur selon le style), `t`
(instant local où il commence). Mets le titre sur le mot qui l'annonce.

`motion` : `type` parmi `cartes`, `telephone`, `orbite`, `fleches`, `chiffres`, `etiquettes`, `saisie`, `liste`, `media` ;
`t` (instant local) ; `textes` ; `medias` (images ou vidéos dans `assets/`) ; `chiffre` (pour `chiffres`) ;
`mots_t` (instant local de chaque élément, pour les caler un par un sur les mots prononcés).

Le passage entre deux pages de caméra (carte et plein visage) se fait en 0,3 s, automatiquement.

## Aller plus loin

Le générateur couvre l'essentiel. Pour une scène unique (un profil Instagram redessiné, une interface précise, un
effet de la référence), écris sa composition à la main dans `compositions/` à partir de celle générée, avec le même
kit, et note-le dans le plan (`"sur_mesure": true`) pour ne pas l'écraser : le générateur saute les scènes marquées
ainsi.
