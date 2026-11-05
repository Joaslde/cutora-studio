# Reconstruit le mixage audio de montage/index.html avec ffmpeg (sans rendre la vidéo) pour le mesurer.
# usage : python mixcheck.py <projet>/index.html [sortie.wav]
import re, subprocess, sys
from pathlib import Path

PROJ = Path(sys.argv[1]).parent if len(sys.argv) > 1 else Path.cwd()
html = (Path(sys.argv[1]) if len(sys.argv) > 1 else PROJ / "index.html").read_text(encoding="utf-8")
out = sys.argv[2] if len(sys.argv) > 2 else str(PROJ / "mixcheck.wav")
tags = re.findall(r"<audio ([^>]*)>", html)
ins, filt, labels = [], [], []
for i, t in enumerate(tags):
    a = dict(re.findall(r'([\w-]+)="([^"]*)"', t))
    st, d, v = float(a["data-start"]), float(a["data-duration"]), float(a.get("data-volume", 1))
    ins += ["-i", str(PROJ / a["src"])]
    fo = float(a.get("data-fade-out", 0))
    chain = f"[{i}:a]aformat=sample_rates=48000:channel_layouts=stereo,atrim=0:{d},volume={v}"
    if fo:
        chain += f",afade=t=out:st={d - fo}:d={fo}"
    chain += f",adelay={int(st * 1000)}|{int(st * 1000)}[a{i}]"
    filt.append(chain)
    labels.append(f"[a{i}]")
filt.append("".join(labels) + f"amix=inputs={len(labels)}:normalize=0:duration=longest[m]")
script = Path(out).with_suffix(".txt")
script.write_text(";\n".join(filt), encoding="utf-8")
subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-/filter_complex", str(script), "-map", "[m]", "-t", re.search(r'id="root"[^>]*data-duration="([\d.]+)"', html).group(1), out], check=True)
r = subprocess.run(["ffmpeg", "-hide_banner", "-i", out, "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
summ = r[r.rfind("Summary"):]
print(" ".join(re.findall(r"(I:\s*[-\d.]+ LUFS|Peak:\s*[-\d.]+ dBFS|LRA:\s*[-\d.]+ LU)", summ)))
