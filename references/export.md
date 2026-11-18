# Exporter et livrer

Seulement après un accord explicite (« c'est bon, exporte », « je valide »). « Continue » ou « ok » ne suffisent
pas : en cas de doute, demande.

## 0. La question de l'export

Après la validation de l'aperçu, demande par une question à choix ce qu'elle veut recevoir :
- **« La vidéo finie (MP4) »** (recommandé, le plus rapide) ;
- **« La vidéo finie et un projet à retoucher dans mon logiciel »** (§ 4).

Si elle veut un projet, demande **quel logiciel** elle utilise (Premiere Pro, DaVinci Resolve, Final Cut Pro,
CapCut) et **n'exporte que celui-là**. Ne propose jamais tous les formats d'un coup : c'est plus long, plus lourd, et
on ne sait plus quoi ouvrir.

Retiens ses réponses dans `consignes.md` (`export: mp4 + projet premiere`) : la fois suivante, ne repose pas la
question, propose la même chose.

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

## 4. Le projet modifiable (un seul logiciel : celui de la personne)

Pour retoucher le montage dans son logiciel. Le dossier livré contient **un seul fichier à ouvrir**
(« <nom> - OUVRIR DANS PREMIERE.xml », ou DAVINCI, FINAL CUT), un `LISEZ-MOI.txt`, et un dossier `Medias/` rangé.
Sur la timeline, tout est déjà à sa place : fond et caméra découpés en blocs, **chaque animation** et **chaque
sous-titre** comme un élément séparé, voix, musique, **chaque bruitage**.

1. **Estime d'abord, et dis-le avant de lancer** :
   ```powershell
   python <skill>/scripts/export_projet.py <projet>/build/plan.json <projet>/exports/<nom>-<logiciel> --logiciel premiere --estimer
   ```
   Annonce le temps et la place simplement : « Ça va prendre environ 40 min et 200 Mo. Je le lance en arrière-plan,
   tu peux faire autre chose. » Vérifie la place libre pendant le calcul (le script l'indique).
2. **Lance en arrière-plan** (sans `--estimer`), `--logiciel premiere|davinci|finalcut|capcut`. Machine modeste :
   `--workers 1`.
3. **Explique comment l'ouvrir, pas à pas** (le `LISEZ-MOI.txt` le dit aussi) :
   - **Premiere Pro** : ouvrir Premiere, Fichier, Importer (Ctrl+I), choisir le fichier « OUVRIR DANS PREMIERE »,
     double-cliquer la séquence qui apparaît, puis **Fichier, Enregistrer sous** : la personne obtient son fichier de
     projet `.prproj`, qu'elle rouvrira directement ensuite. Prévenir : **ne pas double-cliquer le .xml dans
     l'Explorateur** (il s'ouvre dans un navigateur).
   - **DaVinci Resolve** : Fichier, Importer, Timeline, puis le fichier « OUVRIR DANS DAVINCI » (.xml ou .otio).
   - **Final Cut Pro** : Fichier, Importer, XML, puis le fichier « OUVRIR DANS FINAL CUT ».
   - **CapCut** : le projet « Cutora - <nom> » est déjà dans sa liste de projets ; fermer et rouvrir CapCut.
   Ouvre le dossier pour elle. Le dossier doit rester entier : le projet pointe vers les fichiers de `Medias/`.
4. **Dis honnêtement ce qui se modifie** : coupes, ordre, durée, chaque animation et chaque sous-titre (déplacer,
   raccourcir, supprimer), le texte des sous-titres (fichier `.srt`, à importer comme piste de sous-titres), musique,
   bruitages, volumes, étalonnage. Le texte et le mouvement **à l'intérieur** d'une animation ne se modifient pas :
   c'est une vidéo. Pour changer un titre animé, le supprimer et ajouter son propre titre, ou demander ici.

Le script retient la vraie vitesse de l'ordinateur dans `~/cutora-studio.json` : les estimations suivantes sont plus
justes.
