# Télécharge les vraies vidéos d'exemple de la page de choix (vraies personnes, vrais plans) depuis Mixkit,
# les raccourcit et les allège dans choix/media/. Lancé une fois à l'installation du studio (environ 5 Mo au total).
# Usage : python medias_exemples.py
# Les fichiers ne sont pas dans le dépôt GitHub : la licence Mixkit autorise leur usage dans un montage, pas leur
# redistribution telle quelle. Chaque utilisateur les récupère donc lui-même. Sans eux, la page montre des silhouettes.
import json, subprocess, sys, tempfile, urllib.request
from pathlib import Path

DEST = Path(__file__).resolve().parent.parent / "choix" / "media"
# nom, identifiant Mixkit, début (s), durée (s), largeur de sortie, titre de la page Mixkit
CLIPS = [
    ("face", 42323, 0.0, 7.0, 540, "portrait-of-an-influencer-talking-to-the-camera"),
    ("studio", 41272, 1.0, 8.0, 640, "youtuber-vlogging-in-his-studio"),
    ("vlog", 46352, 3.0, 4.0, 640, "vlogger-man-recording-video-outdoors"),
    ("rue", 3428, 0.0, 4.0, 640, "street-with-people-walking-at-dusk"),
    ("ville", 49878, 0.0, 4.0, 540, "big-city-at-night-from-an-aerial-shot"),
    ("clavier", 41183, 0.0, 4.0, 540, "working-on-a-macbook-pro"),
    ("telephone", 39774, 0.0, 4.0, 640, "hands-of-a-young-woman-typing-on-her-smartphone"),
]


def main():
    DEST.mkdir(parents=True, exist_ok=True)
    faits = []
    with tempfile.TemporaryDirectory() as tmp:
        for nom, vid, debut, duree, larg, titre in CLIPS:
            sortie = DEST / f"{nom}.mp4"
            if sortie.exists():
                faits.append(nom); continue
            src = Path(tmp) / f"{vid}.mp4"
            url = f"https://assets.mixkit.co/videos/{vid}/{vid}-720.mp4"
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                src.write_bytes(urllib.request.urlopen(req, timeout=60).read())
                subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(debut), "-t", str(duree), "-i", str(src), "-an",
                                "-vf", f"scale={larg}:-2,fps=25", "-c:v", "libx264", "-crf", "30", "-preset", "slow",
                                "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(sortie)], check=True)
                faits.append(nom)
                print("ok", nom, round(sortie.stat().st_size / 1024), "Ko")
            except Exception as e:
                print("échec", nom, e, file=sys.stderr)
    (DEST / "liste.json").write_text(json.dumps(faits), encoding="utf-8")
    (DEST / "CREDITS.md").write_text("# Vidéos d'exemple\n\nSource : Mixkit (licence Mixkit, gratuite). Pages d'origine :\n\n" +
        "\n".join(f"- {n} : https://mixkit.co/free-stock-video/{t}-{i}/" for n, i, _, _, _, t in CLIPS) + "\n", encoding="utf-8")
    print(len(faits), "vidéos prêtes dans", DEST)


if __name__ == "__main__":
    main()
