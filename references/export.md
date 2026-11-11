# Exporter et livrer

Seulement après un accord explicite (« c'est bon, exporte », « je valide »). « Continue » ou « ok » ne suffisent
pas : en cas de doute, demande.

## 0. La question de l'export

Après la validation de l'aperçu, demande par une question à choix ce qu'elle veut recevoir :
- **« La vidéo finie (MP4) »** (recommandé, le plus rapide) ;
- **« La vidéo finie et un projet modifiable »** pour CapCut, DaVinci Resolve, Premiere Pro ou Final Cut Pro (§ 4).

Retiens sa réponse dans `consignes.md` : la fois suivante, ne repose pas la question, propose la même chose.

## 1. Rendu

```powershell
cd <projet>/montage
npx hyperframes render --quality delivery --crf 14 --output ../exports/<nom>-v<N>-brut.mp4
```

- Machine modeste : ajouter `-w 1` et `$env:NODE_OPTIONS="--max-old-space-size=3072"`.
- Long (souvent 10 à 30 min) : le lancer en arrière-plan, journal dans un fichier, dire la durée estimée.
- Capture d'écran : `--crf 12` ou moins, pour un texte sans blocs de compression.

## 2. Son final

Le mixage sort du rendu parfois plus fort que la mesure. Toujours finir par une normalisation en deux passes,
image copiée telle quelle :

```powershell
ffmpeg -i brut.mp4 -af loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json -f null -
ffmpeg -i brut.mp4 -c:v copy -af "loudnorm=I=-16:TP=-1.5:LRA=11:measured_I=..:measured_TP=..:measured_LRA=..:measured_thresh=..:offset=..:linear=true,alimiter=limit=0.84" -c:a aac -b:a 256k -movflags +faststart final.mp4
```

Mesure le résultat (-16 LUFS, crête sous -1,5 dBTP), puis supprime le fichier brut.

**Contrôle de compatibilité, toujours, avant de livrer** : la vidéo doit se lire partout (Frame.io, YouTube, Instagram,
TikTok, CapCut, Premiere, téléphones).

```powershell
python <skill>/scripts/verifier_export.py final.mp4 --corriger
```

Il vérifie H.264, image 8 bits 4:2:0, cadence fixe, dimensions paires, son AAC 48 kHz stéréo et index en tête de
fichier, et fabrique une version corrigée si un point manque. Livre toujours le fichier qui passe ce contrôle.
Les fichiers ProRes du projet modifiable (§ 4) sont des fichiers de travail pour les logiciels de montage : ne les
présente jamais comme la vidéo à envoyer sur Frame.io ou sur les réseaux.

## 3. Livrer

- Le fichier final dans `exports/`, et une copie là où la personne le veut (par défaut le dossier
  Téléchargements). Note ce choix dans `~/cutora-studio.json` (`"livraison"`).
- Variantes si utiles : 9:16 et 16:9, version sans sous-titres, fichier `.srt`.
- `CREDITS.md` à jour (musiques CC BY à citer dans la description de la publication).
- Ménage : fichiers intermédiaires supprimés, versions gardées (sources, pas les rendus intermédiaires).
- Puis le **bilan de goût** ([apprentissage.md](apprentissage.md) § 5).

## 4. Le projet modifiable (CapCut, DaVinci, Premiere, Final Cut)

Pour retoucher le montage dans son logiciel, sans consommer son abonnement Claude. Le montage est livré **en couches** :
fond et caméra, animations sur fond transparent, sous-titres sur fond transparent, voix, musique, bruitages, chacun
sur sa piste et à sa place.

1. **Estime d'abord, et dis-le avant de lancer** :
   ```powershell
   python <skill>/scripts/export_projet.py <projet>/build/plan.json <projet>/exports/<nom>-projet-modifiable --estimer
   ```
   Le script donne le temps de calcul (d'après les coeurs et la mémoire de l'ordinateur, ou d'après la vitesse mesurée
   lors d'un export précédent) et la place sur le disque. Annonce-les simplement : « Ça va prendre environ 1 h 10 et
   2 Go. Je le lance en arrière-plan, tu peux faire autre chose. » Vérifie la place libre : s'il en manque, dis-le et
   propose la version légère ou un extrait.
2. **Lance en arrière-plan** (sans `--estimer`). Ajoute `--leger` pour des animations en WebM, 50 à 100 fois plus
   légères, utiles si la place manque ou si le logiciel refuse le ProRes. Machine modeste : `--workers 1`.
3. **Ce qui est livré** dans le dossier : `01-video-fond.mp4`, `02-graphismes.mov` et `03-sous-titres.mov`
   (ProRes 4444 transparent), `sous-titres.srt`, `audio/` (voix, musique, bruitages un par un et en une piste),
   `montage-premiere-davinci.xml`, `montage-finalcut.fcpxml`, `montage.otio`, `LISEZ-MOI.txt`. Et, si CapCut est
   installé, **un projet CapCut prêt** dans la liste de ses projets (« Cutora - <nom> »).
4. **Explique comment l'ouvrir**, selon son logiciel :
   - CapCut : fermer et rouvrir CapCut, puis ouvrir « Cutora - <nom> » dans la liste des projets ;
   - DaVinci Resolve : Fichier, Importer, Timeline, puis `montage.otio` ;
   - Premiere Pro : Fichier, Importer, puis `montage-premiere-davinci.xml` ;
   - Final Cut Pro : Fichier, Importer, XML, puis `montage-finalcut.fcpxml`.
   Ouvre le dossier pour elle. Le dossier doit rester entier : les projets pointent vers les fichiers qu'il contient.
5. **Dis honnêtement ce qui se modifie** : coupes, ordre, durée, chaque bloc d'animation (déplacer, supprimer,
   redimensionner), texte des sous-titres (fichier `.srt`), musique, bruitages, volumes, étalonnage. Le texte et le
   mouvement **à l'intérieur** d'une animation ne se modifient pas : c'est une vidéo. Pour changer un titre animé,
   masquer ce bloc et ajouter son propre titre, ou demander la modification ici.

Le script retient la vraie vitesse de l'ordinateur dans `~/cutora-studio.json` : les estimations suivantes sont plus
justes.
