# Mesure des bruitages : durée, attaque (50 % de l'enveloppe), pic, fin.  usage : python measure.py <dossier ou fichiers>
import sys, glob, os, subprocess
import numpy as np
files = []
for a in sys.argv[1:]:
    files += sorted(glob.glob(os.path.join(a, "*.*"))) if os.path.isdir(a) else [a]
for f in files:
    if not f.lower().endswith((".mp3", ".wav", ".ogg", ".flac", ".m4a")):
        continue
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-ac", "1", "-ar", "22050", "-f", "s16le", "-"], capture_output=True).stdout
    x = np.abs(np.frombuffer(raw, np.int16).astype(np.float32) / 32768); sr = 22050
    if not len(x):
        continue
    env = np.convolve(x, np.ones(220) / 220, "same")
    on = int(np.argmax(env > 0.5 * env.max())); pk = int(env.argmax())
    last = len(env) - int(np.argmax(env[::-1] > 0.05 * env.max()))
    print(f"{os.path.basename(f):28} durée={len(x)/sr:6.2f}  attaque={on/sr:6.3f}  pic={pk/sr:6.3f}  fin={last/sr:6.2f}")
