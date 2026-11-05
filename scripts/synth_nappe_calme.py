# Nappe musicale du montage : calme, continue, très régulière (comme la référence), médium audible sur téléphone.
# La mineur, 96 BPM, un accord toutes les deux mesures.
# Lancer : python synth_nappe_calme.py <durée en s> <sortie.wav>
import sys
import numpy as np
from pathlib import Path
from scipy.io import wavfile
from scipy.signal import fftconvolve, butter, sosfilt

SR = 48000
DUR = float(sys.argv[1]) if len(sys.argv) > 1 else 60.0
N = int(DUR * SR)
T = np.arange(N) / SR
rng = np.random.default_rng(11)
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("nappe.wav")
BEAT = 60 / 96
BAR = 4 * BEAT
midi = lambda m: 440 * 2 ** ((m - 69) / 12)

A2, F2, C3, G2 = 45, 41, 48, 43
PROG = [  # fondamentale, notes de l'accord (MIDI)
    (A2, [57, 60, 64, 69]),   # la mineur
    (F2, [53, 57, 60, 65]),   # fa majeur
    (C3, [55, 60, 64, 67]),   # do majeur
    (G2, [55, 59, 62, 67]),   # sol majeur
]
SPAN = 2 * BAR

def saw_pad(freq, cutoff, i0, i1):
    tt = T[i0:i1]
    out = np.zeros(i1 - i0)
    for det in (-0.005, 0.0, 0.006):
        f = freq * (1 + det)
        k = 1
        while f * k < cutoff:
            out += (1 / k) * (1 - f * k / cutoff) ** 1.5 * np.sin(2 * np.pi * f * k * tt + rng.uniform(0, 6.28))
            k += 1
    return out

pad, bass, pluck = np.zeros(N), np.zeros(N), np.zeros(N)
t0, idx = 0.0, 0
while t0 < DUR:
    root, notes = PROG[idx % 4]
    a, b = max(0, int((t0 - 0.6) * SR)), min(N, int((t0 + SPAN + 0.6) * SR))
    wgt = np.clip(np.minimum((T[a:b] - t0 + 0.5) / 1.0, (t0 + SPAN + 0.5 - T[a:b]) / 1.0), 0, 1)
    pad[a:b] += wgt * sum(saw_pad(midi(m), 1900, a, b) for m in notes) / 2
    bass[a:b] += wgt * np.sin(2 * np.pi * midi(root - 12) * T[a:b])
    # arpège doux en croches, registre médium
    arp = [notes[0] + 12, notes[2] + 12, notes[1] + 12, notes[3] + 12]
    L = int(0.45 * SR)
    tl = np.arange(L) / SR
    k, t = 0, t0
    while t < t0 + SPAN - 0.01 and t < DUR:
        f = midi(arp[k % 4])
        note = (np.sin(2 * np.pi * f * tl) + 0.3 * np.sin(2 * np.pi * 2 * f * tl)) * np.exp(-tl / 0.18) * np.minimum(1, tl / 0.003)
        s = int(t * SR)
        e = min(N, s + L)
        pluck[s:e] += note[: e - s] * (1.0 if k % 2 == 0 else 0.7)
        k += 1
        t += BEAT / 2
    t0 += SPAN
    idx += 1

pad *= 0.9 + 0.1 * np.sin(2 * np.pi * T / 6.4)
ir_len = int(2.2 * SR)
ti = np.arange(ir_len) / SR
lp = butter(1, 4500, "lowpass", fs=SR, output="sos")
irs = [sosfilt(lp, rng.standard_normal(ir_len)) * np.exp(-ti / 0.5) for _ in range(2)]
dry = pad / np.abs(pad).max() * 0.55 + bass / np.abs(bass).max() * 0.35 + pluck / np.abs(pluck).max() * 0.3
send = pad / np.abs(pad).max() * 0.5 + pluck / np.abs(pluck).max() * 0.5
mix = np.stack([dry + 0.35 * fftconvolve(send, ir)[:N] / np.abs(fftconvolve(send, ir)[:N]).max() for ir in irs], 1)
fade = np.clip(np.minimum(T / 1.0, (DUR - T) / 1.5), 0, 1)[:, None]
mix = sosfilt(butter(2, 30, "highpass", fs=SR, output="sos"), mix * fade, axis=0)
mix = mix / np.abs(mix).max() * 0.85
OUT.parent.mkdir(parents=True, exist_ok=True)
wavfile.write(OUT, SR, (mix * 32767).astype(np.int16))
print("ok", OUT)
