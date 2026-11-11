# Installation de Cutora Studio sous Windows, en une seule commande, sans rien demander de technique.
# Usage (PowerShell) : powershell -ExecutionPolicy Bypass -File installer.ps1 [-Atelier "D:\Cutora-Studio"]
# Rapide et sans risque de recommencer : chaque outil déjà présent est sauté. Les gros téléchargements (navigateur de
# rendu, modèle de transcription, vidéos d'exemple) partent en arrière-plan : la personne choisit son style pendant ce temps.
# Journaux : %USERPROFILE%\cutora-studio-installation.log et cutora-studio-arriere-plan.log ; fin du travail en arrière-plan : %USERPROFILE%\cutora-studio-pret.txt
param([string]$Atelier = "$env:USERPROFILE\Documents\Cutora-Studio")

$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$Skill = Split-Path -Parent $PSScriptRoot
$Log = "$env:USERPROFILE\cutora-studio-installation.log"
$Pret = "$env:USERPROFILE\cutora-studio-pret.txt"
$LogFond = "$env:USERPROFILE\cutora-studio-arriere-plan.log"
$debut = Get-Date
function Dire($t) { Write-Output $t; Add-Content -Path $Log -Value ("{0:HH:mm:ss} {1}" -f (Get-Date), $t) -Encoding utf8 }
function Recharger-Path {
    # Après une installation, les nouvelles commandes ne sont connues que des nouveaux terminaux : on relit le PATH.
    $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")
}
function Present($cmd) { return [bool](Get-Command $cmd -ErrorAction SilentlyContinue) }

Dire "== Cutora Studio : installation =="

# 1. Place sur le disque
$lettre = (Split-Path -Qualifier $Atelier).TrimEnd(":")
$libre = [math]::Round((Get-PSDrive $lettre).Free / 1GB, 1)
Dire "Place libre sur ${lettre}: : $libre Go"
if ($libre -lt 6) { Dire "ATTENTION : moins de 6 Go libres. Le studio a besoin d'environ 3 Go, plus la place des projets." }

# 2. Outils de base (winget, intégré à Windows 10 et 11)
$outils = @(
    @{ cmd = "git";    id = "Git.Git";            nom = "git" },
    @{ cmd = "node";   id = "OpenJS.NodeJS.LTS";  nom = "Node.js" },
    @{ cmd = "python"; id = "Python.Python.3.11"; nom = "Python" },
    @{ cmd = "ffmpeg"; id = "Gyan.FFmpeg";        nom = "ffmpeg" }
)
$manquants = @($outils | Where-Object { -not (Present $_.cmd) })
# Le « python » du Microsoft Store n'est qu'un raccourci vers la boutique : on le considère comme absent
if ((Present "python") -and ((Get-Command python).Source -like "*WindowsApps*")) { $manquants += $outils[2] }
if ($manquants.Count -gt 0) {
    if (-not (Present "winget")) {
        Dire "MANQUANT : winget. Installe « App Installer » depuis le Microsoft Store, puis relance l'installation."
        exit 2
    }
    foreach ($o in $manquants) {
        Dire "Installation de $($o.nom)..."
        winget install --id $o.id -e --silent --accept-package-agreements --accept-source-agreements --disable-interactivity | Out-Null
        Recharger-Path
        if (Present $o.cmd) { Dire "OK : $($o.nom)" } else { Dire "A REVOIR : $($o.nom) installé mais pas encore reconnu (redémarrer Claude Code règlera ça)" }
    }
} else { Dire "OK : git, Node.js, Python et ffmpeg déjà présents" }
Recharger-Path

# 3. Bibliothèques Python (un seul appel, environ 150 Mo)
if (Present "python") {
    Dire "Bibliothèques Python..."
    python -m pip install --quiet --disable-pip-version-check --upgrade yt-dlp faster-whisper edge-tts numpy scipy pillow opentimelineio otio-fcp-adapter otio-fcpx-xml-adapter "pycapcut==0.0.4" 2>&1 | Out-Null
    python -c "import faster_whisper, edge_tts, numpy, scipy, PIL, opentimelineio" 2>$null
    if ($LASTEXITCODE -eq 0) { Dire "OK : bibliothèques Python" } else { Dire "A REVOIR : bibliothèques Python incomplètes (relancer : python -m pip install -r ...)" }
}

# 4. Fiches HyperFrames pour l'assistant : seulement le dossier utile (4 Mo), jamais le dépôt entier (500 Mo)
$skills = "$env:USERPROFILE\.claude\skills"
$besoin = @("hyperframes", "hyperframes-cli", "hyperframes-registry", "media-use") | Where-Object { -not (Test-Path "$skills\$_\SKILL.md") }
if ($besoin.Count -gt 0 -and (Present "git")) {
    Dire "Fiches HyperFrames..."
    $tmp = Join-Path $env:TEMP ("hf-" + [guid]::NewGuid().ToString("N").Substring(0, 8))
    git clone --quiet --depth 1 --filter=blob:none --sparse https://github.com/heygen-com/hyperframes $tmp 2>&1 | Out-Null
    git -C $tmp sparse-checkout set skills 2>&1 | Out-Null
    New-Item -ItemType Directory -Force $skills | Out-Null
    foreach ($s in $besoin) {
        if (Test-Path "$tmp\skills\$s") {
            Copy-Item -Recurse -Force "$tmp\skills\$s" "$skills\$s"
            # Codex et les autres assistants lisent ~/.agents/skills
            New-Item -ItemType Directory -Force "$env:USERPROFILE\.agents\skills" | Out-Null
            Copy-Item -Recurse -Force "$tmp\skills\$s" "$env:USERPROFILE\.agents\skills\$s"
        }
    }
    Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue
    Dire "OK : fiches HyperFrames"
} else { Dire "OK : fiches HyperFrames déjà présentes" }

# 5. Atelier et configuration
foreach ($d in @("profils", "projets", "a-monter", "_sons", "_musiques")) { New-Item -ItemType Directory -Force (Join-Path $Atelier $d) | Out-Null }
$conf = "$env:USERPROFILE\cutora-studio.json"
if (-not (Test-Path $conf)) {
    $ram = [math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB)
    $machine = "normale"
    if ($ram -lt 12) { $machine = "modeste" }
    $obj = [ordered]@{ atelier = ($Atelier -replace "\\", "/"); profil_actif = ""; machine = $machine; langue = "fr"; installe_le = (Get-Date -Format "yyyy-MM-dd"); profils = @{} }
    $obj | ConvertTo-Json -Depth 5 | Out-File -Encoding utf8 $conf
}
Dire "OK : atelier dans $Atelier"

# 6. En arrière-plan : les gros téléchargements, qui ne servent qu'au premier montage
Remove-Item $Pret -ErrorAction SilentlyContinue
$fond = @"
`$env:Path = [Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [Environment]::GetEnvironmentVariable('Path','User')
npx --yes hyperframes browser ensure *>&1 | Out-File -Append -Encoding utf8 '$LogFond'
python '$Skill\scripts\medias_exemples.py' *>&1 | Out-File -Append -Encoding utf8 '$LogFond'
`$w = Join-Path `$env:TEMP 'cutora-silence.wav'
ffmpeg -v error -y -f lavfi -i anullsrc=r=16000:cl=mono -t 1 `$w
npx --yes hyperframes transcribe `$w --engine parakeet --language fr --json *>&1 | Out-File -Append -Encoding utf8 '$LogFond'
Set-Content -Path '$Pret' -Value (Get-Date -Format 'yyyy-MM-dd HH:mm:ss') -Encoding utf8
"@
$fichierFond = Join-Path $env:TEMP "cutora-fond.ps1"
$fond | Out-File -Encoding utf8 $fichierFond
Start-Process powershell -WindowStyle Hidden -ArgumentList "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $fichierFond
Dire "EN COURS (arrière-plan) : navigateur de rendu, vidéos d'exemple, modèle de transcription (5 à 15 min selon la connexion)"

# 7. Bilan
# Seuls les outils dont le studio a besoin (doctor signale aussi des options inutiles ici, qui inquiéteraient pour rien)
if (Present "npx") {
    $v = npx --yes hyperframes --version 2>$null | Select-Object -Last 1
    if ($v) { Dire "OK : moteur HyperFrames $v" } else { Dire "A REVOIR : moteur HyperFrames (npx hyperframes --version)" }
}
$dispo = [math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory / 1MB, 1)
if ($dispo -lt 2) { Dire "CONSEIL : seulement $dispo Go de mémoire libre. Fermer les applications lourdes avant un rendu." }
$min = [math]::Round(((Get-Date) - $debut).TotalMinutes, 1)
Dire "== Installation terminée en $min min. La suite se télécharge en arrière-plan. =="
