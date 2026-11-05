# Décortique une vidéo de référence : fiche technique, coupes, planches d'images, spectrogramme, loudness.
# usage : python analyse_reference.py references/video.mp4 analyse/
# Ensuite : regarder les planches et le spectrogramme, transcrire (transcrire.py), zoomer sur les transitions
# (bandes à 12 images/s) et écrire ANALYSE-REFERENCE.md avec le modèle fourni.
import sys, os, re, json, subprocess

src, out = sys.argv[1], sys.argv[2]
os.makedirs(f"{out}/frames", exist_ok=True)
run = lambda *a: subprocess.run(a, capture_output=True, text=True)

# 1. Fiche technique
info = json.loads(run("ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type,width,height,r_frame_rate",
                      "-of", "json", src).stdout)
dur = float(info["format"]["duration"])
print("Durée", round(dur, 2), "s |", [(s["codec_type"], s.get("width"), s.get("height"), s.get("r_frame_rate")) for s in info["streams"]])

# 2. Coupes nettes (changement de plan)
r = run("ffmpeg", "-hide_banner", "-i", src, "-vf", "select='gt(scene,0.18)',showinfo", "-an", "-f", "null", "-")
cuts = [round(float(t), 2) for t in re.findall(r"pts_time:([\d.]+)", r.stderr)]
print(len(cuts), "coupes :", cuts)

# 3. Images toutes les 0,5 s avec le temps incrusté, puis planches de 32 images (16 s chacune)
run("ffmpeg", "-v", "error", "-y", "-i", src, "-vf", "fps=2,scale=216:-1", "-an", f"{out}/frames/f_%03d.jpg")
n = len(os.listdir(f"{out}/frames"))
for i in range((n + 31) // 32):
    run("ffmpeg", "-v", "error", "-y", "-start_number", str(i * 32 + 1), "-i", f"{out}/frames/f_%03d.jpg",
        "-frames:v", "1", "-vf", "tile=8x4:padding=4:color=white", f"{out}/planche_{i}_{i*16}s-{i*16+16}s.jpg")

# 4. Son : spectrogramme et loudness
run("ffmpeg", "-v", "error", "-y", "-i", src, "-vn", "-ac", "1", "-ar", "16000", f"{out}/audio16k.wav")
run("ffmpeg", "-v", "error", "-y", "-i", f"{out}/audio16k.wav", "-lavfi",
    "showspectrumpic=s=1600x600:legend=1:scale=log:fscale=log", f"{out}/spectrogramme.png")
lo = run("ffmpeg", "-hide_banner", "-i", src, "-vn", "-af", "ebur128=peak=true", "-f", "null", "-").stderr
lo = lo[lo.rfind("Summary"):]
print("Son :", " ".join(re.findall(r"(I:\s*[-\d.]+ LUFS|Peak:\s*[-\d.]+ dBFS)", lo)))
json.dump({"duree": dur, "coupes": cuts}, open(f"{out}/mesures.json", "w"), indent=1)
print("Fait :", out, "(planches, spectrogramme.png, audio16k.wav pour la transcription, mesures.json)")
print("Bande à 12 i/s autour d'une transition à T secondes :")
print(f'  ffmpeg -ss T -t 0.7 -i "{src}" -vf "fps=12,scale=180:-1,tile=8x1" -frames:v 1 transition_T.jpg')
