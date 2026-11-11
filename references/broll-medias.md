# B-roll, photos, logos, icônes

Ordre de préférence : **les images de la personne** (les plus crédibles), puis des **médias libres** trouvés en
ligne, puis ce qu'on **dessine** (motion design). Jamais d'images d'une vidéo de référence, jamais de visage généré
présenté comme une vraie personne, jamais d'emoji.

Chaque média téléchargé est noté dans `<projet>/CREDITS.md` : source, lien, licence, auteur si demandé.

## 1. La bibliothèque de la personne

Si la personne a ses propres plans (bureau, ville, sport, écran, produit), on les range une fois pour toutes :

1. Dossier `<atelier>/profils/<nom>/broll/` (ou son dossier à elle, qu'on ne déplace pas).
2. Pour chaque fichier : durée, orientation, définition, date (`ffprobe`), et une planche de 6 images
   (`ffmpeg -i clip -vf "fps=6/<durée>,scale=360:-2,tile=3x2" -frames:v 1 planches/<id>.jpg`).
3. Regarde chaque planche et écris une ligne par clip dans `broll/bibliotheque.md` :
   `id | durée | orientation | ce qu'on voit | ambiance | mots clés | la personne est à l'image (oui/non)`.
   Avec des sous-agents, confie les planches par lots de 5 à des sous-agents rapides et peu coûteux.
4. Au montage, une simple recherche dans `bibliotheque.md` trouve « moi au bureau la nuit » sans rouvrir une vidéo.

## 2. Vidéos libres en ligne : chercher par contexte, choisir en regardant

Un B-roll hors sujet est pire que pas de B-roll. Les erreurs à ne jamais refaire : prendre les premiers résultats sans
les regarder, chercher un mot isolé (« yawning » renvoie des lions et des hippopotames), remettre le même plan, ou en
mettre si peu que la vidéo reste plate.

| Source | Licence | Accès |
|---|---|---|
| **Mixkit** | Gratuite, usage commercial, sans crédit obligatoire | Sans compte : `scripts/broll.py` |
| **Pexels** | Gratuite, crédit apprécié | Clé gratuite (pexels.com/api, 2 minutes) dans `~/cutora-studio.json` (`"pexels_cle"`) : `scripts/broll.py` l'utilise. Propose-la à la personne la première fois : elle double le choix |
| Wikimedia Commons, Openverse | Variable, CC0 ou CC BY | Pour des images ; créditer si CC BY |

### 2.1 Le contexte de la vidéo d'abord

Avant toute recherche, écris pour toi une **fiche contexte** en 4 lignes, tirée de la transcription et du profil :
- **le thème** (travail et fatigue, argent, sport, IA, famille...) ;
- **les personnes** qu'on doit voir : âge, style, cohérentes avec la personne qui parle et son public ;
- **les lieux** (bureau, ville, maison, extérieur) ;
- **l'ambiance d'image** (lumière chaude ou froide, jour ou nuit, sobre ou énergique).

Tous les B-rolls d'une vidéo appartiennent au **même univers** : mêmes types de personnes, de lieux, de lumière. Une
vidéo sur l'épuisement au travail montre des bureaux, des écrans, des visages fatigués, pas une plage puis un tigre.

### 2.2 Les moments

Repère dans la transcription les phrases qui gagnent à être **montrées** : une action (« je travaille la nuit »), un
lieu, un objet, une émotion forte, un chiffre concret, un exemple. Regroupe-les **par thème** (tous les moments
« fatigue », tous les moments « argent ») : une recherche par thème donne une série cohérente.

Densité, selon le format et les consignes de la personne :

| Format | B-roll |
|---|---|
| F3 montage complet | Un plan toutes les 4 à 8 s, c'est la matière principale |
| F1 et F2 face caméra | Un plan de 1 à 3 s sur chaque moment fort, environ toutes les 10 à 20 s |
| F4 motion design | Dans des cartes ou des téléphones, sur les exemples concrets |
| F5 capture d'écran | Rarement : seulement pour une illustration hors écran |

La densité (« peu », « régulier », « beaucoup ») se demande **une fois**, puis se note dans `consignes.md`.

### 2.3 Les requêtes

Pour chaque thème, 3 à 5 requêtes en **anglais**, chacune construite comme **qui + quoi + où** et tirée de la fiche
contexte : « tired employee at desk at night », « exhausted woman office laptop », « man rubbing eyes computer ». Jamais
un mot seul. Varie les angles (gros plan, plan large, mains, visage) pour avoir de quoi monter une série.

```powershell
python <skill>/scripts/broll.py chercher <projet>/travail/broll/fatigue "tired employee at desk at night" "exhausted woman office laptop" "man rubbing eyes computer" --orientation landscape --n 12
```

Le script rassemble Mixkit et Pexels, écarte les plans déjà utilisés et fabrique des **planches numérotées** avec
le titre de chaque plan.

### 2.4 Choisir en regardant (obligatoire)

Regarde **chaque planche**. Un plan est retenu seulement s'il coche tout :
- il montre **exactement** l'idée de la phrase, dans le contexte de la vidéo ;
- les personnes sont cohérentes avec la personne qui parle et son public ;
- même univers et même lumière que les autres plans retenus ;
- cadrage compatible avec le format (vertical ou horizontal, sujet au centre si on recadre) ;
- pas d'animal, de lieu ou d'époque hors sujet, pas de texte incrusté ni de logo gênant.

Rien ne convient : reformule (autres mots, autre angle) jusqu'à 2 fois. Toujours rien : remplace par un élément de
motion design, jamais par un plan faible.

```powershell
python <skill>/scripts/broll.py prendre <projet>/travail/broll/fatigue <projet>/montage 1 10 11
```

Les plans choisis arrivent en HD dans `montage/assets/broll/`, sont crédités dans `CREDITS.md` et notés dans
`deja-utilises.json` : **jamais deux fois le même plan** dans une vidéo. Pour éviter les répétitions d'une vidéo à
l'autre, garde aussi la liste dans `profils/<personne>/broll-deja-utilises.json`.

### 2.5 Montrer avant de monter

Au niveau d'autonomie 1 et 2, montre la sélection avant de l'intégrer : une planche des plans retenus, avec la phrase
sur laquelle chacun tombera. « Voici les B-rolls que je propose. Je garde tout, ou j'en change un ? » Ses refus vont
dans le journal (« pas de plans trop corporate », « des personnes plus jeunes ») : la recherche suivante en tient compte.

### 2.6 Poser le B-roll

- Sur le mot qui le nomme, 0,5 à 3 s, en coupe franche ou dans une carte selon le style.
- Recadre et étalonne-le pour qu'il colle au reste ([image-son.md](image-son.md)).
- Faux A-roll (format sans visage) : une personne libre qui parle face caméra, dans un téléphone ou une carte, jamais
  présentée comme une vraie personne citée.
- Supprime les candidats non retenus à la fin (`travail/broll/*/vignettes`).

## 3. Logos et interfaces

- **Vrais logos** des marques citées, jamais une lettre dans un cercle ni une imitation. Sources : le kit presse ou
  le site officiel de la marque, **Simple Icons** (`https://simpleicons.org`, SVG de marques en CC0, la marque reste
  propriété de son détenteur), Wikimedia Commons. Logo introuvable avec certitude : demande le fichier.
- **Interfaces** (une appli, un site, un profil Instagram) : redessinées à l'identique en HTML (mêmes polices, mêmes
  espacements), avec les vraies données que la personne donne (ses chiffres, sa bio, sa photo). Pour un site :
  `npx hyperframes capture <url>` donne une capture réelle.

## 4. Icônes et illustrations

- Icônes au trait : **Lucide** (ISC), **Tabler Icons** (MIT), **Phosphor** (MIT). SVG recolorés aux couleurs du
  profil. Copiés dans `montage/assets/icons/`.
- Illustrations et objets 3D : dessinés en SVG ou en CSS, ou photos détourées
  (`npx hyperframes remove-background` sur une image).
- **Aucun emoji**, même en 3D : ils font amateur. Une vraie photo dans un rond ou une carte vaut toujours mieux.

## 5. Photos de la personne et de son monde

Demande tôt ses photos utiles (photo de profil, logo, produit, équipe, lieux) et range-les dans
`profils/<nom>/charte/`. Elles servent dans toutes les vidéos suivantes.
