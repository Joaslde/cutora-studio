# Exporte un montage Cutora Studio en projet modifiable pour UN logiciel de montage : celui que la personne utilise.
# Usage : python export_projet.py <build/plan.json> <dossier de sortie> --logiciel premiere|davinci|finalcut|capcut
#         [--workers 1] [--estimer] [--sans-rendu]
#
# Ce qui est livré (exemple pour Premiere Pro) :
#   <Nom> - OUVRIR DANS PREMIERE.xml   le seul fichier à ouvrir : toutes les pistes déjà placées
#   LISEZ-MOI.txt                      comment l'ouvrir et l'enregistrer en projet (.prproj), en 4 étapes
#   Medias/                            tout ce que le projet utilise, rangé (ne pas déplacer ni renommer)
#     video-fond.mp4                   fond et caméra, découpés en blocs sur la timeline
#     animations/                      un fichier par animation, seulement le temps où elle est à l'écran
#     sous-titres/                     un fichier par sous-titre, plus sous-titres.srt (texte modifiable)
#     audio/                           voix, musique, un fichier par bruitage
#
# Pourquoi c'est léger : les animations et les sous-titres ne sont plus rendus sur toute la durée de la vidéo
# (89 % d'image vide), mais seulement aux moments où ils apparaissent, et dans un format transparent compressé
# (QuickTime Animation pour Premiere, ProRes 4444 pour les autres). Les passages opaques (B-roll plein cadre)
# sont en H.264.
# Besoin : ffmpeg, npx hyperframes, pillow, opentimelineio, otio-fcp-adapter, otio-fcpx-xml-adapter (pycapcut pour CapCut)
import json, os, re, shutil, subprocess, sys, time
from pathlib import Path

args, _i = [], 1
while _i < len(sys.argv):  # positionnels : tout ce qui n'est ni une option ni la valeur d'une option
    if sys.argv[_i] in ("--workers", "--logiciel"):
        _i += 2
        continue
    if not sys.argv[_i].startswith("--"):
        args.append(sys.argv[_i])
    _i += 1
PLAN_F, OUT = Path(args[0]).resolve(), Path(args[1]).resolve()
WORKERS = sys.argv[sys.argv.index("--workers") + 1] if "--workers" in sys.argv else "1"
LOGICIEL = (sys.argv[sys.argv.index("--logiciel") + 1] if "--logiciel" in sys.argv else "").lower()
NOMS = {"premiere": "PREMIERE", "davinci": "DAVINCI", "finalcut": "FINAL CUT", "capcut": "CAPCUT"}
if LOGICIEL not in NOMS:
    sys.exit("Précise le logiciel de la personne : --logiciel premiere, davinci, finalcut ou capcut "
             "(demande-lui lequel elle utilise, et n'exporte que celui-là).")
PLAN = json.loads(PLAN_F.read_text(encoding="utf-8"))
PROJ = (PLAN_F.parent / PLAN.get("projet", "../montage")).resolve()
W, H, TOTAL = PLAN.get("largeur", 1080), PLAN.get("hauteur", 1920), float(PLAN["duree"])
FPS = int(PLAN.get("fps", 30))
NOM = PLAN.get("nom") or PLAN_F.parent.parent.name or "Montage Cutora Studio"
MED = OUT / "Medias"


# ---------- 0. Estimation du temps, d'après la machine (--estimer : estime et s'arrête) ----------
def estimer():
    """Secondes de calcul par seconde de vidéo et par calque, mesurées sur un PC de 4 coeurs et 8 Go (1 processus) :
    environ 15 s. Une vitesse mesurée lors d'un export précédent (~/cutora-studio.json, "vitesse_export") prime."""
    try:
        conf = json.loads((Path.home() / "cutora-studio.json").read_text(encoding="utf-8"))
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

INDEX = (PROJ / "index.html").read_text(encoding="utf-8")
A_SOUSTITRES = "captions-host" in INDEX
vitesse, base = estimer()
nb_calques = 2 + (1 if A_SOUSTITRES else 0)
duree_est = vitesse * TOTAL * nb_calques * 1.1
poids_est = TOTAL / 60 * 0.25  # Go : environ 250 Mo par minute de vidéo (fond, animations, sons)
temp_est = TOTAL / 60 * 0.6    # Go : images temporaires pendant le calcul, effacées à la fin
print(f"Estimation : environ {duree_est / 60:.0f} min de calcul ({base}). "
      f"Poids final environ {max(poids_est, 0.05):.1f} Go ; il faut environ {poids_est + temp_est:.1f} Go libres pendant le calcul.")
if "--estimer" in sys.argv:
    sys.exit(0)
T0 = time.time()

for d in (MED / "animations", MED / "sous-titres", MED / "audio"):
    d.mkdir(parents=True, exist_ok=True)


def run(cmd, **k):
    r = subprocess.run(cmd, capture_output=True, text=True, **k)
    if r.returncode:
        sys.exit(f"Échec : {' '.join(map(str, cmd))[:200]}\n{r.stderr[-1500:]}")
    return r


# ---------- 1. Les calques vidéo, rendus par HyperFrames ----------
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
    print("rendu :", sortie.name, flush=True)
    run([NPX, "--yes", "hyperframes", "render", "-c", fichier, "--format", fmt, "-w", WORKERS, "-o", str(sortie), "--quiet"],
        cwd=PROJ, shell=(sys.platform == "win32"))

FOND = MED / "video-fond.mp4"
if not ("--sans-rendu" in sys.argv and FOND.exists()):
    rendre(calque("fond", {"fond", "camera"}), FOND, "mp4")


def morceaux(dossier_png, coupures):
    """Repère, image par image, les passages où le calque montre quelque chose (pixels non transparents).
    Renvoie [(première image, dernière image exclue, opaque?)], coupés aussi aux changements de scène."""
    from PIL import Image
    images = sorted(dossier_png.glob("*.png"))
    plein, opaque = [], []
    for f in images:
        im = Image.open(f)
        if "A" not in im.getbands():  # image enregistrée sans transparence : entièrement opaque
            plein.append(True); opaque.append(True)
            continue
        bas, haut = im.getchannel("A").getextrema()
        plein.append(haut > 8)  # quelques pixels presque invisibles ne comptent pas
        opaque.append(bas == 255)
    bornes = {round(c * FPS) for c in coupures}
    runs, i, n = [], 0, len(images)
    while i < n:
        if not plein[i]:
            i += 1
            continue
        j = i + 1
        while j < n and j not in bornes and (plein[j] or (j + 4 < n and any(plein[j:j + 5]))):
            j += 1  # un trou de moins de 5 images (une demi-seconde à 10 i/s près) ne coupe pas le passage
        runs.append((i, j, all(opaque[i:j])))
        i = j
    return images, [r for r in runs if r[1] - r[0] >= 3]


CODEC_ALPHA = {"premiere": ["-c:v", "qtrle", "-pix_fmt", "argb"]}.get(
    LOGICIEL, ["-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", "yuva444p10le", "-vendor", "apl0"])

def decouper(calque_nom, garder, dossier, prefixe, coupures, noms):
    """Rend un calque en images PNG transparentes, puis écrit un petit fichier vidéo par passage visible."""
    tmp = OUT / f".images-{calque_nom}"
    if "--sans-rendu" in sys.argv and any(dossier.iterdir()):
        return [json.loads(l) for l in (dossier / ".liste.jsonl").read_text(encoding="utf-8").splitlines()]
    deja = len(list(tmp.glob("*.png"))) if tmp.exists() else 0
    if deja < round(TOTAL * FPS) - 2:  # images d'une tentative précédente réutilisées si elles sont complètes
        shutil.rmtree(tmp, ignore_errors=True)
        rendre(calque(calque_nom, garder), tmp, "png-sequence")
    images, runs = morceaux(tmp, coupures)
    clips = []
    for k, (a, b, opaque) in enumerate(runs, 1):
        nom = f"{k:03d}-{noms(a / FPS, b / FPS)}"
        liste = tmp / "liste.txt"
        liste.write_text("".join(f"file '{images[x].as_posix()}'\nduration {1 / FPS:.6f}\n" for x in range(a, b)), encoding="utf-8")
        if opaque:  # passage plein cadre (B-roll, écran de motion) : pas besoin de transparence
            f = dossier / f"{nom}.mp4"
            run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(liste), "-r", str(FPS),
                 "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", str(f)])
        else:
            f = dossier / f"{nom}.mov"
            run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(liste), "-r", str(FPS), *CODEC_ALPHA, str(f)])
        clips.append({"fichier": f.relative_to(OUT).as_posix(), "debut": a / FPS, "duree": (b - a) / FPS, "nom": f.stem})
    shutil.rmtree(tmp, ignore_errors=True)
    (dossier / ".liste.jsonl").write_text("\n".join(json.dumps(c, ensure_ascii=False) for c in clips), encoding="utf-8")
    return clips


def court(texte, n=4):
    import unicodedata
    texte = unicodedata.normalize("NFKD", texte).encode("ascii", "ignore").decode()
    return re.sub(r"[^\w-]+", "-", " ".join(texte.split()[:n]), flags=re.U).strip("-")[:40] or "element"

SCENES = PLAN["scenes"]
def nom_scene(debut, fin):
    s = next((s for s in SCENES if float(s["debut"]) <= debut + 0.05 < float(s["fin"])), {})
    t = s.get("titre") or {}
    txt = " ".join(x for x in (t.get("faible"), t.get("fort"), t.get("cle")) if x) or (s.get("motion") or {}).get("type") or s.get("page", "")
    return court(f"{s.get('id', '')} {txt}")

MOTS = []
if PLAN.get("mots"):
    MOTS = json.loads((PLAN_F.parent / PLAN["mots"]).resolve().read_text(encoding="utf-8"))
    MOTS = [(w.get("text", w.get("texte", "")).strip(), float(w.get("start", w.get("debut"))), float(w.get("end", w.get("fin"))))
            for w in MOTS if (w.get("text") or w.get("texte", "")).strip()]
BLOCS, _cur = [], []
for _i, _m in enumerate(MOTS):  # une ligne par phrase courte : coupure sur une pause ou au 7e mot
    _cur.append(_m)
    _pause = _i + 1 < len(MOTS) and MOTS[_i + 1][1] - _m[2] > 0.35
    if len(_cur) >= 7 or _pause or _i == len(MOTS) - 1:
        BLOCS.append(_cur); _cur = []

def nom_sous_titre(debut, fin):
    return court(" ".join(m[0] for m in MOTS if debut - 0.05 <= m[1] < fin) or "sous-titre")

coupes = [float(s["debut"]) for s in SCENES]
ANIMS = decouper("graphismes", {"scenes"}, MED / "animations", "animation", coupes, nom_scene)
# Les groupes réellement affichés par la vidéo (écrits par build.py), sinon les phrases du SRT
_cap = PROJ / "compositions" / "captions.html"
GROUPES = [float(x) for x in re.findall(r'\{"debut": ([\d.]+), "fin": [\d.]+, "mots"', _cap.read_text(encoding="utf-8"))] if _cap.exists() else []
SOUS = decouper("sous-titres", {"sous-titres"}, MED / "sous-titres", "sous-titre", GROUPES or [b[0][1] for b in BLOCS], nom_sous_titre) if A_SOUSTITRES else []
for f in PROJ.glob("calque-*.html"):
    f.unlink()


# ---------- 2. Les sons, chacun dans son fichier, prêts à poser ----------
def src(p):
    return (PROJ / p).resolve()

pistes_audio = []  # (piste, fichier relatif, début dans la vidéo, durée, nom)
if PLAN.get("voix"):
    run(["ffmpeg", "-v", "error", "-y", "-i", str(src(PLAN["voix"])), "-t", str(TOTAL), "-ar", "48000", str(MED / "audio" / "voix.wav")])
    pistes_audio.append(("Voix", "Medias/audio/voix.wav", 0.0, TOTAL, "Voix"))
mu = PLAN.get("musique")
if mu:
    vol, fondu = mu.get("volume", 0.3), mu.get("fondu", 1.2)
    run(["ffmpeg", "-v", "error", "-y", "-i", str(src(mu["src"])), "-t", str(TOTAL), "-af",
         f"volume={vol},afade=t=out:st={max(0, TOTAL - fondu)}:d={fondu}", "-ar", "48000", "-ac", "2", str(MED / "audio" / "musique.wav")])
    pistes_audio.append(("Musique", "Medias/audio/musique.wav", 0.0, TOTAL, "Musique"))
sfx = PLAN.get("sfx", [])
if sfx:
    (MED / "audio" / "bruitages").mkdir(exist_ok=True)
    for i, fx in enumerate(sfx):
        nom = f"Medias/audio/bruitages/{i + 1:02d}-{Path(fx['src']).stem}.wav"
        d = float(fx.get("duree", 1.5))
        run(["ffmpeg", "-v", "error", "-y", "-i", str(src(fx["src"])), "-t", str(d), "-af", f"volume={fx.get('volume', 0.4)}",
             "-ar", "48000", "-ac", "2", str(OUT / nom)])
        d = min(d, float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(OUT / nom)]).stdout.strip() or d))
        pistes_audio.append(("Bruitages", nom, float(fx["t"]), d, f"Bruitage {Path(fx['src']).stem}"))


# ---------- 3. Sous-titres en texte (SRT), modifiables dans tous les logiciels ----------
def tc(t):
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"
if MOTS:
    blocs = BLOCS
    (MED / "sous-titres" / "sous-titres.srt").write_text("\n".join(
        f"{k + 1}\n{tc(b[0][1])} --> {tc(b[-1][2])}\n{' '.join(x[0] for x in b)}\n" for k, b in enumerate(blocs)), encoding="utf-8")


# ---------- 4. La timeline du logiciel choisi ----------
bornes = sorted({0.0, TOTAL, *coupes, *[float(c) for c in PLAN.get("coupes", [])]})
bornes = [b for b in bornes if 0 <= b <= TOTAL]
V1 = [("Medias/video-fond.mp4", a, a, b - a, TOTAL, f"Fond {k:02d}") for k, (a, b) in enumerate(zip(bornes, bornes[1:]), 1) if b - a > 0.02]
V2 = [(c["fichier"], c["debut"], 0.0, c["duree"], c["duree"], c["nom"]) for c in ANIMS]
V3 = [(c["fichier"], c["debut"], 0.0, c["duree"], c["duree"], c["nom"]) for c in SOUS]
AUD = {p: [(f, d, 0.0, du, du, n) for pp, f, d, du, n in pistes_audio if pp == p] for p in ("Voix", "Musique", "Bruitages")}
ENTREE = None

if LOGICIEL in ("premiere", "davinci", "finalcut"):
    import opentimelineio as otio

    def rt(s):
        return otio.opentime.RationalTime(round(s * FPS), FPS)
    def tr(debut, duree):
        return otio.opentime.TimeRange(rt(debut), rt(duree))

    tl = otio.schema.Timeline(name=NOM)
    tl.global_start_time = rt(0)

    def piste(nom, kind, elements):
        """elements : (fichier, début dans la vidéo, entrée dans le fichier, durée, durée du fichier, nom). Trous comblés."""
        t = otio.schema.Track(name=nom, kind=kind)
        curseur = 0.0
        for fichier, debut, entree, duree, dmedia, nom_clip in sorted(elements, key=lambda m: m[1]):
            debut = max(debut, curseur)  # jamais de chevauchement sur une même piste
            if debut > curseur + 1e-3:
                t.append(otio.schema.Gap(source_range=tr(0, debut - curseur)))
            ref = otio.schema.ExternalReference(target_url=(OUT / fichier).as_uri(), available_range=tr(0, dmedia))
            t.append(otio.schema.Clip(name=nom_clip, media_reference=ref, source_range=tr(entree, duree)))
            curseur = debut + duree
        return t

    def pistes_bruitages():
        """Des bruitages qui se chevauchent vont sur des pistes différentes."""
        libres, out = [], []
        for e in sorted(AUD["Bruitages"], key=lambda m: m[1]):
            k = next((i for i, fin in enumerate(libres) if fin <= e[1] + 1e-3), None)
            if k is None:
                libres.append(0); out.append([]); k = len(libres) - 1
            libres[k] = e[1] + e[3]; out[k].append(e)
        return out

    tl.tracks.append(piste("Fond et caméra", otio.schema.TrackKind.Video, V1))
    if V2: tl.tracks.append(piste("Animations", otio.schema.TrackKind.Video, V2))
    if V3: tl.tracks.append(piste("Sous-titres", otio.schema.TrackKind.Video, V3))
    for p in ("Voix", "Musique"):
        if AUD[p]: tl.tracks.append(piste(p, otio.schema.TrackKind.Audio, AUD[p]))
    for k, b in enumerate(pistes_bruitages(), 1):
        tl.tracks.append(piste(f"Bruitages {k}", otio.schema.TrackKind.Audio, b))

    titre = f"{NOM} - OUVRIR DANS {NOMS[LOGICIEL]}"
    if LOGICIEL == "finalcut":
        fx = otio.adapters.write_to_string(tl, adapter_name="fcpx_xml")
        fx = re.sub(r'<format id="r1" frameDuration="([^"]+)" name=""\s*/>',
                    rf'<format id="r1" frameDuration="\1" width="{W}" height="{H}" name="FFVideoFormat{W}x{H}p{FPS}"/>', fx, count=1)
        ENTREE = OUT / f"{titre}.fcpxml"
        ENTREE.write_text(fx, encoding="utf-8")
    else:
        xml = otio.adapters.write_to_string(tl, adapter_name="fcp_xml")
        fmt = (f"<format><samplecharacteristics><rate><timebase>{FPS}</timebase><ntsc>FALSE</ntsc></rate>"
               f"<width>{W}</width><height>{H}</height><pixelaspectratio>square</pixelaspectratio>"
               f"<fielddominance>none</fielddominance></samplecharacteristics></format>")
        xml = xml.replace("<format/>", fmt, 1)
        # Chemins au format que Premiere écrit lui-même (file://localhost/C%3a/...), le plus sûr à la réouverture
        xml = re.sub(r"file:///([A-Za-z]):/", lambda m: f"file://localhost/{m.group(1)}%3a/", xml)
        ENTREE = OUT / f"{titre}.xml"
        ENTREE.write_text(xml, encoding="utf-8")
        if LOGICIEL == "davinci":
            otio.adapters.write_to_file(tl, str(OUT / f"{titre}.otio"))

capcut_ok = False
if LOGICIEL == "capcut":
    try:
        import pycapcut as cc
        from pycapcut import trange_seconds as ts
        racine = Path(os.environ.get("LOCALAPPDATA", "")) / "CapCut" / "User Data" / "Projects" / "com.lveditor.draft"
        if not racine.exists():  # macOS
            racine = Path.home() / "Movies" / "CapCut" / "User Data" / "Projects" / "com.lveditor.draft"
        if racine.exists():
            nom = f"Cutora - {NOM}"
            s = cc.DraftFolder(str(racine)).create_draft(nom, W, H, FPS, allow_replace=True)
            pistes = [("Fond et caméra", V1), ("Animations", V2), ("Sous-titres", V3)]
            for k, (p, el) in enumerate(pistes):
                if el: s.add_track(cc.TrackType.video, p, relative_index=k)
            for k, p in enumerate(["Voix", "Musique", "Bruitages"]):
                if AUD[p]: s.add_track(cc.TrackType.audio, p, relative_index=k)
            fond = cc.VideoMaterial(str(OUT / V1[0][0]))
            for f, d, e, du, _, _ in V1:
                s.add_segment(cc.VideoSegment(fond, ts(d, duration=du), source_timerange=ts(e, duration=du)), "Fond et caméra")
            for p, el in pistes[1:]:
                for f, d, e, du, _, _ in el:
                    s.add_segment(cc.VideoSegment(str(OUT / f), ts(d, duration=du)), p)
            for p in ("Voix", "Musique", "Bruitages"):
                for f, d, e, du, _, _ in AUD[p]:
                    s.add_segment(cc.AudioSegment(str(OUT / f), ts(d, duration=du)), p)
            s.save()
            capcut_ok = True
            print("Projet CapCut créé :", nom, "(ferme et rouvre CapCut pour le voir)")
        else:
            print("CapCut n'est pas installé sur cet ordinateur : projet CapCut non créé")
    except ImportError:
        print("CapCut : module pycapcut absent (relancer l'installateur)")
    except Exception as e:
        print("CapCut : projet non créé :", e)


# ---------- 5. Le mode d'emploi, seulement pour le logiciel choisi ----------
OUVRIR = {
    "premiere": f"""1. Ouvre Premiere Pro et crée un nouveau projet (ou ouvre le tien).
2. Menu Fichier, puis Importer (Ctrl+I), puis choisis le fichier « {ENTREE.name if ENTREE else ''} ».
   Ne double-clique pas sur ce fichier dans l'Explorateur : il s'ouvrirait dans un navigateur.
3. Une séquence « {NOM} » apparaît dans le panneau Projet : double-clique dessus. Toutes les pistes sont placées :
   fond et caméra, animations, sous-titres, voix, musique, bruitages.
4. Menu Fichier, puis Enregistrer sous : tu obtiens ton fichier de projet Premiere (.prproj), à rouvrir directement
   les fois suivantes.
Sous-titres en texte modifiable : Fichier, Importer, Medias/sous-titres/sous-titres.srt, puis glisse-le sur la
séquence (il devient une piste de sous-titres Premiere, modifiable mot par mot). Masque alors la piste Sous-titres animée.""",
    "davinci": f"""1. Ouvre DaVinci Resolve et un projet.
2. Menu Fichier, Importer, Timeline, puis choisis « {ENTREE.name if ENTREE else ''} » (ou le .otio du même nom).
3. Si DaVinci demande où sont les médias, montre-lui le dossier Medias.
Sous-titres en texte : glisse Medias/sous-titres/sous-titres.srt dans le Media Pool puis sur la timeline.""",
    "finalcut": f"""1. Ouvre Final Cut Pro.
2. Menu Fichier, Importer, XML, puis choisis « {ENTREE.name if ENTREE else ''} ».
Sous-titres en texte : Fichier, Importer, Sous-titres, Medias/sous-titres/sous-titres.srt.""",
    "capcut": ("Le projet est déjà dans ta liste de projets CapCut : ferme et rouvre CapCut, puis ouvre « Cutora - " + NOM + " »."
               if capcut_ok else "CapCut n'a pas été trouvé sur cet ordinateur : installe-le, puis redemande l'export.")
             + "\nSous-titres en texte : Texte, Sous-titres locaux, puis Medias/sous-titres/sous-titres.srt.",
}[LOGICIEL]
(OUT / "LISEZ-MOI.txt").write_text(f"""PROJET MODIFIABLE {NOMS[LOGICIEL]} (Cutora Studio)
{NOM} : {W} x {H}, {FPS} images/s, {TOTAL:.1f} s.

COMMENT L'OUVRIR
{OUVRIR}

IMPORTANT
Garde ce dossier entier et ne renomme rien dans Medias : le projet pointe vers ces fichiers. Pour l'envoyer à
quelqu'un, compresse le dossier entier ; s'il manque des médias à l'ouverture, indique au logiciel le dossier Medias.

CE QUI SE MODIFIE
- Les coupes, l'ordre et la durée des blocs de la caméra.
- Chaque animation est un élément séparé sur la piste Animations : déplacer, raccourcir, supprimer.
- Chaque sous-titre est un élément séparé sur la piste Sous-titres ; le texte se modifie avec le fichier .srt.
- La voix, la musique, chaque bruitage, les volumes ; l'étalonnage.
- Le texte à l'intérieur d'une animation (un titre animé) ne se modifie pas : c'est une vidéo. Pour le changer,
  supprime cet élément et ajoute ton propre titre, ou demande la modification à Claude.
""", encoding="utf-8")

if "--sans-rendu" not in sys.argv:  # retenir la vraie vitesse de cette machine pour les prochaines estimations
    try:
        cf = Path.home() / "cutora-studio.json"
        conf = json.loads(cf.read_text(encoding="utf-8")) if cf.exists() else {}
        conf["vitesse_export"] = round((time.time() - T0) / (TOTAL * nb_calques), 1)
        cf.write_text(json.dumps(conf, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass
poids = sum(f.stat().st_size for f in OUT.rglob("*") if f.is_file()) / 1e6
print(f"Durée réelle : {(time.time() - T0) / 60:.0f} min")
print(f"{len(ANIMS)} animations, {len(SOUS)} sous-titres, {len(AUD['Bruitages'])} bruitages, chacun à sa place.")
print(f"Projet {NOMS[LOGICIEL]} prêt : {OUT} ({poids:.0f} Mo)")
if ENTREE:
    print("Fichier à ouvrir :", ENTREE.name)
