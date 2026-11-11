# Recherche et choix de B-roll libres (Mixkit sans compte, Pexels avec une clé gratuite), en regardant avant de prendre.
#
# 1. Chercher : python broll.py chercher <dossier> "requête 1" "requête 2" ... [--orientation portrait|landscape] [--n 12]
#    Écrit <dossier>/candidats.json et <dossier>/planche-<k>.jpg : chaque candidat numéroté avec son titre.
#    Regarde les planches et choisis ceux qui montrent EXACTEMENT l'idée (voir references/broll-medias.md).
# 2. Prendre : python broll.py prendre <dossier> <projet montage> <n°> [<n°> ...] [--nom broll-03]
#    Télécharge la version HD des candidats choisis dans <montage>/assets/broll/, les note dans <dossier>/deja-utilises.json
#    (jamais deux fois le même plan) et dans <montage>/../CREDITS.md.
# Clé Pexels (gratuite, pexels.com/api) : dans ~/cutora-studio.json, "pexels_cle". Sans clé, Mixkit seul.
import json, re, sys, html, urllib.request, urllib.parse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}

def get(url, headers=None, binaire=False, timeout=40):
    req = urllib.request.Request(url, headers={**UA, **(headers or {})})
    data = urllib.request.urlopen(req, timeout=timeout).read()
    return data if binaire else data.decode("utf-8", "ignore")

def opt(nom, defaut=None):
    return sys.argv[sys.argv.index(nom) + 1] if nom in sys.argv else defaut

def conf():
    try:
        return json.loads((Path.home() / "cutora-studio.json").read_text(encoding="utf-8"))
    except Exception:
        return {}

def deja(dossier):
    """Plans déjà utilisés : dans ce projet, et dans tout le profil si le fichier existe plus haut."""
    ids = set()
    for f in [dossier / "deja-utilises.json", *[p / "broll-deja-utilises.json" for p in dossier.parents]]:
        if f.exists():
            ids |= set(json.loads(f.read_text(encoding="utf-8")))
    return ids

# ---------- Sources ----------
def mixkit(requete):
    slug = re.sub(r"[^a-z0-9]+", "-", requete.lower()).strip("-")
    url = f"https://mixkit.co/free-stock-video/{slug}/" if "-" not in slug else f"https://mixkit.co/free-stock-video/discover/{slug}/"
    try:
        p = get(url)
    except Exception:
        return []
    out, vus = [], set()
    for m in re.finditer(r'href="/free-stock-video/([a-z0-9-]+)-(\d+)/"', p):
        titre, vid = m.group(1).replace("-", " "), m.group(2)
        if vid in vus:
            continue
        vus.add(vid)
        t = re.search(rf"videos/{vid}/{vid}-thumb-360-(\d)\.jpg", p)
        out.append({"id": f"mixkit-{vid}", "source": "Mixkit", "titre": titre,
                    "page": f"https://mixkit.co/free-stock-video/{m.group(1)}-{vid}/",
                    "vignette": f"https://assets.mixkit.co/videos/{vid}/{vid}-thumb-360-{t.group(1) if t else 0}.jpg",
                    "hd": [f"https://assets.mixkit.co/videos/{vid}/{vid}-1080.mp4", f"https://assets.mixkit.co/videos/{vid}/{vid}-720.mp4"],
                    "licence": "Licence Mixkit (gratuite, sans crédit obligatoire)", "requete": requete})
    return out

def pexels(requete, orientation, n):
    cle = conf().get("pexels_cle")
    if not cle:
        return []
    q = {"query": requete, "per_page": n}
    if orientation:
        q["orientation"] = orientation
    try:
        d = json.loads(get("https://api.pexels.com/videos/search?" + urllib.parse.urlencode(q), {"Authorization": cle}))
    except Exception as e:
        print("Pexels :", e)
        return []
    out = []
    for v in d.get("videos", []):
        fichiers = sorted([f for f in v.get("video_files", []) if f.get("link") and f.get("width")], key=lambda f: -f["width"])
        hd = [f["link"] for f in fichiers if f["width"] <= 1920] or [f["link"] for f in fichiers]
        slug = re.search(r"/video/([a-z0-9-]+)-\d+/?$", v.get("url", ""))
        out.append({"id": f"pexels-{v['id']}", "source": "Pexels", "titre": (slug.group(1).replace("-", " ") if slug else requete),
                    "page": v.get("url"), "vignette": v.get("image"), "hd": hd[:2], "duree": v.get("duration"),
                    "auteur": (v.get("user") or {}).get("name"), "licence": "Licence Pexels (gratuite, crédit apprécié)",
                    "requete": requete, "taille": f"{v.get('width')}x{v.get('height')}"})
    return out

# ---------- Chercher ----------
def chercher():
    dossier = Path(sys.argv[2]).resolve()
    dossier.mkdir(parents=True, exist_ok=True)
    requetes = [a for a in sys.argv[3:] if not a.startswith("--") and sys.argv[sys.argv.index(a) - 1] not in ("--orientation", "--n")]
    orient, n = opt("--orientation"), int(opt("--n", 12))
    exclus = deja(dossier)
    cands, vus = [], set()
    for r in requetes:
        trouves = mixkit(r)[:n] + pexels(r, orient, n)
        mots = set(re.findall(r"[a-z]+", r.lower()))
        trouves.sort(key=lambda c: -len(mots & set(c["titre"].split())))  # le titre décrit le plan : les plus proches d'abord
        for c in trouves:
            if c["id"] in vus or c["id"] in exclus:
                continue
            vus.add(c["id"]); cands.append(c)
    for i, c in enumerate(cands, 1):
        c["n"] = i
    print(len(cands), "candidats (sans les plans déjà utilisés) pour", len(requetes), "requêtes")
    # vignettes
    vdir = dossier / "vignettes"; vdir.mkdir(exist_ok=True)
    def vign(c):
        f = vdir / f"{c['n']:03d}.jpg"
        try:
            f.write_bytes(get(c["vignette"], binaire=True)); c["fichier_vignette"] = str(f)
        except Exception:
            c["fichier_vignette"] = None
    with ThreadPoolExecutor(8) as ex:
        list(ex.map(vign, cands))
    (dossier / "candidats.json").write_text(json.dumps(cands, ensure_ascii=False, indent=1), encoding="utf-8")
    # planches : 4 colonnes, numéro et titre sous chaque vignette, 16 par planche
    from PIL import Image, ImageDraw, ImageFont
    try:
        font = ImageFont.truetype("arial.ttf", 15); big = ImageFont.truetype("arialbd.ttf", 22)
    except Exception:
        font = big = ImageFont.load_default()
    for k in range(0, len(cands), 16):
        lot = cands[k:k + 16]
        cw, ch = 320, 180
        plan = Image.new("RGB", (4 * (cw + 10) + 10, ((len(lot) + 3) // 4) * (ch + 58) + 10), "white")
        d = ImageDraw.Draw(plan)
        for j, c in enumerate(lot):
            x, y = 10 + (j % 4) * (cw + 10), 10 + (j // 4) * (ch + 58)
            if c.get("fichier_vignette"):
                im = Image.open(c["fichier_vignette"]).convert("RGB"); im.thumbnail((cw, ch))
                plan.paste(im, (x + (cw - im.width) // 2, y + (ch - im.height) // 2))
            d.rectangle([x, y, x + 46, y + 30], fill="black"); d.text((x + 6, y + 3), str(c["n"]), fill="white", font=big)
            d.text((x, y + ch + 4), f"{c['source']} : {c['titre'][:42]}", fill="black", font=font)
            d.text((x, y + ch + 24), f"« {c['requete'][:40]} »", fill=(110, 110, 110), font=font)
        plan.save(dossier / f"planche-{k // 16 + 1}.jpg", quality=85)
    print("Planches :", ", ".join(str(p) for p in sorted(dossier.glob("planche-*.jpg"))))

# ---------- Prendre ----------
def prendre():
    dossier, montage = Path(sys.argv[2]).resolve(), Path(sys.argv[3]).resolve()
    nums = [int(a) for a in sys.argv[4:] if a.isdigit()]
    cands = {c["n"]: c for c in json.loads((dossier / "candidats.json").read_text(encoding="utf-8"))}
    dest = montage / "assets" / "broll"; dest.mkdir(parents=True, exist_ok=True)
    fdeja = dossier / "deja-utilises.json"
    utilises = json.loads(fdeja.read_text(encoding="utf-8")) if fdeja.exists() else []
    credits = montage.parent / "CREDITS.md"
    for n in nums:
        c = cands[n]
        sortie = dest / f"{c['id']}.mp4"
        for url in c["hd"]:
            try:
                sortie.write_bytes(get(url, binaire=True, timeout=180)); break
            except Exception:
                continue
        if not sortie.exists():
            print("échec du téléchargement :", n, c["titre"]); continue
        utilises.append(c["id"])
        with open(credits, "a", encoding="utf-8") as f:
            f.write(f"- B-roll {c['source']} : {c['titre']} ({c['page']}){', auteur ' + c['auteur'] if c.get('auteur') else ''}, {c['licence']}\n")
        print("pris :", n, "->", sortie.relative_to(montage))
    fdeja.write_text(json.dumps(sorted(set(utilises)), indent=0), encoding="utf-8")

if __name__ == "__main__":
    {"chercher": chercher, "prendre": prendre}[sys.argv[1]]()
