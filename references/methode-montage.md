# Monter une vidéo : la méthode

Valable pour tous les formats. Relis le profil avant de commencer, puis la fiche de son format
([formats.md](formats.md)).

## 1. Le projet

```text
<atelier>/projets/<profil>/<projet>/
├── references/   a-roll/   b-roll/   voix/      ce que la personne dépose (jamais modifié)
├── work/         fichiers de travail : audio 16 kHz, transcriptions, EDL, rush traité
├── build/        le générateur (build.py, head.html, tpl/) : le montage s'écrit ici
├── montage/      le projet HyperFrames généré (npx hyperframes init montage)
├── montage-v1/   les versions précédentes, conservées
└── exports/      les vidéos finies
```

Mesure chaque fichier déposé (`ffprobe -v error -show_entries format=duration:stream=codec_name,width,height,r_frame_rate -of json`)
et regarde une planche de chaque rush avant de décider quoi que ce soit.

## 2. Dérush et transcription

1. Audio 16 kHz mono : `ffmpeg -i rush.mp4 -vn -ac 1 -ar 16000 -c:a pcm_s16le work/rush_16k.wav`.
2. Transcris le **rush original** (jamais l'audio déjà coupé) :
   - Parakeet : `npx hyperframes transcribe work/rush_16k.wav --engine parakeet --language fr --json` ;
   - s'il bascule en anglais ou écorche trop de mots : `python <skill>/scripts/transcrire.py work/rush_16k.wav
     work/rush_mots.json small` (ou `medium`), avec dans le script un `initial_prompt` qui contient les noms
     propres de la personne (son nom, ses marques, ses outils).
3. Lis le texte. Repère les ratés, les phrases recommencées (garder la **dernière** bonne prise), les « euh », les
   blancs. Relis les noms propres et signale les phrases incertaines.
4. Coupe sur **l'onde sonore**, jamais sur les horodatages de la transcription (décalés jusqu'à 1 s par endroits) :
   marge de 0,08 s avant la reprise de parole et 0,16 s après la fin de phrase. Jamais au ras d'un mot.
   Vérifie chaque raccord (aucun mot coupé) avant de continuer.
5. Écris l'EDL (`work/edl.json` : segments gardés) et reporte les mots sur la timeline coupée
   (`work/mots_coupes.json`). Toutes les animations se calent sur ces temps.
6. Le rush webcam ou téléphone a souvent une **cadence variable** : ramène-le à 30 images/s constants
   (`-vf fps=30`) dès le dérush, sinon les masques et les calques dérivent.

## 3. Le générateur (la façon de travailler qui donne les meilleurs résultats)

On n'écrit pas le HTML du montage à la main scène par scène. On part du **modèle de montage** du skill
([../modele-montage/LISEZ-MOI.md](../modele-montage/LISEZ-MOI.md)) :

1. `npx hyperframes init montage` dans le projet, puis copie les médias dans `montage/assets/` (rush traité,
   voix, musique, B-rolls, sons).
2. Écris `build/plan.json` d'après `<skill>/modele-montage/plan-exemple.json` : chemin du `choix.json` du style,
   mots de la voix, caméra, et le **découpage en scènes** (mise en page, titre, motion design, instants calés sur les
   mots prononcés). C'est là que se joue la qualité : un changement visuel au rythme du style, chaque élément sur le
   mot qui le nomme, le vocabulaire de motion design préféré de la personne.
3. `python <skill>/modele-montage/build.py build/plan.json` écrit tout le projet HyperFrames dans le style exact de
   la personne (polices téléchargées, couleurs, sous-titres, animations, transitions, caméra en carte ou plein
   cadre). Une correction = modifier le plan, relancer, en une seconde.
4. Les scènes particulières (une interface redessinée, un effet de la référence) : édite leur composition à la main
   en partant de celle générée, et marque la scène `"sur_mesure": true` dans le plan pour ne pas l'écraser.

Ce que chaque choix de la page devient dans la vidéo : [correspondance.md](correspondance.md).


Dans chaque scène, les temps sont **locaux** (`w(i)` = instant du mot i dans la scène). Les fonctions communes
(entrée en pop, sortie, trait qui se dessine, mise en avant) sont écrites une fois dans le préambule JS commun.

## 4. Construire dans HyperFrames

Lis le skill `hyperframes` (contrat de rendu) avant d'écrire. L'essentiel :

- une sous-composition par scène dans `compositions/`, montée par `index.html` avec `data-start` / `data-duration` ;
- chaque élément temporisé a `class="clip"`, chaque composition une timeline GSAP en pause enregistrée dans
  `window.__timelines` ;
- la vidéo de la caméra est `muted`, la voix traitée est un `<audio>` séparé ; musique et bruitages aussi ;
- pas d'aléatoire non initialisé, pas de minuterie : tout dépend du temps de la timeline ;
- polices : celles intégrées à HyperFrames, sinon un `@font-face` vers `assets/fonts/` ;
- avant de dessiner un effet nommé (grain, glitch, graphique, transition), cherche dans le catalogue
  (`hyperframes-registry`).

**La caméra précalculée** : quand la caméra change de mise en page (plein visage, carte, tête qui dépasse),
précalcule-la avec ffmpeg dans **une seule** vidéo (VP9 avec transparence si besoin) plutôt que de décoder deux ou
trois vidéos dans la page : le rendu reste rapide et stable.

## 5. Le motion design : ce qui fait « pro »

- Chaque animation arrive **sur le mot qui la nomme**, à l'image près.
- Entrée signature : flou vers net, légère montée d'échelle (0,85 vers 1), 6 à 8 images, ease rapide qui se pose.
- **Grand et affirmé** : un élément de motion design remplit sa zone. Mesure la référence au pixel ; à défaut, un
  titre fait au moins 70 px de haut en 1080 de large, une icône ou une tuile au moins 200 px.
- Une poussée lente continue (échelle 1 vers 1,05) sur l'élément principal pendant qu'on parle : rien n'est figé.
- Vraies choses : vrais logos, vraies interfaces redessinées à l'identique, vraies photos. Aucun emoji.
- Sous-titres jamais sur la bouche ; un titre qui dit les mêmes mots remplace le sous-titre.
- La fin : l'appel à l'action, lisible au moins 2 secondes.

## 6. Contrôler puis montrer

1. `npx hyperframes check` (zéro erreur).
2. `npx hyperframes snapshot --at <t1>,<t2>,...` aux moments clés (une image par scène, plus chaque transition) et
   **regarde chaque image** : proportions, lisibilité, débordements, liserés, acquis du profil.
3. Mixage mesuré sans rendu : `python <skill>/scripts/mixcheck.py montage/index.html` (-16 LUFS visés, crête sous
   -1,5 dBTP).
4. Checklist de [qualite.md](qualite.md).
5. `npx hyperframes preview` (ou ouvre l'aperçu déjà lancé) et donne le lien, avec ce qu'il faut regarder.

Machine modeste (8 Go de mémoire ou moins) : les rendus avec `-w 1` et
`NODE_OPTIONS=--max-old-space-size=3072`.
