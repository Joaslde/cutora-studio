# Installer le studio

Environ 20 à 40 minutes, une seule fois. L'utilisateur n'a rien de technique à faire : tu lances tout, tu expliques
chaque étape en une phrase, tu ne lui demandes d'agir que pour cliquer « Oui » sur une fenêtre Windows ou accepter
une autorisation de Claude. Quand une commande demande une autorisation, dis en une phrase pourquoi elle est sans
risque.

Le skill vit dans `~/.claude/skills/cutora-studio/` (`<skill>` ci-dessous). Les commandes sont données pour Windows
(PowerShell) ; macOS : `brew install`, Linux : le gestionnaire de paquets.

## 1. Vérifier l'ordinateur

```powershell
Get-PSDrive C | Select-Object Used,Free
(Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB
git --version; node -v; python --version; ffmpeg -version; yt-dlp --version
```

Affiche une ligne par outil : présent (version) ou absent.

- Moins de 15 Go libres : préviens. Le studio occupe 3 à 5 Go (outils + modèles), plus les projets.
- Moins de 8 Go de mémoire : les rendus et le détourage seront lents, note-le dans `~/cutora-studio.json`
  (`"machine": "modeste"`) pour rendre toujours avec `-w 1`.

## 2. Installer ce qui manque

| Outil | Sert à | Windows |
|---|---|---|
| git | récupérer les skills | `winget install --id Git.Git -e` |
| Node.js 22 LTS | HyperFrames (moteur de montage) | `winget install --id OpenJS.NodeJS.LTS -e` |
| Python 3.11 | scripts du studio, transcription | `winget install --id Python.Python.3.11 -e` |
| ffmpeg | toute la vidéo et le son | `winget install --id Gyan.FFmpeg -e` |
| deno | yt-dlp sur YouTube (il lui faut un moteur JavaScript) | `winget install --id DenoLand.Deno -e` |

Puis les bibliothèques Python :

```powershell
python -m pip install --upgrade yt-dlp faster-whisper edge-tts numpy scipy pillow
```

- Après `winget`, les nouvelles commandes ne sont pas reconnues dans le terminal déjà ouvert : utilise le chemin
  complet ou demande à l'utilisateur de relancer Claude Code, puis reprends à l'étape suivante.
- winget absent : explique comment installer « App Installer » depuis le Microsoft Store.
- Python sous Windows : préfixe `$env:PYTHONUTF8=1` (ou `PYTHONUTF8=1` en bash) pour les accents.
- Vérifie chaque outil (version affichée) avant de passer à la suite.

## 3. Le moteur HyperFrames et ses skills

HyperFrames s'utilise via `npx hyperframes <commande>` (rien à installer en global). Installe ses skills, qui
contiennent son contrat de rendu et son catalogue de blocs :

```powershell
npx --yes hyperframes skills update
```

Cela installe `hyperframes`, `hyperframes-cli`, `hyperframes-registry` et `media-use`. Si la commande échoue
(erreur fréquente sous Windows), récupère **seulement le dossier des fiches**, jamais le dépôt entier (il pèse plus de
500 Mo et peut bloquer l'installation pendant des heures sur une connexion moyenne) :

```powershell
git clone --depth 1 --filter=blob:none --sparse https://github.com/heygen-com/hyperframes <dossier temporaire vide>
git -C <dossier temporaire> sparse-checkout set skills
```

Environ 4 Mo, quelques secondes. Copie ensuite `hyperframes`, `hyperframes-cli`, `hyperframes-registry` et
`media-use` de `skills/` dans `~/.claude/skills/`, puis supprime le dossier temporaire. Vérifie qu'aucun skill
existant n'est écrasé sans le dire.

**Ces fiches ne bloquent jamais le parcours** : elles servent au moment du montage, pas pour choisir un style. Si leur
récupération traîne, passe à l'étape suivante (choix du style) et termine-les en arrière-plan. Dis-le clairement à la
personne : « Je finis de récupérer un dernier outil en arrière-plan, ça ne t'empêche pas de continuer : on passe au
choix de ton style. » Ne lui promets jamais de la prévenir plus tard sans lui dire ce qu'elle peut faire en attendant.

Un téléchargement qui dépasse 5 minutes ou qui échoue deux fois : arrête-le, dis-le simplement, et propose la
solution de secours au lieu de relancer la même chose.

Test : `npx hyperframes --version`. Le premier rendu télécharge un navigateur sans interface (environ 550 Mo).

Puis les vraies vidéos d'exemple de la page de choix (environ 1,5 Mo, licence Mixkit, jamais redistribuées) :

```powershell
python <skill>/scripts/medias_exemples.py
```

## 4. Transcription et détourage

Deux moteurs de transcription, tous deux gratuits et locaux :

1. **Parakeet** (intégré à HyperFrames, rapide) : `npx hyperframes transcribe audio16k.wav --engine parakeet
   --language fr --json`. Il télécharge son modèle au premier usage (environ 640 Mo).
2. **faster-whisper** (`<skill>/scripts/transcrire.py`) : plus fiable quand Parakeet se met à écrire en anglais sur
   du français, ou sur un accent marqué. Modèle `small` (460 Mo) par défaut, `medium` (environ 1,5 à 2,3 Go) pour un résultat
   plus juste, téléchargés au premier usage.

Détourage d'une personne (tête qui dépasse d'un cadre, fond changé, texte derrière la personne) :
`npx hyperframes remove-background` (modèle local de 170 Mo, téléchargé au premier usage). Lent sur CPU : environ 0,2 à 0,7
image par seconde, donc plusieurs heures pour 2 minutes de vidéo. Le lancer tôt, en arrière-plan.

Ne télécharge pas les modèles pendant l'installation : ils viennent au premier montage qui en a besoin.
Dis-le à l'utilisateur.

## 5. Créer l'atelier

Demande où le mettre (recommandé : `Documents\Cutora-Studio`), puis crée :

```text
Cutora-Studio/
├── profils/                 un dossier par personne ou par client (jamais dans le dossier du skill)
│   └── <nom>/               acquis.md, gouts.md, consignes.md, journal.md, charte/, broll/
│       └── styles/<style>/  style.md, acquis.md, choix.json, references/ (une personne peut avoir plusieurs styles)
├── projets/
│   └── <nom>/<projet>/      references, a-roll, b-roll, voix, exports, montage (créé par toi)
├── a-monter/                boîte de dépôt : la personne y glisse rushs et B-rolls, tu crées le projet
├── _sons/                   packs de sons achetés par l'utilisateur (avec leur licence)
└── _musiques/
```

Puis écris `~/cutora-studio.json` :

```json
{ "atelier": "C:/Users/<nom>/Documents/Cutora-Studio", "profil_actif": "", "machine": "normale", "langue": "fr",
  "installe_le": "<date>", "profils": { "<nom>": { "etape": 2, "autonomie": 1, "videos_validees": 0 } } }
```

**Pourquoi le profil vit hors du skill** : une mise à jour du skill remplace son dossier. Les goûts de
l'utilisateur ne doivent jamais être effacés par une mise à jour.

## 6. Autorisations

Propose (sans l'imposer) d'autoriser une fois pour toutes les commandes du studio, pour ne plus avoir de fenêtre
d'autorisation à chaque étape. Avec son accord, ajoute dans `~/.claude/settings.json`, section
`permissions.allow` : `Bash(ffmpeg *)`, `Bash(ffprobe *)`, `Bash(npx hyperframes *)`, `Bash(yt-dlp *)`,
`Bash(python *)`. Montre la liste avant d'écrire.

## 7. Test et suite

1. Test de 8 secondes : une voix de 2 phrases (`<skill>/scripts/voix.py`), un titre mot par mot, un bruitage,
   `npx hyperframes check`, aperçu dans le navigateur. Pas d'export.
2. Résumé en 5 lignes : ce qui est installé, où est l'atelier, l'espace utilisé, ce qui a échoué (et quoi faire).
3. Enchaîne sur **Découvrir le style** ([decouverte-style.md](decouverte-style.md)) : « Maintenant, on fait
   connaissance avec ton style. Tu as une vidéo que tu aimes, ou tu préfères que je te montre des choix ? »
