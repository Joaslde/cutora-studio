# Pièges déjà rencontrés (ne pas les redécouvrir)

## Windows et outils

- Après `winget install`, la commande n'est pas reconnue dans le terminal déjà ouvert : chemin complet ou relancer.
- Python : `PYTHONUTF8=1` pour les accents. Les chemins `/tmp` ne marchent pas pour Python sous Windows.
- ffmpeg récent : `-/filter_complex fichier.txt` remplace l'ancien `-filter_complex_script`.
- `npx skills add` peut échouer (« Could not determine Node.js install directory ») : `git clone` puis copie.
- Mémoire faible : rendu en `-w 1`, `NODE_OPTIONS=--max-old-space-size=3072`, fermer les applications lourdes.

## Transcription

- Parakeet bascule en anglais sur de l'audio français déjà coupé, et parfois sur des rushs entiers : transcrire le
  rush original, et passer à faster-whisper si besoin.
- Les noms propres sont écorchés : un `initial_prompt` avec les noms, puis relire.
- Horodatages décalés jusqu'à 1 s : couper sur l'onde, pas sur le texte.

## HyperFrames

- Vidéo non timée = `media_missing_data_start` : la vidéo vit dans sa sous-composition avec `data-start` /
  `data-duration`.
- L'étalonnage par `media-treatment` crée un calque au-dessus des compositions de niveau bas : hôtes graphiques à
  `z-index: 10`, sous-titres à `20`.
- Plusieurs clips de voix séparés coupent la voix dans l'aperçu : fusionner en une seule piste.
- Deux ou trois vidéos décodées en même temps ralentissent ou figent le rendu : précalculer la caméra en une vidéo.
- Un zoom avec retour en `back.out` repasse sous 1 et laisse un liseré noir : `power2.out`.
- Mot actif agrandi dans les sous-titres : il mange l'espace, mettre `margin: 0 0.05em` sur chaque mot.
- Les fins de tween qui dépassent la durée de la scène : raccourcir, sinon `check` signale un dépassement.

## Détourage et caméra

- Rush à cadence variable (webcam, téléphone) : le masque de détourage dérive de plusieurs images pendant les
  gestes rapides. Ramener le rush à 30 images/s constants, puis réaligner le masque image par image
  (associer chaque image du masque à l'image du rush la plus ressemblante, puis réécrire le masque).
- Masque à moitié transparent = tête fantôme : durcir le masque (seuil) puis léger flou (0,9 à 1,1 px).
- Liseré clair autour des cheveux : resserrer le masque de 2 px et assombrir légèrement la frange.
- Ligne sombre d'un pixel à la frontière tête / carte : faire déborder la tête de quelques pixels dans la carte.
- Le détourage est très lent sur CPU (plusieurs heures pour 2 minutes) : le lancer dès le dérush.

## Sources en ligne

- Openverse limite les requêtes (429 pour la journée si on insiste) et tombe parfois (504) : Mixkit en secours.
- yt-dlp échoue sur Instagram sans connexion : demander le fichier. Sur YouTube, le mettre à jour en cas d'erreur.

## Échanges avec l'utilisateur

- « Continue » ne veut pas dire « exporte ».
- Une page HTML de comparaison avant/après est un outil de choix, pas le montage : le dire clairement.
- Une nappe de suspense peut être ressentie comme de l'horreur : pas de stridences, pas de dissonances.
