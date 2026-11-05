# Image et son : améliorer la matière

Objectif image : ressembler le plus possible à une vidéo tournée avec une bonne caméra, rendu cinéma **léger**,
jamais un filtre visible. Objectif son : une voix chaude, présente, sans souffle, sans « s » qui sifflent.

Toujours : **mesurer d'abord**, proposer **2 ou 3 variantes** sur quelques images ou un extrait, montrer
**avant et après côte à côte**, laisser choisir, puis traiter tout le rush dans un **nouveau fichier**. Le choix
retenu va dans le profil (chaîne ffmpeg exacte), pour être réappliqué sans redemander.

## 1. Mesurer un rush

- `ffprobe` : définition, images par seconde (variable ?), débit, codec.
- Une image toutes les 10 s en pleine résolution, regardée à 100 % : exposition du visage, couleur de la peau,
  dominante (verte, jaune, bleue), bruit dans les zones sombres, netteté.
- Histogramme rapide : `ffmpeg -i rush.mp4 -vf "select=eq(n\,100),histogram" -frames:v 1 histo.png`.

## 2. Caméra, webcam, téléphone (une personne filmée)

Ordre de traitement :

1. **Débruitage** dosé, seulement s'il y a du bruit : `hqdn3d=1.5:1.5:0:0` (très léger) ; plus fort :
   `nlmeans=s=2` (lent). Trop de débruitage = visage cireux.
2. **Exposition et contraste** : `curves=all='0/0 0.22/0.27 0.55/0.60 1/0.97'` (tons moyens remontés, blancs
   protégés). Visage plus sombre que le fond : remonter les moyens, pas tout.
3. **Balance des blancs et peau** : `colorbalance` par petites touches (0,01 à 0,04). Corriger une dominante verte :
   `rs=0.02:gs=-0.02:rm=0.04:gm=-0.03`. Ne jamais retirer le rouge ou l'orange d'une peau.
4. **Saturation** : `eq=saturation=1.04` à `1.10`.
5. **Look cinéma léger** (si le profil le veut) : une LUT `.cube` (`lut3d=file.cube`, avec un mélange à 30 à 60 %),
   ou ombres légèrement froides et peau chaude, vignettage très doux (`vignette=PI/6`).
6. **Agrandissement** vers la définition de sortie : `scale=W:H:flags=lanczos`, puis netteté fine `cas=0.4`
   (ou `unsharp=5:5:0.4`).
7. **Grain** très léger à la toute fin seulement si le profil le demande (`noise=alls=4:allf=t`).
8. **Stabilisation** si ça tremble : `vidstabdetect` puis `vidstabtransform=smoothing=20` (deux passes).

Exemple validé (webcam 720p, mur blanc, légère dominante verte) :
`hqdn3d=1.5:1.5:0:0,colorbalance=rs=0.02:gs=-0.02:rm=0.04:gm=-0.03:bm=-0.01,curves=all='0/0 0.22/0.27 0.55/0.60 1/0.97',eq=saturation=1.06`
puis `scale=1080:1920:flags=lanczos,cas=0.45` après recadrage.

- **Harmoniser** plusieurs rushs (deux caméras, deux jours) : régler le plus important, puis corriger les autres
  jusqu'à ce que la peau ait la même couleur sur une planche côte à côte.
- Recadrer serré un rush 720p en 9:16 l'agrandit 2,5 fois : c'est la limite de netteté. Conseiller à la personne
  de filmer en 1080p ou en 4K, lumière face à elle.
- Dans HyperFrames, l'étalonnage d'un média peut aussi passer par `npx hyperframes media-treatment` (skill
  `media-use`), jamais par des filtres CSS.

## 3. Capture d'écran (PC)

- **Pas** de débruitage, de grain ni de LUT cinéma : le texte devient baveux et les couleurs fausses.
- Agrandissement net : `scale=3840:2160:flags=lanczos,cas=0.5` (ou `spline`) pour un texte bien découpé.
- Export à débit élevé (`-crf 14` ou moins) : sinon des blocs de compression apparaissent sur le texte.
- La qualité vient surtout de l'enregistrement : conseiller 1440p ou 4K, débit élevé (OBS, qualité
  « Indistinguable »), interface de Windows agrandie (125 à 150 %) pour un texte lisible sur téléphone.

## 4. Le son de la voix

1. **Mesurer** : loudness et crête (`ffmpeg -i voix.wav -af ebur128=peak=true -f null -`), niveau des silences
   (5e et 10e centiles du niveau RMS), où est le bruit (spectrogramme d'un silence : ronflement grave,
   ventilateur, souffle aigu).
2. **Chaîne de base** (validée) :
   `highpass=f=80,equalizer=f=200:t=q:w=1:g=1.5,equalizer=f=3500:t=q:w=1.2:g=2,deesser=i=0.4:m=0.5:f=0.5,acompressor=threshold=-24dB:ratio=2.5:attack=10:release=150:makeup=2`
3. **Débruitage** devant la base, selon la mesure :
   - léger : `afftdn=nr=6:nf=-55` ;
   - moyen (validé sur webcam) : `adeclick,afftdn=nr=12:nf=-50` ;
   - fort : `arnndn` avec un modèle RNNoise `.rnnn` (quelques centaines de Ko, à demander avant de le récupérer).
   Une voix « sous l'eau » est pire qu'un léger souffle : comparer en écoutant (par la personne).
4. **Clics de clavier et de souris** trop forts (capture d'écran) : `adeclick`, ou baisser les passages repérés
   sur l'onde.
5. **Niveau final** : `loudnorm=I=-16:TP=-1.5:LRA=11` en **deux passes** (`linear=true`), puis
   `alimiter=limit=0.84`. Mesurer : -16 LUFS, crête sous -1,5 dBTP.
6. Faire écouter un extrait de 10 s avant et après (deux fichiers), dans la variante choisie.

La voix traitée devient un `<audio>` séparé dans le montage ; la vidéo de la caméra est `muted`.
