# Vérifie qu'une vidéo finale se lit partout (Frame.io, YouTube, Instagram, TikTok, CapCut, Premiere, téléphones),
# et la corrige si besoin. Usage : python verifier_export.py <video.mp4> [--corriger]
# Norme visée, la plus compatible : conteneur MP4, H.264 profil High, image 8 bits 4:2:0, cadence fixe, dimensions paires,
# couleurs BT.709, son AAC-LC 48 kHz stéréo, index en tête de fichier (lecture en ligne immédiate).
import json, subprocess, sys
from pathlib import Path

f = Path(sys.argv[1]).resolve()
info = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(f)],
                                 capture_output=True, text=True).stdout or "{}")
v = next((s for s in info.get("streams", []) if s["codec_type"] == "video"), {})
a = next((s for s in info.get("streams", []) if s["codec_type"] == "audio"), None)
problemes = []
if v.get("codec_name") != "h264": problemes.append(f"vidéo en {v.get('codec_name')} au lieu de H.264")
if v.get("pix_fmt") != "yuv420p": problemes.append(f"image en {v.get('pix_fmt')} au lieu de yuv420p (8 bits 4:2:0)")
if v.get("profile") not in ("High", "Main", "Constrained Baseline"): problemes.append(f"profil H.264 {v.get('profile')}")
if v.get("r_frame_rate") != v.get("avg_frame_rate"): problemes.append("cadence variable")
if int(v.get("width", 0)) % 2 or int(v.get("height", 0)) % 2: problemes.append("dimensions impaires")
if a is None: problemes.append("pas de piste son (certains lecteurs refusent)")
elif a.get("codec_name") != "aac" or int(a.get("sample_rate", 0)) != 48000 or int(a.get("channels", 0)) != 2:
    problemes.append(f"son en {a.get('codec_name')} {a.get('sample_rate')} Hz {a.get('channels')} canaux au lieu de AAC 48 kHz stéréo")
tete = f.read_bytes()[:2_000_000]
if not (0 <= tete.find(b"moov") < (tete.find(b"mdat") if tete.find(b"mdat") >= 0 else 10**12)):
    problemes.append("index en fin de fichier (lecture en ligne lente, certains sites échouent)")

if not problemes:
    print(f"OK : {f.name} se lit partout ({v.get('width')}x{v.get('height')}, {v.get('r_frame_rate')} i/s, H.264, AAC)")
    sys.exit(0)
print("À corriger :", " ; ".join(problemes))
if "--corriger" not in sys.argv:
    sys.exit(1)
fps = v.get("r_frame_rate", "30/1")
sortie = f.with_name(f.stem + "-compatible.mp4")
entrees = ["-i", str(f)]
cartes = ["-map", "0:v:0", "-map", "0:a:0"]
if a is None:  # une piste son silencieuse, de la durée de la vidéo
    entrees += ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"]
    cartes = ["-map", "0:v:0", "-map", "1:a:0", "-shortest"]
cmd = ["ffmpeg", "-v", "error", "-y", *entrees, *cartes,
       "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2,format=yuv420p", "-r", fps, "-c:v", "libx264", "-profile:v", "high",
       "-preset", "slow", "-crf", "16", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
       "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-ac", "2", "-movflags", "+faststart", str(sortie)]
subprocess.run(cmd, check=True)
print("Corrigé :", sortie)
