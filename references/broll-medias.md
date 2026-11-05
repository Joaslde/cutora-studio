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

## 2. Vidéos libres en ligne (sans compte, gratuit)

| Source | Licence | Comment |
|---|---|---|
| **Mixkit** (vidéos) | Gratuite, usage commercial, sans crédit, pas de revente des fichiers seuls | Page `https://mixkit.co/free-stock-video/<mot-anglais>/` ; fichier `https://assets.mixkit.co/videos/<id>/<id>-720.mp4` (ou `-1080.mp4`) |
| **Pexels** (vidéos et photos) | Gratuite, sans crédit obligatoire | Site `https://www.pexels.com/fr-fr/chercher/videos/<mots>/` ; l'API demande une clé gratuite (à demander à la personne) |
| **Pixabay** | Gratuite, sans crédit | Clé API gratuite nécessaire pour l'automatiser |
| **Wikimedia Commons** | Variable (CC0, CC BY, CC BY-SA) | Lire la licence de chaque fichier ; créditer si CC BY |
| **Openverse** (images) | CC0 ou CC BY | `https://api.openverse.org/v1/images/?q=<mots>&license=cc0` |

Méthode :

- Cherche en **anglais**, avec 1 ou 2 mots concrets (« laptop night », « city crowd », « money counting »).
- Télécharge 3 à 5 candidats dans `work/broll-candidats/`, fais une planche de chaque, garde le meilleur.
  Critères : même ambiance de lumière que le reste, pas de texte incrusté, pas de logo de marque gênant, un plan
  qui **montre exactement le mot** prononcé.
- Un faux A-roll (quelqu'un qui parle, pour un format sans visage) : une vidéo libre d'une personne face caméra,
  dans un téléphone ou une carte, jamais présentée comme une vraie personne citée.
- Recadre et étalonne le B-roll pour qu'il colle au reste ([image-son.md](image-son.md)).
- Supprime les candidats non retenus à la fin.

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
