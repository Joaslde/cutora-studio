# Construit (ou met à jour) le catalogue de musiques de fond du skill : musique/catalogue.json.
# Outil de maintenance, lancé par l'équipe Cutora, pas pendant un montage.
# Étape 1 (fiches) : parcourt toutes les ambiances et tous les genres Mixkit, page par page, et garde pour chaque
#   morceau titre, auteur, durée, ambiances, instruments, genres, mots clés et lien du MP3.
# Étape 2 (--mesurer) : écoute chaque morceau à la place de l'IA, qui ne peut pas écouter : tempo, netteté de la
#   pulsation, énergie, dynamique, brillance, part de basses et de médium, voix chantée probable, début utile,
#   courbe d'énergie par tranches de 5 s. Le MP3 est effacé aussitôt après la mesure.
# Licence Mixkit : usage gratuit dans les vidéos, commerciales comprises, sans crédit obligatoire.
# Les fichiers audio ne sont jamais stockés dans le dépôt : seulement leurs liens.
# Usage : python catalogue_musique.py [--mesurer] [--seulement-mesurer] [--limite N]
import json, re, subprocess, sys, tempfile, time, urllib.request
from html import unescape
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
SORTIE = RACINE / "musique" / "catalogue.json"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36"}
TYPES = {"mood": "ambiances", "instrument": "instruments", "genre": "genres", "tag": "mots"}


def lire(url):
    for essai in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
                return r.read().decode("utf8", "replace")
        except Exception:
            time.sleep(2 + essai * 3)
    return ""


def fiches(h, genres=()):
    for b in h.split('class="item-grid__item"')[1:]:
        m = re.search(r'data-audio-player-item-id-value="(\d+)"', b)
        if not m or 'item-type-value="music"' not in b:
            continue
        titre = re.search(r'item-grid-card__title">\s*(.*?)\s*</h2>', b, re.S)
        auteur = re.search(r'music-preview__author">\s*by\s*(.*?)\s*</p>', b, re.S)
        duree = re.search(r'data-test-id="duration">\s*(\d+):(\d+)', b)
        liens = re.findall(r'href="/free-stock-music/(mood|instrument|genre|tag)/([^/"]+)/"', b)
        liens += [("genre", g) for g in re.findall(r'href="/free-stock-music/([a-z0-9-]+)/"', b) if g in genres]
        yield {
            "id": int(m.group(1)),
            "titre": unescape(titre.group(1)).strip() if titre else "",
            "auteur": unescape(auteur.group(1)).strip() if auteur else "",
            "duree": int(duree.group(1)) * 60 + int(duree.group(2)) if duree else 0,
            "liens": liens,
        }


def construire(limite=None):
    accueil = lire("https://mixkit.co/free-stock-music/")
    moods = sorted(set(re.findall(r'href="/free-stock-music/mood/([^/"]+)/"', accueil)))
    genres = sorted(set(re.findall(r'href="/free-stock-music/([a-z0-9-]+)/"', accueil)) - {"discover", "mood", "instrument", "tag"})
    pages = [f"mood/{m}" for m in moods] + genres
    if limite:
        pages = pages[:limite]
    cat = {}
    for n, p in enumerate(pages, 1):
        page = 1
        while True:
            h = lire(f"https://mixkit.co/free-stock-music/{p}/" + (f"?page={page}" if page > 1 else ""))
            trouves = 0
            for f in fiches(h, genres):
                e = cat.setdefault(f["id"], {"id": f["id"], "titre": f["titre"], "auteur": f["auteur"], "duree": f["duree"],
                                             "ambiances": set(), "instruments": set(), "genres": set(), "mots": set()})
                trouves += 1
                for typ, val in f["liens"]:
                    e[TYPES[typ]].add(val)
                if p.startswith("mood/"):
                    e["ambiances"].add(p[5:])
                else:
                    e["genres"].add(p)
            if not trouves or f"?page={page + 1}" not in h:
                break
            page += 1
            time.sleep(0.4)
        print(f"[{n}/{len(pages)}] {p} : {len(cat)} morceaux en tout", flush=True)
        time.sleep(0.4)
    morceaux = []
    for e in sorted(cat.values(), key=lambda x: x["id"]):
        for k in TYPES.values():
            e[k] = sorted(e[k])
        e["mp3"] = f"https://assets.mixkit.co/music/{e['id']}/{e['id']}.mp3"
        morceaux.append(e)
    return morceaux


def mesurer(e, dossier):
    """Ce que l'oreille dirait, en chiffres. Analyse en mono, 22 kHz."""
    import numpy as np
    f = Path(dossier) / f"{e['id']}.mp3"
    with urllib.request.urlopen(urllib.request.Request(e["mp3"], headers=UA), timeout=90) as r:
        f.write_bytes(r.read())
    brut = subprocess.run(["ffmpeg", "-v", "error", "-i", str(f), "-ac", "1", "-ar", "22050", "-f", "f32le", "-"],
                          capture_output=True).stdout
    f.unlink(missing_ok=True)
    x = np.frombuffer(brut, dtype=np.float32)
    if x.size < 22050 * 5:
        return None
    sr, hop, win = 22050, 512, 2048
    n = (x.size - win) // hop
    fps = sr / hop
    spec = np.empty((n, win // 2 + 1), dtype=np.float32)
    fen = np.hanning(win).astype(np.float32)
    for i in range(0, n, 2000):  # par paquets, pour ne pas saturer la mémoire
        j = min(n, i + 2000)
        idx = np.arange(win)[None, :] + hop * np.arange(i, j)[:, None]
        spec[i:j] = np.abs(np.fft.rfft(x[idx] * fen, axis=1))
    freqs = np.fft.rfftfreq(win, 1 / sr)
    rms = np.sqrt((x[: n * hop].reshape(n, hop) ** 2).mean(axis=1) + 1e-12)
    db = 20 * np.log10(rms + 1e-9)
    # Tempo : autocorrélation du flux spectral, cherché entre 60 et 180 BPM
    flux = np.maximum(np.diff(np.log1p(spec), axis=0), 0).sum(axis=1)
    flux = flux - flux.mean()
    ac = np.fft.irfft(np.abs(np.fft.rfft(flux, 2 * flux.size)) ** 2)[: flux.size]
    lags = np.arange(ac.size)
    zone = (lags >= fps * 60 / 180) & (lags <= fps * 60 / 60)
    lag = lags[zone][np.argmax(ac[zone])]
    bpm = 60 * fps / lag
    while bpm < 80:  # l'autocorrélation tombe souvent sur la moitié du tempo réel
        bpm *= 2
    while bpm > 160:
        bpm /= 2
    bloc = int(5 * fps)
    courbe = [round(float(np.mean(db[i:i + bloc])), 1) for i in range(0, db.size, bloc)]
    seuil = np.percentile(db, 60) - 6
    total = spec.sum() + 1e-9
    bande = spec[:, (freqs > 300) & (freqs < 3400)] + 1e-9
    platitude = np.exp(np.mean(np.log(bande), axis=1)) / bande.mean(axis=1)
    return {
        "bpm": int(round(bpm)),
        "pulsation": round(float(ac[lag] / (ac[0] + 1e-9)), 2),
        "energie": round(float(np.percentile(db, 75)), 1),
        "dynamique": round(float(np.percentile(db, 95) - np.percentile(db, 10)), 1),
        "brillance_hz": int(round(float((spec * freqs).sum() / total))),
        "basses": round(float(spec[:, freqs < 250].sum() / total), 2),
        "medium": round(float(spec[:, (freqs >= 400) & (freqs < 3000)].sum() / total), 2),
        "voix_probable": round(float(np.mean(platitude < 0.12)), 2),
        "debut_utile": round(float(np.argmax(db > seuil) / fps), 1),
        "courbe_5s": courbe,
    }


if __name__ == "__main__":
    limite = int(sys.argv[sys.argv.index("--limite") + 1]) if "--limite" in sys.argv else None
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    ancien = {m["id"]: m for m in json.loads(SORTIE.read_text("utf8"))["morceaux"]} if SORTIE.exists() else {}
    if "--seulement-mesurer" in sys.argv and ancien:
        morceaux = list(ancien.values())
    else:
        morceaux = construire(limite)
        for m in morceaux:
            if ancien.get(m["id"], {}).get("mesure"):
                m["mesure"] = ancien[m["id"]]["mesure"]

    def ecrire():
        SORTIE.write_text(json.dumps({
            "source": "Mixkit, licence Mixkit Free Music : gratuite, usage commercial compris, sans crédit obligatoire",
            "mis_a_jour": time.strftime("%Y-%m-%d"), "nombre": len(morceaux), "morceaux": morceaux,
        }, ensure_ascii=False, indent=1), "utf8")

    ecrire()
    print(f"{len(morceaux)} morceaux dans {SORTIE}")
    if "--mesurer" in sys.argv or "--seulement-mesurer" in sys.argv:
        a_faire = [m for m in morceaux if not m.get("mesure")]
        with tempfile.TemporaryDirectory() as d:
            for i, m in enumerate(a_faire, 1):
                try:
                    m["mesure"] = mesurer(m, d)
                except Exception as err:
                    print("  échec", m["id"], err, flush=True)
                if i % 10 == 0 or i == len(a_faire):
                    ecrire()
                    print(f"  mesurés : {i}/{len(a_faire)}", flush=True)
