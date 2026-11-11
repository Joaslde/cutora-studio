# Exporte un montage Cutora Studio en projet modifiable : CapCut, DaVinci Resolve, Premiere Pro, Final Cut Pro.
# Usage : python export_projet.py <build/plan.json> <dossier de sortie> [--workers 1] [--leger]
#   Lit le plan du modèle de montage et le projet HyperFrames déjà construit (build.py), puis écrit :
#     01-video-fond.mp4          fond et caméra, déjà coupés (la base de la timeline)
#     02-graphismes.mov          toutes les animations, fond transparent (ProRes 4444)
#     03-sous-titres.mov         les sous-titres animés, fond transparent (ProRes 4444)
#     sous-titres.srt            les sous-titres en texte, modifiables partout
#     audio/                     voix, musique (volume et fondu appliqués), bruitages (un fichier par son + une piste)
#     montage-premiere-davinci.xml   timeline pour Premiere Pro et DaVinci Resolve
#     montage-finalcut.fcpxml    timeline pour Final Cut Pro
#     montage.otio               timeline OpenTimelineIO (DaVinci Resolve, autres logiciels)
#     LISEZ-MOI.txt              comment ouvrir le projet dans chaque logiciel, CapCut compris
#   --leger : ajoute des versions WebM transparentes, beaucoup plus légères (pour CapCut si le ProRes est trop lourd).
# Besoin : ffmpeg, npx hyperframes, python -m pip install opentimelineio otio-fcp-adapter otio-fcpx-xml-adapter
import json, re, shutil, subprocess, sys
from pathlib import Path

args = [a for a in sys.argv[1:] if not a.startswith("--")]
PLAN_F, OUT = Path(args[0]).resolve(), Path(args[1]).resolve()
WORKERS = sys.argv[sys.argv.index("--workers") + 1] if "--workers" in sys.argv else "1"
LEGER = "--leger" in sys.argv
PLAN = json.loads(PLAN_F.read_text(encoding="utf-8"))
PROJ = (PLAN_F.parent / PLAN.get("projet", "../montage")).resolve()
W, H, TOTAL = PLAN.get("largeur", 1080), PLAN.get("hauteur", 1920), float(PLAN["duree"])
FPS = int(PLAN.get("fps", 30))

# ---------- 0. Estimation du temps, d'après la machine (--estimer : estime et s'arrête) ----------
def estimer():
    """Secondes de calcul par seconde de vidéo et par calque, mesurées sur un PC de 4 coeurs et 8 Go (1 processus) :
    environ 15 s. Plus de mémoire permet plusieurs processus en parallèle, plus de coeurs accélèrent chacun.
    Une vitesse mesurée lors d'un export précédent (~/cutora-studio.json, "vitesse_export") prime sur le calcul."""
    import os, json as js
    try:
        conf = js.loads((Path.home() / "cutora-studio.json").read_text(encoding="utf-8"))
        if conf.get("vitesse_export"):
            return float(conf["vitesse_export"]), "mesurée lors d'un export précédent"
    except Exception:
        pass
    coeurs = os.cpu_count() or 4
    try:
        import ctypes
        class M(ctypes.Structure):
            _fields_ = [("l", ctypes.c_ulong), ("c", ctypes.c_ulong), ("tot", ctypes.c_ulonglong), ("av", ctypes.c_ulonglong),
                        ("a", ctypes.c_ulonglong), ("b", ctypes.c_ulonglong), ("d", ctypes.c_ulonglong), ("e", ctypes.c_ulonglong), ("f", ctypes.c_ulonglong)]
        m = M(); m.l = ctypes.sizeof(M); ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
        go = m.tot / 2**30
    except Exception:
        go = 8
    proc = 1 if go < 12 else (2 if go < 24 else 4)
    return 15 * 8 / max(4, min(coeurs, 16)) / proc, f"{coeurs} coeurs, {go:.0f} Go de mémoire, {proc} rendu(s) en parallèle"

vitesse, base = estimer()
nb_calques = 2 + (1 if "captions-host" in (PROJ / "index.html").read_text(encoding="utf-8") else 0)
duree_est = vitesse * TOTAL * nb_calques * 1.1
poids_est = TOTAL * (14 if W * H >= 1920 * 1080 else 10) / 1000  # Go, surtout le ProRes des animations
print(f"Estimation : environ {duree_est / 60:.0f} min de calcul ({base}), environ {poids_est:.1f} Go sur le disque.")
if "--estimer" in sys.argv:
    sys.exit(0)
import time
T0 = time.time()

OUT.mkdir(parents=True, exist_ok=True)
(OUT / "audio").mkdir(exist_ok=True)

def run(cmd, **k):
    r = subprocess.run(cmd, capture_output=True, text=True, **k)
    if r.returncode:
        sys.exit(f"Échec : {' '.join(map(str, cmd))[:200]}\n{r.stderr[-1500:]}")
    return r

# ---------- 1. Les trois calques vidéo, rendus par HyperFrames ----------
INDEX = (PROJ / "index.html").read_text(encoding="utf-8")
LIGNES = INDEX.split("\n")
def calque(nom, garder):
    """Écrit une variante de index.html qui ne garde qu'une partie des éléments."""
    out = []
    for l in LIGNES:
        if 'id="camclip"' in l and "camera" not in garder: continue
        if "scene-host" in l and "scenes" not in garder: continue
        if "captions-host" in l and "sous-titres" not in garder: continue
        if "<audio" in l: continue
        out.append(l)
    s = "\n".join(out)
    if "fond" not in garder:  # fond transparent
        s = re.sub(r"background: (#[0-9A-Fa-f]{3,8})", r"background: transparent", s)
    f = PROJ / f"calque-{nom}.html"
    f.write_text(s, encoding="utf-8")
    return f.name

NPX = shutil.which("npx") or "npx"
def rendre(fichier, sortie, fmt):
    if "--sans-rendu" in sys.argv and sortie.exists():  # refaire seulement les timelines et les sons
        return
    print("rendu :", sortie.name, flush=True)
    run([NPX, "--yes", "hyperframes", "render", "-c", fichier, "--format", fmt, "-w", WORKERS, "-o", str(sortie), "--quiet"],
        cwd=PROJ, shell=(sys.platform == "win32"))

a_soustitres = 'captions-host' in INDEX
rendre(calque("fond", {"fond", "camera"}), OUT / "01-video-fond.mp4", "mp4")
rendre(calque("graphismes", {"scenes"}), OUT / "02-graphismes.mov", "mov")
if a_soustitres:
    rendre(calque("sous-titres", {"sous-titres"}), OUT / "03-sous-titres.mov", "mov")
for f in PROJ.glob("calque-*.html"):
    f.unlink()

if LEGER:  # copies WebM VP9 transparentes, 10 à 20 fois plus légères que le ProRes
    for src in [OUT / "02-graphismes.mov", OUT / "03-sous-titres.mov"]:
        if src.exists():
            run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-b:v", "0",
                 "-crf", "32", "-row-mt", "1", "-auto-alt-ref", "0", str(src.with_suffix(".webm"))])

# ---------- 2. Les sons, chacun dans son fichier, prêts à poser ----------
def src(p):
    return (PROJ / p).resolve()

pistes_audio = []  # (piste, nom de fichier, début dans la vidéo, durée)
if PLAN.get("voix"):
    run(["ffmpeg", "-v", "error", "-y", "-i", str(src(PLAN["voix"])), "-t", str(TOTAL), "-ar", "48000", str(OUT / "audio" / "voix.wav")])
    pistes_audio.append(("Voix", "audio/voix.wav", 0.0, TOTAL))
mu = PLAN.get("musique")
if mu:
    vol, fondu = mu.get("volume", 0.2), mu.get("fondu", 1.2)
    run(["ffmpeg", "-v", "error", "-y", "-i", str(src(mu["src"])), "-t", str(TOTAL), "-af",
         f"volume={vol},afade=t=out:st={max(0, TOTAL - fondu)}:d={fondu}", "-ar", "48000", str(OUT / "audio" / "musique.wav")])
    pistes_audio.append(("Musique", "audio/musique.wav", 0.0, TOTAL))
sfx = PLAN.get("sfx", [])
if sfx:
    (OUT / "audio" / "bruitages").mkdir(exist_ok=True)
    entrees, filtres = [], []
    for i, fx in enumerate(sfx):
        nom = f"audio/bruitages/{i + 1:02d}-{Path(fx['src']).stem}.wav"
        d = float(fx.get("duree", 1.5))
        run(["ffmpeg", "-v", "error", "-y", "-i", str(src(fx["src"])), "-t", str(d), "-af", f"volume={fx.get('volume', 0.4)}",
             "-ar", "48000", "-ac", "2", str(OUT / nom)])
        d = min(d, float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(OUT / nom)]).stdout.strip() or d))
        pistes_audio.append(("Bruitages", nom, float(fx["t"]), d))
        entrees += ["-i", str(OUT / nom)]
        filtres.append(f"[{i}:a]adelay={int(float(fx['t']) * 1000)}|{int(float(fx['t']) * 1000)}[f{i}]")
    # la même chose en une seule piste, pour CapCut
    run(["ffmpeg", "-v", "error", "-y", *entrees, "-filter_complex",
         ";".join(filtres) + ";" + "".join(f"[f{i}]" for i in range(len(sfx))) + f"amix=inputs={len(sfx)}:normalize=0,apad=whole_dur={TOTAL}",
         "-t", str(TOTAL), "-ar", "48000", str(OUT / "audio" / "bruitages-piste-complete.wav")])

# ---------- 3. Sous-titres en texte (SRT) ----------
def tc(t):
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"
if PLAN.get("mots"):
    mots = json.loads((PLAN_F.parent / PLAN["mots"]).resolve().read_text(encoding="utf-8"))
    mots = [(w.get("text", w.get("texte", "")).strip(), float(w.get("start", w.get("debut"))), float(w.get("end", w.get("fin"))))
            for w in mots if (w.get("text") or w.get("texte", "")).strip()]
    blocs, cur = [], []
    for i, m in enumerate(mots):  # une ligne par phrase courte : coupure sur une pause ou au 7e mot
        cur.append(m)
        pause = i + 1 < len(mots) and mots[i + 1][1] - m[2] > 0.35
        if len(cur) >= 7 or pause or i == len(mots) - 1:
            blocs.append(cur); cur = []
    (OUT / "sous-titres.srt").write_text("\n".join(
        f"{k + 1}\n{tc(b[0][1])} --> {tc(b[-1][2])}\n{' '.join(x[0] for x in b)}\n" for k, b in enumerate(blocs)), encoding="utf-8")

# ---------- 4. Les timelines (Premiere, DaVinci, Final Cut) ----------
import opentimelineio as otio

def rt(s):
    return otio.opentime.RationalTime(round(s * FPS), FPS)
def tr(debut, duree):
    return otio.opentime.TimeRange(rt(debut), rt(duree))
def media(nom, duree):
    ref = otio.schema.ExternalReference(target_url=(OUT / nom).as_uri(), available_range=tr(0, duree))
    return ref

tl = otio.schema.Timeline(name=PLAN_F.parent.parent.name or "Montage Cutora Studio")
tl.global_start_time = rt(0)

def piste(nom, kind, morceaux):
    """morceaux : (fichier, début dans la vidéo, entrée dans le fichier, durée). Les trous sont comblés."""
    t = otio.schema.Track(name=nom, kind=kind)
    curseur = 0.0
    for fichier, debut, entree, duree, dmedia in sorted(morceaux, key=lambda m: m[1]):
        if debut > curseur + 1e-3:
            t.append(otio.schema.Gap(source_range=tr(0, debut - curseur)))
        t.append(otio.schema.Clip(name=Path(fichier).stem, media_reference=media(fichier, dmedia), source_range=tr(entree, duree)))
        curseur = debut + duree
    return t

# Vidéo de fond découpée aux changements de scène (et aux coupes du dérush si le plan les donne) : des blocs déplaçables
bornes = sorted({0.0, TOTAL, *[float(s["debut"]) for s in PLAN["scenes"]], *[float(c) for c in PLAN.get("coupes", [])]})
bornes = [b for b in bornes if 0 <= b <= TOTAL]
v1 = [("01-video-fond.mp4", a, a, b - a, TOTAL) for a, b in zip(bornes, bornes[1:]) if b - a > 0.02]
v2 = [("02-graphismes.mov", float(s["debut"]), float(s["debut"]), float(s["fin"]) - float(s["debut"]), TOTAL)
      for s in PLAN["scenes"] if s.get("titre") or s.get("motion") or s.get("media")]
tl.tracks.append(piste("Fond et caméra", otio.schema.TrackKind.Video, v1))
tl.tracks.append(piste("Graphismes", otio.schema.TrackKind.Video, v2))
if a_soustitres:
    tl.tracks.append(piste("Sous-titres", otio.schema.TrackKind.Video, [("03-sous-titres.mov", 0.0, 0.0, TOTAL, TOTAL)]))
for nom_piste in ["Voix", "Musique", "Bruitages"]:
    m = [(f, d, 0.0, du, du) for p, f, d, du in pistes_audio if p == nom_piste]
    if m:
        tl.tracks.append(piste(nom_piste, otio.schema.TrackKind.Audio, m))

otio.adapters.write_to_file(tl, str(OUT / "montage.otio"))
# Premiere et DaVinci : la taille de l'image (sinon la séquence s'ouvre en 1920 x 1080 par défaut)
xml = otio.adapters.write_to_string(tl, adapter_name="fcp_xml")
fmt = (f"<format><samplecharacteristics><rate><timebase>{FPS}</timebase><ntsc>FALSE</ntsc></rate>"
       f"<width>{W}</width><height>{H}</height><pixelaspectratio>square</pixelaspectratio>"
       f"<fielddominance>none</fielddominance></samplecharacteristics></format>")
xml = xml.replace("<format/>", fmt, 1)
(OUT / "montage-premiere-davinci.xml").write_text(xml, encoding="utf-8")
try:
    fx = otio.adapters.write_to_string(tl, adapter_name="fcpx_xml")
    fx = re.sub(r'<format id="r1" frameDuration="([^"]+)" name=""\s*/>',
                rf'<format id="r1" frameDuration="\1" width="{W}" height="{H}" name="FFVideoFormat{W}x{H}p{FPS}"/>', fx, count=1)
    (OUT / "montage-finalcut.fcpxml").write_text(fx, encoding="utf-8")
except Exception as e:  # le format Final Cut est plus strict : on le signale sans bloquer le reste
    print("Final Cut : timeline non écrite :", e)

# ---------- 5. Projet CapCut (s'ouvre directement depuis la liste des projets de CapCut) ----------
capcut_ok = False
if "--sans-capcut" not in sys.argv:
    try:
        import os
        import pycapcut as cc
        from pycapcut import trange_seconds as ts
        racine = Path(os.environ.get("LOCALAPPDATA", "")) / "CapCut" / "User Data" / "Projects" / "com.lveditor.draft"
        if not racine.exists():  # macOS
            racine = Path.home() / "Movies" / "CapCut" / "User Data" / "Projects" / "com.lveditor.draft"
        if racine.exists():
            nom = f"Cutora - {tl.name}"
            s = cc.DraftFolder(str(racine)).create_draft(nom, W, H, FPS, allow_replace=True)
            s.add_track(cc.TrackType.video, "Fond et caméra")
            s.add_track(cc.TrackType.video, "Graphismes", relative_index=1)
            if a_soustitres:
                s.add_track(cc.TrackType.video, "Sous-titres", relative_index=2)
            for k, p in enumerate(["Voix", "Musique", "Bruitages"]):
                s.add_track(cc.TrackType.audio, p, relative_index=k)
            for f, d, e, du, _ in v1:
                s.add_segment(cc.VideoSegment(str(OUT / f), ts(d, duration=du), source_timerange=ts(e, duration=du)), "Fond et caméra")
            gfx = cc.VideoMaterial(str(OUT / "02-graphismes.mov"))
            for f, d, e, du, _ in v2:
                s.add_segment(cc.VideoSegment(gfx, ts(d, duration=du), source_timerange=ts(e, duration=du)), "Graphismes")
            if a_soustitres:
                s.add_segment(cc.VideoSegment(str(OUT / "03-sous-titres.mov"), ts(0, duration=TOTAL)), "Sous-titres")
            for p, f, d, du in pistes_audio:
                s.add_segment(cc.AudioSegment(str(OUT / f), ts(d, duration=du)), p)
            s.save()
            capcut_ok = True
            print("Projet CapCut créé :", nom, "(ferme et rouvre CapCut pour le voir)")
    except ImportError:
        print("CapCut : module pycapcut absent, seul le pack à poser à la main est livré")
    except Exception as e:
        print("CapCut : projet non créé :", e)

# ---------- 6. Le mode d'emploi ----------
(OUT / "LISEZ-MOI.txt").write_text(f"""PROJET MODIFIABLE (Cutora Studio)
Format : {W} x {H}, {FPS} images/s, {TOTAL:.2f} s. Garde ce dossier entier : les fichiers de projet pointent vers les fichiers qui sont dedans.

CAPCUT
{"Le projet est déjà dans ta liste de projets CapCut : ferme et rouvre CapCut, puis ouvre « Cutora - " + tl.name + " »." if capcut_ok else ""}
Sinon, à la main :
1. Nouveau projet, puis importe tous les fichiers de ce dossier (vidéos, sons, sous-titres).
2. Pose-les tous au tout début de la timeline (à 0:00), dans cet ordre, de bas en haut :
   01-video-fond.mp4, puis 02-graphismes.mov au-dessus, puis 03-sous-titres.mov au-dessus.
   Sons : audio/voix.wav, audio/musique.wav, audio/bruitages-piste-complete.wav.
3. Le montage est reconstitué. Tu peux couper, déplacer, supprimer une animation, changer la musique.
   Pour modifier le texte des sous-titres : supprime 03-sous-titres.mov et importe sous-titres.srt
   (Texte, puis Sous-titres locaux, ou glisse le fichier .srt dans la timeline).
   Si CapCut refuse un fichier .mov ou le lit sans transparence, utilise les versions .webm (export avec --leger).

DAVINCI RESOLVE
Fichier, puis Importer, puis Timeline : choisis montage.otio (ou montage-premiere-davinci.xml).
Si DaVinci demande où sont les médias, montre-lui ce dossier.

PREMIERE PRO
Fichier, puis Importer : choisis montage-premiere-davinci.xml. Une séquence s'ouvre avec toutes les pistes.
Sous-titres en texte : Fichier, puis Importer, sous-titres.srt.

FINAL CUT PRO
Fichier, puis Importer, puis XML : choisis montage-finalcut.fcpxml.

CE QUI SE MODIFIE
- Les coupes, l'ordre, la durée des blocs ; chaque animation (bloc de la piste Graphismes) se déplace ou se supprime ;
  le texte des sous-titres (fichier .srt) ; la musique, les bruitages, les volumes ; l'étalonnage.
- Le texte à l'intérieur d'une animation (un titre animé) ne se modifie pas : c'est une vidéo. Pour le changer, masque
  ce bloc et ajoute ton propre titre, ou demande la modification à Claude.
""", encoding="utf-8")

if "--sans-rendu" not in sys.argv:  # retenir la vraie vitesse de cette machine pour les prochaines estimations
    try:
        cf = Path.home() / "cutora-studio.json"
        conf = json.loads(cf.read_text(encoding="utf-8")) if cf.exists() else {}
        conf["vitesse_export"] = round((time.time() - T0) / (TOTAL * nb_calques), 1)
        cf.write_text(json.dumps(conf, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass
print(f"Durée réelle : {(time.time() - T0) / 60:.0f} min")
poids = sum(f.stat().st_size for f in OUT.rglob("*") if f.is_file()) / 1e6
print(f"Projet modifiable prêt : {OUT} ({poids:.0f} Mo)")
