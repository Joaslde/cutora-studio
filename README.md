# Cutora Studio

Un skill Claude Code qui fait de Claude un monteur vidéo complet, qui apprend **ton** style et s'améliore à chaque
correction.

- **Installe tout** : ffmpeg, HyperFrames, yt-dlp, transcription, détourage. Tu n'as rien de technique à faire.
- **Trouve ton style avec toi** : une page s'ouvre dans ton navigateur, tu cliques sur ce que tu aimes (format,
  couleurs, polices, sous-titres, animations, rythme, musique), ou tu colles le lien d'une vidéo modèle. Tu peux
  avoir plusieurs styles.
- **Reproduit une référence au plus près** : analyse plan par plan, image, rythme et son mesurés.
- **Monte tes vidéos** : dépose tes rushs et tes B-rolls, il dérushe, monte, anime, sonorise, améliore l'image et
  le son, te montre l'aperçu, et n'exporte qu'avec ton accord.
- **Apprend de toi** : chaque remarque est notée, classée et retenue. Plus tu l'utilises, moins tu as à corriger,
  jusqu'au montage presque automatique.

Formats : face caméra avec motion design, navigation (plein visage / écran partagé), montage complet avec B-roll,
motion design sans visage, capture d'écran et tutoriel, découpe d'une vidéo longue en shorts.

## Installer

Il faut un abonnement Claude (Pro ou Max) avec **Claude Code** : l'application de bureau Claude (onglet **Code**),
le terminal ou VS Code. Windows, macOS ou Linux, et environ 10 Go libres.

**Le plus simple : demander à Claude de l'installer.** Ouvre Claude Code et colle ce message :

```
Installe le skill Cutora Studio depuis https://github.com/Joaslde/cutora-studio :
clone le dépôt dans le dossier des skills de Claude (~/.claude/skills/cutora-studio),
installe git d'abord s'il manque, puis dis-moi de redémarrer Claude Code.
```

Redémarre Claude Code, puis tape **`/cutora-studio`** : le studio installe ses outils et te guide pas à pas.

**À la main** (si tu préfères) :

```
git clone https://github.com/Joaslde/cutora-studio.git ~/.claude/skills/cutora-studio
```

Sous Windows (PowerShell) : `git clone https://github.com/Joaslde/cutora-studio.git "$env:USERPROFILE\.claude\skills\cutora-studio"`

**Mettre à jour** : `git -C ~/.claude/skills/cutora-studio pull` (tes styles ne sont pas touchés : ils vivent dans ton
atelier, pas dans le skill).

## Contenu

- `SKILL.md` : le point d'entrée.
- `references/` : la méthode (installation, découverte du style, apprentissage, formats, montage, image et son,
  bruitages, B-roll, qualité, export, pièges, style par défaut).
- `choix/` : la page de découverte du style.
- `modele-montage/` : le générateur qui transforme ton style et un plan en projet HyperFrames prêt à montrer.
- `scripts/` : outils Python (serveur de la page de choix, analyse de référence, transcription, voix off, sons).
- `profil-modele/` : les fichiers de profil copiés pour chaque personne.

Tes styles et tes préférences sont rangés dans ton atelier (`Documents/Cutora-Studio/profils/`), jamais dans le
dossier du skill : une mise à jour du skill ne les efface pas.

Voir [CREDITS.md](CREDITS.md).
