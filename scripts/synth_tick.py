# Tics synthétisés d'après un spectrogramme de référence.
# usage : python synth_tick.py sortie.wav [f0=880] [h_min=4] [h_max=10] [n=6] [pas=0.095] [decay=0.012]
# Exemple relevé sur une pub : 6 tics, harmoniques 4 à 10 de 880 Hz, espacés de 0,095 s (flèche pointillée).
import sys
import numpy as np
from scipy.io import wavfile
SR = 48000
a = sys.argv[1:] + [None] * 7
out = a[0]; f0 = float(a[1] or 880); h0 = int(a[2] or 4); h1 = int(a[3] or 10)
n = int(a[4] or 6); step = float(a[5] or 0.095); decay = float(a[6] or 0.012)
rng = np.random.default_rng(7)
t = np.arange(int(0.06 * SR)) / SR
one = sum(np.sin(2 * np.pi * f0 * k * t + rng.uniform(0, 6.28)) / (1 + 0.15 * (k - h0)) for k in range(h0, h1 + 1))
one = (one + 0.25 * rng.standard_normal(len(t)) * np.exp(-t / 0.003)) * np.exp(-t / decay) * np.minimum(1, t / 0.0008)
x = np.zeros(int((step * (n - 1) + 0.2) * SR))
for i in range(n):
    s = int(i * step * SR); x[s:s + len(one)] += one
x = x / np.abs(x).max() * 0.7
wavfile.write(out, SR, (np.stack([x, x], 1) * 32767).astype(np.int16))
print("ok", out)
