# Modèle de nappe de suspense calée sur les scènes (exemple : pub Cutora, 66 s, ré mineur, 100 BPM).
# Adapter DUR, CHORDS (début de chaque accord), on_windows (pulsation), les courbes env_curve et le dossier de sortie A.
# Lancer : python synth_bed.py  (écrit A/music/suspense-raw.wav, puis normaliser avec loudnorm)
from pathlib import Path
from scipy.io import wavfile
from scipy.signal import fftconvolve, butter, sosfilt

SR = 48000
A = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
rng = np.random.default_rng(7)

def save(path, x, peak=0.89):
    x = x / (np.abs(x).max() + 1e-9) * peak
    if x.ndim == 1:
        x = np.stack([x, x], 1)
    wavfile.write(path, SR, (x * 32767).astype(np.int16))

# ---------- Tic de la flèche (relevé sur la référence : harmoniques 4 à 10 de 880 Hz, ~30 ms) ----------
def tick(f0=880, parts=range(4, 11), dur=0.06, decay=0.012):
    t = np.arange(int(dur * SR)) / SR
    x = sum(np.sin(2 * np.pi * f0 * k * t + rng.uniform(0, 6.28)) / (1 + 0.15 * (k - 4)) for k in parts)
    x += 0.25 * rng.standard_normal(len(t)) * np.exp(-t / 0.003)  # petit transitoire
    return x * np.exp(-t / decay) * np.minimum(1, t / 0.0008)

def seq(n, step, one):
    out = np.zeros(int((step * (n - 1) + 0.2) * SR))
    for i in range(n):
        s = int(i * step * SR)
        out[s:s + len(one)] += one * (0.9 + 0.1 * (i % 2))
    return out

(A / "sfx2").mkdir(parents=True, exist_ok=True); (A / "music").mkdir(parents=True, exist_ok=True)
save(A / "sfx2" / "arrow-ticks.wav", seq(6, 0.095, tick()), 0.7)

# ---------- Tic d'horloge sec (frise du montage automatique) ----------
t = np.arange(int(0.12 * SR)) / SR
bp = butter(2, [1800, 5200], "bandpass", fs=SR, output="sos")
clk = sosfilt(bp, rng.standard_normal(len(t))) * np.exp(-t / 0.006)
clk += 0.5 * np.sin(2 * np.pi * 1150 * t) * np.exp(-t / 0.018)
save(A / "sfx2" / "clock-tick.wav", clk, 0.7)

# ---------- Nappe de suspense (66 s, ré mineur, 100 BPM, calée sur les scènes) ----------
DUR = 66.0
N = int(DUR * SR)
T = np.arange(N) / SR
BEAT = 0.6           # noire à 100 BPM
EIGHTH = BEAT / 2
BAR = BEAT * 4

def midi(m):
    return 440 * 2 ** ((m - 69) / 12)

def env_curve(points):
    """Courbe par morceaux linéaires [(t, v), ...] évaluée sur T."""
    ts, vs = zip(*points)
    return np.interp(T, ts, vs)

# Accords (notes MIDI) par section : temps de début absolus de la vidéo
D2, F2, G2, A2, Bb1, C2 = 38, 41, 43, 45, 34, 36
def triad(root, minor=True):
    return [root, root + 12, root + 12 + (3 if minor else 4), root + 19]
CHORDS = [  # (début, notes)
    (0.0, [D2, A2]),                                   # écran de gauche : quinte à vide, retenue
    (14.5, triad(D2)), (16.9, triad(Bb1 + 12, False)), (19.3, triad(G2)), (21.7, [A2, A2 + 12, A2 + 16, A2 + 19]),
    (24.1, triad(D2)), (26.5, triad(Bb1 + 12, False)), (28.9, triad(G2)), (31.3, [A2, A2 + 12, A2 + 16, A2 + 19]),
    (33.7, triad(D2)),
    (36.5, [D2, D2 + 12, D2 + 15]),                    # la différence : suspension
    (40.6, triad(Bb1 + 12, False)),                    # "présenté" : ouverture
    (41.7, [D2, D2 + 1 + 12, D2 + 15]),                # fond marine : plus sombre (cluster)
    (46.4, [D2, D2 + 12, D2 + 15, D2 + 19]),
    (48.3, triad(D2)), (50.7, triad(Bb1 + 12, False)), (53.1, triad(F2, False)), (55.5, [C2 + 12, C2 + 24, C2 + 28, C2 + 31]),
    (57.5, triad(Bb1 + 12, False)), (59.9, [A2, A2 + 12, A2 + 16, A2 + 19]),
    (60.7, [D2, D2 + 12, D2 + 16, D2 + 19, D2 + 24]),  # CTA : ré majeur, résolution
]

def pad_note(freq, cutoff, a, b):
    """Trois dents de scie légèrement désaccordées, harmoniques coupées à cutoff, calculées sur [a, b]."""
    i0, i1 = max(0, int(a * SR)), min(N, int(b * SR))
    tt = T[i0:i1]
    out = np.zeros(N)
    for det in (-0.006, 0.0, 0.0065):
        f = freq * (1 + det)
        k = 1
        while f * k < cutoff:
            g = (1 / k) * (1 - (f * k / cutoff)) ** 1.5
            out[i0:i1] += g * np.sin(2 * np.pi * f * k * tt + rng.uniform(0, 6.28))
            k += 1
    return out

pad = np.zeros(N)
strings = np.zeros(N)
cut_for = lambda t0: 1100 if t0 < 14.5 else (2400 if t0 < 36.5 else (2800 if t0 < 41.7 else (1300 if t0 < 48.3 else 2600)))
for i, (t0, notes) in enumerate(CHORDS):
    t1 = CHORDS[i + 1][0] if i + 1 < len(CHORDS) else DUR
    a, b = t0 - 0.5, t1 + 0.5
    w = np.clip(np.minimum((T - t0 + 0.4) / 0.8, (t1 + 0.4 - T) / 0.8), 0, 1)  # fondu enchaîné entre accords
    seg = sum(pad_note(midi(m), cut_for(t0), a, b) for m in notes) / len(notes) ** 0.5
    pad += seg * w
    # cordes aiguës en trémolo (la tension), sur l'écran de droite et l'offre
    if 14.5 <= t0 < 36.5 or 48.3 <= t0 < 60.7:
        top = max(notes) + 12
        strings += pad_note(midi(top), 5000, a, b) * w + 0.6 * pad_note(midi(top - 5), 5000, a, b) * w
strings *= 0.6 + 0.4 * np.sin(2 * np.pi * 7.5 * T)
strings *= env_curve([(0, 0), (14.5, 0), (16.5, 0.5), (36.3, 0.6), (36.5, 0), (48.3, 0), (50.0, 0.5), (60.5, 0.7), (60.8, 0)])
# respiration lente de la nappe
pad *= 0.85 + 0.15 * np.sin(2 * np.pi * T / 4.8)
pad *= env_curve([(0, 0.0), (1.2, 0.55), (14.4, 0.6), (14.8, 0.9), (36.3, 0.9), (36.6, 0.7), (40.5, 1.0),
                  (41.6, 1.0), (41.9, 0.7), (48.2, 0.75), (48.5, 0.9), (60.6, 1.0), (61.4, 1.0), (DUR - 1.4, 0.8), (DUR, 0)])

# Pulsation de basse en croches (la tension), avec ses arrêts aux moments clés
pulse = np.zeros(N)
root_at = lambda tt: next(m for (t0, m) in reversed([(c[0], c[1][0]) for c in CHORDS]) if t0 <= tt)
on_windows = [(0.0, 36.45, EIGHTH), (41.7, 48.3, BEAT), (48.3, 60.7, EIGHTH)]
L = int(0.32 * SR)
tl = np.arange(L) / SR
for a, b, step in on_windows:
    k = 0
    tt = a
    while tt < b:
        f = midi(root_at(tt) - 12)
        acc = 1.0 if k % 2 == 0 else 0.62
        note = (np.sin(2 * np.pi * f * tl) + 0.45 * np.sin(2 * np.pi * 2 * f * tl) + 0.12 * np.sin(2 * np.pi * 3 * f * tl))
        note *= np.exp(-tl / 0.16) * np.minimum(1, tl / 0.004) * acc
        s = int(tt * SR)
        e = min(N, s + L)
        pulse[s:e] += note[: e - s]
        k += 1
        tt += step
pulse *= env_curve([(0, 0.0), (0.6, 0.45), (14.4, 0.5), (14.6, 0.8), (36.4, 0.85), (36.5, 0), (41.7, 0), (41.8, 0.6),
                    (48.2, 0.6), (48.4, 0.7), (60.5, 1.0), (60.7, 0)])

# Tic discret sur les contretemps (le temps qui passe), seulement sur l'écran de droite et l'offre
hat = np.zeros(N)
hp = butter(2, 6000, "highpass", fs=SR, output="sos")
burst = sosfilt(hp, rng.standard_normal(int(0.03 * SR))) * np.exp(-np.arange(int(0.03 * SR)) / SR / 0.006)
for a, b in [(14.5, 36.4), (48.3, 60.6)]:
    tt = a + EIGHTH
    while tt < b:
        s = int(tt * SR)
        hat[s:s + len(burst)] += burst
        tt += BEAT

# Réverbération : réponse impulsionnelle synthétique (2,4 s), stéréo
ir_len = int(2.4 * SR)
ti = np.arange(ir_len) / SR
lp = butter(1, 5000, "lowpass", fs=SR, output="sos")
irL = sosfilt(lp, rng.standard_normal(ir_len)) * np.exp(-ti / 0.55)
irR = sosfilt(lp, rng.standard_normal(ir_len)) * np.exp(-ti / 0.55)
dry = 0.55 * pad + 0.5 * pulse + 0.1 * hat + 0.22 * strings
wetL = fftconvolve(0.6 * pad + 0.15 * pulse + 0.1 * hat + 0.35 * strings, irL)[:N]
wetR = fftconvolve(0.6 * pad + 0.15 * pulse + 0.1 * hat + 0.35 * strings, irR)[:N]
wetL /= np.abs(wetL).max()
wetR /= np.abs(wetR).max()
mix = np.stack([dry / np.abs(dry).max() + 0.35 * wetL, dry / np.abs(dry).max() + 0.35 * wetR], 1)
hp_sub = butter(2, 28, "highpass", fs=SR, output="sos")
mix = sosfilt(hp_sub, mix, axis=0)
save(A / "music" / "suspense-raw.wav", mix, 0.8)
print("ok")
