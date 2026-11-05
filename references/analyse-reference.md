# Analyser une vidéo de référence (et la reproduire au plus près)

La personne donne une vidéo qu'elle aime. On la **mesure** au lieu de l'estimer à l'œil, plan par plan, puis on
la reproduit avec le contenu de la personne : même grammaire, mêmes proportions, même son, mêmes rythmes. Jamais
les images, les textes, les logos ou les sons de la référence.

Dossier de travail : `<atelier>/profils/<nom>/styles/<style>/references/<ref>/` (appelé `W`). Les fichiers lourds (la vidéo, le
son) sont supprimés à la fin ; on garde le rapport, les planches et quelques images clés.

## 1. Récupérer la vidéo

- Fichier local : l'utiliser tel quel.
- YouTube : `yt-dlp -f "bv*[height<=1920]+ba/b" --merge-output-format mp4 -o "W/ref.%(ext)s" "<lien>"`.
- Instagram, TikTok : essayer `yt-dlp` ; s'il est bloqué (connexion demandée), demander à la personne
  d'enregistrer la vidéo et de la déposer dans `W`.
- Idéal : 2 ou 3 vidéos du même créateur et du même format. Une seule vidéo peut être l'exception.
- yt-dlp échoue sur un lien qui marche dans le navigateur : le mettre à jour (`python -m pip install -U yt-dlp`).

## 2. Mesurer (les trois passes sont obligatoires)

```powershell
python <skill>/scripts/analyse_reference.py W/ref.mp4 W
```

Le script donne : format, durée, images par seconde, coupes détectées (dans `mesures.json`), planches de
32 images à 2 images par seconde (`planche_<N>_<a>s-<b>s.jpg`, N à partir de 0 : la case i montre la seconde
16N + i/2), spectrogramme (`spectrogramme.png`), loudness, et `audio16k.wav` pour la transcription.

### Passe 1 : l'image

Lis **toutes** les planches et note :

- **mises en page** et leur part du temps (plein visage, écran partagé, carte, plein motion design, B-roll) ;
- **où est chaque chose**, en pixels : hauteur du titre, ligne de sous-titres, cadre caméra (x, y, largeur, rayon
  des coins). Extrais les images clés en pleine résolution et mesure au pixel :
  `ffmpeg -v error -ss <s> -i W/ref.mp4 -frames:v 1 W/hd_<s>.png` ;
- **typographie** : famille (grotesque grasse, serif italique, condensée, ronde), graisse, casse, taille en px,
  approche, couleurs, mot mis en valeur et comment ;
- **apparition du texte** : mot par mot ou bloc, flou vers net, glissement, durée en images ;
- **motion design** : le vocabulaire qui revient (cartes, téléphone, icônes, flèches, étiquettes, chiffres),
  quand il arrive (sur le mot qui le nomme ?), comment il sort ;
- **mouvements** : poussée lente, zoom, flou de mouvement, ease (rapide qui se pose, élastique) ;
- **transitions** : coupe franche, zoom, glissement, ou rien ;
- **image** : étalonnage (lumineux et plat, contrasté et sombre), grain, vignettage ;
- **accroche** (2 premières secondes) et **appel à l'action** (3 dernières).

Pour les transitions rapides, une bande à 12 images par seconde autour du moment :
`ffmpeg -v error -ss <s-0,5> -t 1 -i W/ref.mp4 -vf "fps=12,scale=270:-2,tile=12x1" -frames:v 1 W/trans_<s>.jpg`.

### Passe 2 : le rythme

- Secondes par plan = durée / (nombre de coupes + 1). Note aussi les bascules de mise en page (pas seulement les
  coupes).
- Taille du visage sur 10 cases (part de la hauteur de l'image) et ses sauts : un saut à une coupe = changement de
  cadrage ; un saut dans un plan = zoom ; une croissance lente = poussée. Ces chiffres sont des **plafonds** pour
  notre copie.
- Transcris la référence (fiche méthode § 2) pour savoir **sur quels mots** tombent les bascules et les animations.

### Passe 3 : le son

Lis `spectrogramme.png` à côté des coupes de `mesures.json` (x = largeur × t / durée) :

- trait vertical fin en haut = clic ; large et bas = impact grave ; traînée qui monte = whoosh ou montée ;
  lignes horizontales continues = nappe musicale ; trou dans la nappe = la musique se coupe ;
- zoom sur un moment : `ffmpeg -v error -ss <s-1> -t 2 -i W/ref.mp4 -lavfi "showspectrumpic=s=1000x500:legend=0:scale=log:stop=11000" W/son_<s>.png` ;
- un son répété (tics d'une flèche, frappe) : compter les coups et mesurer l'espacement, pour le recréer par
  synthèse ([bruitages-musique.md](bruitages-musique.md)) ;
- niveau de la musique sous la voix (estimé sur le spectrogramme), loudness intégrée, crête.

**Avec des sous-agents** (Claude Code) : fais les planches et les coupes toi-même, puis confie image, rythme et
son à trois sous-agents en parallèle, chacun avec les chemins absolus et un fichier de notes à écrire (chiffres et
instants uniquement). Tu juges le style sur les planches pendant qu'ils mesurent.

## 3. Écrire le rapport

`W/ANALYSE.md`, d'après `<skill>/profil-modele/ANALYSE-REFERENCE-modele.md` : fiche technique, principe de mise en
page, charte, vocabulaire de motion design, mouvements, découpage plan par plan, son, ce que ça implique pour les
rushs de la personne, et ce qu'on ne reprend pas (et pourquoi). Chaque ligne donne une valeur et la mesure qui la
soutient.

Puis reporte l'essentiel dans `styles/<style>/style.md`, source `(référence <ref>, mesuré)`.

## 4. Reproduire, puis comparer AVANT de montrer

1. Monte un passage de 10 à 20 s avec le contenu de la personne, dans le format de la référence.
2. Planche comparative, référence en haut, copie en bas, aux mêmes instants relatifs :
   `ffmpeg -v error -i W/ref.mp4 -i copie.mp4 -filter_complex "[0:v]fps=1,scale=216:384,trim=end_frame=12,tile=12x1[a];[1:v]fps=1,scale=216:384,trim=end_frame=12,tile=12x1[b];[a][b]vstack" -frames:v 1 W/compare.jpg`
   (sans rendu : `npx hyperframes snapshot --at <t1>,<t2>...` sur la copie).
3. Case par case : taille et graisse du texte, taille des éléments (ils remplissent l'espace comme dans
   l'original, jamais de petits éléments perdus dans le vide), position des sous-titres, cadrage, étalonnage,
   transitions, nombre de zooms. Spectrogramme de la copie : les sons tombent sur les mêmes événements.
4. Corrige chaque écart. Un sous-agent « œil neuf » à qui tu donnes la planche comparative et cette liste repère
   ce que tu ne vois plus.

## 5. Ce qui ne se copie pas (leçons de copies refusées)

- Les clics, tics et whooshes sur **chaque** élément qui entre : insupportables recopiés tels quels. Garder les
  sons sur les vrais moments (bascule, révélation, appel à l'action), sauf si la personne veut exactement la
  densité de l'original.
- Une montée (riser) avant un moment : souvent ressentie comme du bruit. Préférer l'impact **sur** le moment.
- L'étalonnage de la référence appliqué à une autre peau : visage gris ou vert. Ne jamais retirer le rouge ou
  l'orange d'une peau ; éclaircir, monter un peu les tons moyens, saturation +5 %.
- Les vidéos générées par IA de la référence : remplacées par les vraies images de la personne ou du B-roll libre.
- Copier « à l'identique » veut dire la même grammaire, les mêmes proportions, le même rythme et le même son.
  Les couleurs et les polices peuvent devenir celles de la personne : c'est une demande normale.
