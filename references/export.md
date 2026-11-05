# Exporter et livrer

Seulement après un accord explicite (« c'est bon, exporte », « je valide »). « Continue » ou « ok » ne suffisent
pas : en cas de doute, demande.

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

## 3. Livrer

- Le fichier final dans `exports/`, et une copie là où la personne le veut (par défaut le dossier
  Téléchargements). Note ce choix dans `~/cutora-studio.json` (`"livraison"`).
- Variantes si utiles : 9:16 et 16:9, version sans sous-titres, fichier `.srt`.
- `CREDITS.md` à jour (musiques CC BY à citer dans la description de la publication).
- Ménage : fichiers intermédiaires supprimés, versions gardées (sources, pas les rendus intermédiaires).
- Puis le **bilan de goût** ([apprentissage.md](apprentissage.md) § 5).
