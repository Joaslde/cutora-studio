# Installer Cutora Studio avec un seul message

1. Ouvre l'application Claude sur ton ordinateur et clique sur l'onglet **Code** (le logo `</>`).
   Pas encore l'application ? Télécharge-la sur claude.com/fr/download (il faut un abonnement Pro ou Max).
2. Copie **tout le bloc ci-dessous**, colle-le dans Claude Code et envoie.
3. Laisse Claude travailler. Quand il te demande une autorisation, il t'explique pourquoi : accepte. Si Windows
   demande « Voulez-vous autoriser cette application à modifier votre appareil ? », clique sur **Oui**.

```
Installe et lance Cutora Studio, mon studio de montage vidéo : https://github.com/Joaslde/cutora-studio

Je ne suis pas technique. Fais tout toi-même dans le terminal, explique chaque étape en une phrase simple, et ne me
demande d'agir que si c'est vraiment indispensable (par exemple cliquer « Oui » sur une fenêtre Windows). Quand tu
me demandes une autorisation, dis-moi en une phrase pourquoi elle est sans risque. Ne me montre jamais d'erreur
brute : dis-moi ce qui se passe et ce que tu fais pour le régler.

1. Regarde mon ordinateur : le système (Windows, Mac ou Linux), la place libre sur le disque, et si git est
   installé (git --version). Préviens-moi s'il reste moins de 15 Go.

2. Si git manque, installe-le toi-même :
   - Windows : winget install --id Git.Git -e --accept-package-agreements --accept-source-agreements
   - Mac : xcode-select --install, ou brew install git si Homebrew est là
   - Linux : sudo apt install -y git (ou l'équivalent de ma distribution)
   Si tu ne peux pas l'installer toi-même (winget absent, droits refusés, mot de passe demandé), guide-moi pas à pas :
   le lien exact à ouvrir, les boutons à cliquer, une étape à la fois, et attends que je te dise « c'est fait ».
   Ensuite vérifie avec git --version. Si la commande n'est pas reconnue juste après l'installation, utilise son
   chemin complet (sous Windows : "C:\Program Files\Git\cmd\git.exe").

3. Installe le skill dans le dossier des skills de Claude :
   - s'il n'y est pas encore : git clone https://github.com/Joaslde/cutora-studio.git dans ~/.claude/skills/cutora-studio
     (sous Windows : "$env:USERPROFILE\.claude\skills\cutora-studio") ;
   - s'il y est déjà : mets-le à jour avec git pull dans ce dossier. Mes styles ne sont pas dedans, ils ne risquent rien.
   Vérifie que le fichier SKILL.md est bien présent dans ce dossier.

4. Installe les outils de montage. Sous Windows, lance le script d'installation du skill, en une seule commande :
   powershell -ExecutionPolicy Bypass -File "$env:USERPROFILE\.claude\skills\cutora-studio\scripts\installer.ps1"
   Annonce-moi d'abord la durée (5 à 10 minutes si rien n'est installé, moins d'une minute sinon). Sous Mac ou Linux,
   suis la fiche references/installation.md du skill. Les gros téléchargements continuent en arrière-plan : ne me
   fais pas attendre pour eux.

   Ensuite, lis entièrement ~/.claude/skills/cutora-studio/SKILL.md et continue le parcours du studio comme si j'avais
   tapé /cutora-studio : le choix de mon style. Suis les règles du skill, en particulier le guidage pas à pas.

5. Quand l'installation des outils est finie, dis-moi en 3 lignes ce qui est installé, puis continue avec le choix
   de mon style. Rappelle-moi aussi qu'à partir de la prochaine fois, il me suffira d'ouvrir Claude Code et de taper
   /cutora-studio (après avoir fermé et rouvert l'application une fois).
```

## Mettre à jour plus tard

Dans Claude Code : « Mets à jour le skill Cutora Studio (git pull dans ~/.claude/skills/cutora-studio). »
Tes styles et tes projets ne sont pas touchés.
