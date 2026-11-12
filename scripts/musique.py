# Choisir la musique de fond d'un montage dans le catalogue du skill (musique/catalogue.json, plusieurs centaines de
# morceaux Mixkit classés et mesurés), d'après l'ambiance, le rythme et l'énergie de la vidéo.
#
#   python musique.py familles
#       liste les familles d'ambiance (calme, inspirant, motivant, suspense...) et ce qu'elles contiennent.
#   python musique.py choisir <projet> --familles inspirant,calme [--tempo 85-110] [--energie basse|moyenne|haute]
#           [--duree 90] [--instruments piano,strings] [--genres corporate-music] [--eviter dark,scary]
#           [--profil <dossier du profil>] [--n 8]
#       note chaque morceau, écarte ceux déjà utilisés par la personne, garde une sélection variée (un seul morceau
#       par auteur), écrit <projet>/musique/candidats.json et <projet>/musique/ecoute.html (page d'écoute à ouvrir).
#   python musique.py essai <projet> <id> --voix <voix.wav> [--debut 0] [--duree 30] [--volume 0.35]
#       mélange 30 s de la vraie voix avec le morceau, au niveau du montage : <projet>/musique/essai-<id>.mp3.
#       C'est ainsi que la personne juge vraiment : une musique seule et une musique sous une voix sont deux choses.
#   python musique.py prendre <projet> <id> [--profil <dossier>] [--montage <nom>]
#       télécharge le morceau dans <projet>/assets/musique/, le note dans musiques-utilisees.json du profil
#       (pour ne pas reprendre le même la fois suivante) et dans CREDITS.md.
import json, subprocess, sys, urllib.request
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
CATALOGUE = RACINE / "musique" / "catalogue.json"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36"}

# Familles d'ambiance : le vocabulaire de la personne et de la vidéo, traduit en ambiances Mixkit.
# Chaque famille donne aussi un tempo et une énergie typiques, utilisés si on ne précise rien.
FAMILLES = {
    "calme":       {"ambiances": ["calm", "peaceful", "relaxed", "serene", "soothing", "mellow", "meditative", "contented"],
                    "tempo": (60, 100), "energie": "basse", "dit": "posé, rassurant, explication tranquille"},
    "inspirant":   {"ambiances": ["hopeful", "uplifting", "positive", "warm", "beautiful", "motivating", "tender"],
                    "tempo": (80, 125), "energie": "moyenne", "dit": "histoire qui donne envie, déclic, transformation"},
    "motivant":    {"ambiances": ["energetic", "motivating", "determined", "confident", "driving", "dynamic", "upbeat", "powerful"],
                    "tempo": (100, 140), "energie": "haute", "dit": "passer à l'action, sport, business qui avance"},
    "pro":         {"ambiances": ["confident", "positive", "neutral", "determined", "elegant"], "genres": ["corporate-music"],
                    "tempo": (90, 125), "energie": "moyenne", "dit": "présentation d'entreprise, offre, tutoriel sérieux"},
    "reflexion":   {"ambiances": ["reflective", "emotional", "sentimental", "nostalgic", "melancholic", "tender", "lonely"],
                    "tempo": (60, 100), "energie": "basse", "dit": "confidence, récit personnel, moment difficile"},
    "suspense":    {"ambiances": ["suspenseful", "tension", "mysterious", "cautious", "anxious", "restless", "stealth"],
                    "tempo": (70, 120), "energie": "moyenne", "dit": "révélation, erreur à éviter, enquête, accroche"},
    "sombre":      {"ambiances": ["dark", "ominous", "menacing", "sombre", "eerie"],
                    "tempo": (60, 110), "energie": "moyenne", "dit": "danger, arnaque, vérité dérangeante (avec mesure)"},
    "epique":      {"ambiances": ["epic", "heroic", "triumphant", "majestic", "glorious", "proud", "powerful"],
                    "tempo": (80, 140), "energie": "haute", "dit": "résultat, victoire, grand chiffre, bande-annonce"},
    "leger":       {"ambiances": ["playful", "fun", "cheerful", "happy", "lighthearted", "carefree", "friendly", "joyful"],
                    "tempo": (95, 135), "energie": "moyenne", "dit": "astuce, quotidien, humour léger, lifestyle"},
    "decale":      {"ambiances": ["quirky", "whimsical", "humorous", "mischievous", "silly", "ironic"],
                    "tempo": (90, 135), "energie": "moyenne", "dit": "humour, absurde, situation gênante"},
    "tech":        {"ambiances": ["futuristic", "hypnotic", "mechanical", "atmospheric"], "genres": ["electronic", "electronica", "ambient"],
                    "tempo": (90, 130), "energie": "moyenne", "dit": "IA, outils, logiciel, écran partagé, futur"},
    "chill":       {"ambiances": ["smooth", "dreamy", "lazy", "mellow", "relaxed"], "genres": ["chillout", "downtempo", "lofi-hip-hop", "hip-hop"],
                    "tempo": (70, 100), "energie": "basse", "dit": "vlog, ambiance détendue, coulisses, travail au calme"},
    "elegant":     {"ambiances": ["elegant", "glamorous", "smooth", "sensual", "graceful"],
                    "tempo": (70, 115), "energie": "moyenne", "dit": "luxe, immobilier, mode, beauté"},
    "dramatique":  {"ambiances": ["dramatic", "emotional", "tragic", "passionate", "intense"],
                    "tempo": (60, 120), "energie": "moyenne", "dit": "émotion forte, histoire vraie, avant et après"},
    "festif":      {"ambiances": ["festive", "euphoric", "exciting", "lively", "glorious"], "genres": ["dance-pop", "edm", "house", "disco"],
                    "tempo": (115, 135), "energie": "haute", "dit": "lancement, promo, fête, annonce"},
}
ENERGIE = {"basse": (-40, -15), "moyenne": (-17, -10), "haute": (-12, 0)}


def arg(nom, defaut=None):
    return sys.argv[sys.argv.index(nom) + 1] if nom in sys.argv else defaut


def liste(nom):
    v = arg(nom)
    return [x.strip() for x in v.split(",") if x.strip()] if v else []


def charger():
    if not CATALOGUE.exists():
        sys.exit("Catalogue absent : lancer d'abord python scripts/catalogue_musique.py --mesurer")
    return json.loads(CATALOGUE.read_text("utf8"))["morceaux"]


def deja(profil):
    f = Path(profil) / "musiques-utilisees.json" if profil else None
    return (json.loads(f.read_text("utf8")) if f and f.exists() else []), f


def noter(m, voulu, tempo, energie, duree, instruments, genres, eviter):
    s, raisons = 0.0, []
    amb = set(m["ambiances"])
    communs = amb & voulu
    if not communs:
        return None, []
    s += 3 * len(communs)
    raisons.append("ambiance " + ", ".join(sorted(communs)))
    if amb & eviter:
        return None, []
    mes = m.get("mesure") or {}
    if mes:
        bpm = mes["bpm"]
        if tempo[0] <= bpm <= tempo[1]:
            s += 2
            raisons.append(f"{bpm} BPM")
        else:
            s -= min(3, abs(bpm - (tempo[0] if bpm < tempo[0] else tempo[1])) / 10)
        lo, hi = ENERGIE[energie]
        if lo <= mes["energie"] <= hi:
            s += 1.5
            raisons.append(f"énergie {energie}")
        if mes.get("voix_probable", 0) > 0.25:
            s -= 4  # une voix chantée se bat avec la voix off
        else:
            s += 1
        if mes.get("dynamique", 30) < 16:
            s += 1  # régulier : reste sagement sous la voix
            raisons.append("régulier sous la voix")
        if mes.get("medium", 0) > 0.6:
            s -= 1  # trop de médium : couvre la voix
    if duree:
        if m["duree"] >= duree:
            s += 1.5
            raisons.append("assez long, sans boucle")
        elif m["duree"] < duree * 0.6:
            s -= 1.5
    if instruments and set(m["instruments"]) & instruments:
        s += 1.5
        raisons.append(", ".join(sorted(set(m["instruments"]) & instruments)))
    if genres and set(m["genres"]) & genres:
        s += 1.5
    return s, raisons


def choisir():
    projet = Path(sys.argv[2])
    fams = liste("--familles") or ["inspirant"]
    inconnues = [f for f in fams if f not in FAMILLES]
    if inconnues:
        sys.exit(f"Familles inconnues : {inconnues}. Disponibles : {', '.join(FAMILLES)}")
    voulu = set(sum((FAMILLES[f]["ambiances"] for f in fams), []))
    genres = set(liste("--genres")) | set(sum((FAMILLES[f].get("genres", []) for f in fams), []))
    t = arg("--tempo")
    tempo = tuple(int(x) for x in t.split("-")) if t else FAMILLES[fams[0]]["tempo"]
    energie = arg("--energie", FAMILLES[fams[0]]["energie"])
    duree = float(arg("--duree", 0))
    n = int(arg("--n", 8))
    utilises, _ = deja(arg("--profil"))
    exclus = {u["id"] for u in utilises}
    notes = []
    for m in charger():
        if m["id"] in exclus:
            continue
        s, r = noter(m, voulu, tempo, energie, duree, set(liste("--instruments")), genres, set(liste("--eviter")))
        if s is not None:
            notes.append((s, m, r))
    notes.sort(key=lambda x: -x[0])
    choix, auteurs = [], set()
    for s, m, r in notes:  # variété : un seul morceau par auteur dans la sélection
        if m["auteur"] in auteurs:
            continue
        auteurs.add(m["auteur"])
        choix.append({**m, "note": round(s, 1), "pourquoi": r})
        if len(choix) == n:
            break
    d = projet / "musique"
    d.mkdir(parents=True, exist_ok=True)
    (d / "candidats.json").write_text(json.dumps({"familles": fams, "tempo": tempo, "energie": energie, "duree": duree,
                                                  "candidats": choix}, ensure_ascii=False, indent=1), "utf8")
    page(d / "ecoute.html", fams, choix)
    print(f"{len(notes)} morceaux correspondent, {len(choix)} retenus (déjà utilisés écartés : {len(exclus)})")
    for i, c in enumerate(choix, 1):
        mes = c.get("mesure") or {}
        print(f"{i}. [{c['id']}] {c['titre']} ({c['auteur']}), {c['duree'] // 60}:{c['duree'] % 60:02d}, "
              f"{mes.get('bpm', '?')} BPM : {' ; '.join(c['pourquoi'])}")
    print("Page d'écoute :", d / "ecoute.html")


def page(f, fams, choix):
    cartes = []
    for i, c in enumerate(choix, 1):
        mes = c.get("mesure") or {}
        debut = mes.get("debut_utile", 0)
        cartes.append(f"""<article><div class="n">{i}</div><div class="c">
<h2>{c['titre']}</h2><p class="a">{c['auteur']} . {c['duree'] // 60}:{c['duree'] % 60:02d} . {mes.get('bpm', '?')} BPM</p>
<p class="t">{', '.join(c['ambiances'][:6])}{(' . ' + ', '.join(c['instruments'][:4])) if c['instruments'] else ''}</p>
<p class="p">{' ; '.join(c['pourquoi'])}</p>
<audio controls preload="none" src="{c['mp3']}#t={debut}"></audio></div></article>""")
    f.write_text(f"""<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Musiques proposées</title><style>
body{{margin:0;background:#FDFBF7;color:#1A1A1A;font:16px/1.5 system-ui,sans-serif}}
main{{max-width:760px;margin:0 auto;padding:32px 16px}}h1{{font-size:26px;margin:0 0 4px}}
.s{{color:#6b6b6b;margin:0 0 24px}}article{{display:flex;gap:16px;border:1px solid #e5ded2;border-radius:14px;padding:16px;margin:0 0 12px;background:#fff}}
.n{{font:900 28px system-ui;color:#B87333;min-width:32px}}.c{{flex:1;min-width:0}}h2{{margin:0;font-size:18px}}
.a,.t{{margin:2px 0;color:#6b6b6b;font-size:14px}}.p{{margin:6px 0 10px;font-size:14px;color:#1F355E}}audio{{width:100%}}
</style></head><body><main><h1>Musiques proposées</h1>
<p class="s">Ambiance recherchée : {', '.join(fams)}. Écoute, puis dis le numéro que tu préfères (ou « aucune »).</p>
{''.join(cartes)}</main></body></html>""", "utf8")


def telecharger(m, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.exists():
        with urllib.request.urlopen(urllib.request.Request(m["mp3"], headers=UA), timeout=120) as r:
            dest.write_bytes(r.read())
    return dest


def trouver(i):
    m = next((x for x in charger() if x["id"] == int(i)), None)
    if not m:
        sys.exit(f"Morceau {i} absent du catalogue")
    return m


def essai():
    projet, m = Path(sys.argv[2]), trouver(sys.argv[3])
    voix = arg("--voix")
    if not voix:
        sys.exit("--voix <fichier> obligatoire : l'essai se juge sous la vraie voix")
    src = telecharger(m, projet / "assets" / "musique" / f"{m['id']}.mp3")
    debut = float(arg("--debut", (m.get("mesure") or {}).get("debut_utile", 0)))
    duree, vol = float(arg("--duree", 30)), float(arg("--volume", 0.35))
    intro = 3  # 3 s de musique seule, pour l'entendre avant que la voix arrive
    sortie = projet / "musique" / f"essai-{m['id']}.mp3"
    sortie.parent.mkdir(parents=True, exist_ok=True)
    total = duree + intro
    filtre = (f"[1:a]atrim=start={debut}:duration={total},asetpts=PTS-STARTPTS,loudnorm=I=-16,"
              f"volume='if(lt(t,{intro}),{min(1, vol * 2.2)},{vol})':eval=frame,"
              f"afade=t=in:d=1,afade=t=out:st={total - 2}:d=2[m];"
              f"[0:a]atrim=duration={duree},loudnorm=I=-16,adelay={intro * 1000}|{intro * 1000},apad[v];"
              f"[m][v]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.9")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", voix, "-i", str(src), "-filter_complex", filtre,
                    "-c:a", "libmp3lame", "-b:a", "192k", str(sortie)], check=True)
    print("Essai :", sortie)


def prendre():
    projet, m = Path(sys.argv[2]), trouver(sys.argv[3])
    dest = telecharger(m, projet / "assets" / "musique" / f"{m['id']}.mp3")
    utilises, f = deja(arg("--profil"))
    if f:
        if m["id"] not in {u["id"] for u in utilises}:
            utilises.append({"id": m["id"], "titre": m["titre"], "montage": arg("--montage", projet.name)})
        f.write_text(json.dumps(utilises, ensure_ascii=False, indent=1), "utf8")
    cr = projet / "CREDITS.md"
    ligne = f"- Musique : « {m['titre']} » par {m['auteur']} (Mixkit, licence Mixkit Free Music, crédit non obligatoire)\n"
    if not cr.exists() or ligne not in cr.read_text("utf8"):
        with cr.open("a", encoding="utf8") as o:
            o.write(ligne)
    print("Musique prête :", dest, f"(début utile conseillé : {(m.get('mesure') or {}).get('debut_utile', 0)} s)")


if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else ""
    if action == "familles":
        for k, v in FAMILLES.items():
            print(f"{k:11s} {v['tempo'][0]}-{v['tempo'][1]} BPM, énergie {v['energie']:8s} : {v['dit']}")
    elif action == "choisir":
        choisir()
    elif action == "essai":
        essai()
    elif action == "prendre":
        prendre()
    else:
        print(__doc__ if __doc__ else open(__file__, encoding="utf8").read().split("import json")[0])
