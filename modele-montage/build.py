# Générateur de montage Cutora Studio : style de la personne + plan de montage -> projet HyperFrames complet.
# Usage : python build.py <plan.json>
#   Le plan (voir plan-exemple.json) dit où sont la voix, les mots, la caméra, les médias, et découpe la vidéo en
#   scènes avec leur mise en page. Le style vient du choix.json de la personne (page de choix).
#   Écrit <projet>/index.html, <projet>/compositions/*.html et télécharge les polices manquantes dans assets/fonts/.
# Mises en page : « partage » (motion design en haut, caméra en carte en bas ou à droite), « visage » (caméra plein
# cadre), « motion » (motion design plein cadre, sans caméra), « media » (un B-roll plein cadre).
import json, re, sys, urllib.request
from pathlib import Path

ICI = Path(__file__).resolve().parent
PLAN_F = Path(sys.argv[1]).resolve()
PLAN = json.loads(PLAN_F.read_text(encoding="utf-8"))
BASE = PLAN_F.parent
PROJ = (BASE / PLAN.get("projet", "../montage")).resolve()
STYLE = json.loads((BASE / PLAN["style"]).resolve().read_text(encoding="utf-8"))
W, H = PLAN.get("largeur", 1080), PLAN.get("hauteur", 1920)
VERT = H > W
TOTAL = float(PLAN["duree"])
(PROJ / "compositions").mkdir(parents=True, exist_ok=True)

# ---------- Style : couleurs, polices, tailles ----------
def lum(h):
    n = int(h.lstrip("#"), 16)
    return (0.299 * (n >> 16) + 0.587 * ((n >> 8) & 255) + 0.114 * (n & 255)) / 255

def rgba(h, a):
    n = int(h.lstrip("#"), 16)
    return f"rgba({n >> 16},{(n >> 8) & 255},{n & 255},{a})"

C = STYLE["couleurs"]
BG, ACC, ACC2 = C["fond"], C["forte"], C.get("secondaire", C["forte"])
LIGHT = lum(BG) > 0.5
FG = C.get("texte") or ("#151515" if LIGHT else "#FDFBF7")
P = STYLE["polices"]
PF, PT, PA = P["forte"], P["normale"], P["accent"]
TAILLE = {"normal": 0.75, "grand": 1.0, "tres-grand": 1.3}.get(STYLE.get("taille_titres"), 1.0)
TS = (9.5 if VERT else 5.2) * TAILLE
ANIM = STYLE.get("apparition_texte", "flou-net")
TRANS = STYLE.get("transitions", "coupe")
ACCENT = STYLE.get("mot_cle", "couleur-italique")
CAPS = STYLE.get("sous_titres", "mot-unique")
ECART = {"calme": 0.18, "naturel": 0.12, "rapide": 0.08}.get(STYLE.get("rythme"), 0.12)

VARS = (f"--bg:{BG};--fg:{FG};--acc:{ACC};--acc2:{ACC2};--onacc:{'#111111' if lum(ACC) > 0.6 else '#FFFFFF'};"
        f"--gl:{'rgba(0,0,0,.07)' if LIGHT else 'rgba(255,255,255,.06)'};--tile:{'rgba(0,0,0,.05)' if LIGHT else 'rgba(255,255,255,.07)'};"
        f"--tileb:{'rgba(0,0,0,.15)' if LIGHT else 'rgba(255,255,255,.18)'};--halo:{rgba(ACC, .18)};--halo2:{rgba(ACC, .45)};"
        f"--ff:'{PF['police']}';--fw:{PF['graisse']};--fmaj:{'uppercase' if PF.get('capitales') else 'none'};"
        f"--ft:'{PT['police']}';--ftw:{PT['graisse']};--fa:'{PA['police']}';--faw:{PA['graisse']};"
        f"--fai:{'italic' if PA.get('italique') else 'normal'};--ts:{TS * W / 100:.1f}px;--u:{W / 100:.2f}px;")

# ---------- Polices : celles de HyperFrames sont intégrées, les autres sont téléchargées ----------
INTEGREES = {"Inter", "Montserrat", "Outfit", "Nunito", "Oswald", "League Gothic", "Archivo Black", "Space Mono", "IBM Plex Mono",
             "JetBrains Mono", "EB Garamond", "Playfair Display", "Source Code Pro", "Noto Sans JP", "Roboto", "Open Sans", "Lato", "Poppins"}

def polices_css():
    css, dossier = [], PROJ / "assets" / "fonts"
    for p in (PF, PT, PA):
        fam = p["police"]
        if fam in INTEGREES:
            continue
        nom = re.sub(r"[^a-z0-9]+", "-", fam.lower())
        f = dossier / f"{nom}-{p['graisse']}{'i' if p.get('italique') else ''}.woff2"
        if not f.exists():
            dossier.mkdir(parents=True, exist_ok=True)
            ua = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"}
            nomq = fam.replace(" ", "+")
            essais = [f"{nomq}:ital,wght@1,{p['graisse']}", f"{nomq}:ital@1", f"{nomq}:ital,wght@1,400"] if p.get("italique") else \
                     [f"{nomq}:wght@{p['graisse']}", nomq]
            url = None
            for q in essais:  # certaines polices n'ont qu'une graisse : on essaie du plus précis au plus simple
                try:
                    txt = urllib.request.urlopen(urllib.request.Request(f"https://fonts.googleapis.com/css2?family={q}&display=swap", headers=ua), timeout=30).read().decode("utf-8")
                except Exception:
                    continue
                blocs = re.findall(r"/\* latin \*/\s*@font-face\s*{(.*?)}", txt, re.S) or re.findall(r"@font-face\s*{(.*?)}", txt, re.S)
                m = re.search(r"url\((https://[^)]+)\)", blocs[-1]) if blocs else None
                if m:
                    url = m.group(1); break
            if not url:
                print("police introuvable, remplacée par Montserrat :", fam)
                continue
            f.write_bytes(urllib.request.urlopen(urllib.request.Request(url, headers=ua), timeout=30).read())
            print("police téléchargée :", fam)
        css.append(f"@font-face {{ font-family: '{fam}'; src: url('assets/fonts/{f.name}') format('woff2'); "
                   f"font-weight: {p['graisse']}; font-style: {'italic' if p.get('italique') else 'normal'}; }}")
    return "\n".join(css)

FONTS_CSS = polices_css()
KIT_CSS = (ICI / "kit.css").read_text(encoding="utf-8")
KIT_JS = (ICI / "kit.js").read_text(encoding="utf-8")

# ---------- Géométrie des mises en page (en pixels de la vidéo) ----------
if VERT:
    CARTE = (round(0.06 * W), round(0.66 * H), round(0.88 * W), H - round(0.66 * H))  # caméra en carte en bas
    ZONE = {"partage": "left:8%;right:8%;top:24%;height:28%", "motion": "left:8%;right:8%;top:27%;height:42%"}
    CAP_TOP = {"partage": 0.55, "visage": 0.76, "motion": 0.77, "media": 0.77}
    TTL = {"partage": "--ttl-top:7%", "motion": "--ttl-top:8%", "media": "--ttl-top:8%"}
else:
    CARTE = (round(0.58 * W), round(0.13 * H), round(0.37 * W), round(0.74 * H))  # caméra en carte à droite
    ZONE = {"partage": "left:5%;right:46%;top:36%;height:50%", "motion": "left:14%;right:14%;top:30%;height:55%"}
    CAP_TOP = {"partage": 0.88, "visage": 0.84, "motion": 0.88, "media": 0.86}
    TTL = {"partage": "--ttl-top:10%;right:46%", "motion": "--ttl-top:8%", "media": "--ttl-top:8%"}
RAYON = round(0.035 * min(W, H))

# ---------- Contenus de motion design ----------
def media_tag(src, sid, i, dur, pos="50% 50%"):
    if re.search(r"\.(mp4|webm|mov)$", src, re.I):
        return (f'<video id="{sid}-m{i}" class="clip" src="{src}" data-start="0" data-duration="{dur}" data-track-index="{5 + i}" '
                f'muted playsinline style="object-position:{pos}"></video>')
    return f'<img src="{src}" alt="" style="object-position:{pos}">'

def motion_html(m, sid, dur):
    k, tx, md = m.get("type", "cartes"), m.get("textes", []), m.get("medias", [])
    if k == "telephone":
        inner = media_tag(md[0], sid, 0, dur) if md else '<div style="margin:22% auto 6%;width:40%;aspect-ratio:1;border-radius:50%;background:var(--acc)"></div>'
        return f'<div class="halo" style="left:28%;top:18%;width:44%;height:64%"></div><div class="phone" style="left:31%;top:0;width:38%;height:100%">{inner}</div>'
    if k == "orbite":
        n = max(3, len(md) or len(tx) - 1 or 5)
        import math
        ics = []
        for i in range(n):
            a = 2 * math.pi * i / n - math.pi / 2
            cont = f'<img src="{md[i]}" alt="">' if i < len(md) else (tx[i + 1] if i + 1 < len(tx) else "")
            ics.append(f'<div class="ic" style="left:calc(var(--u) * {30 * math.cos(a):.1f});top:calc(var(--u) * {(18 if VERT else 12) * math.sin(a):.1f})">{cont}</div>')
        return f'<div class="tag" style="left:50%;top:50%;transform:translate(-50%,-50%)">{tx[0] if tx else "Idée"}</div><div class="orb" style="position:absolute;left:50%;top:50%;width:0;height:0">{"".join(ics)}</div>'
    if k == "fleches":
        cible = f'<div class="tile tg" style="right:4%;top:10%;width:46%;height:80%">{media_tag(md[0], sid, 0, dur) if md else ""}{f"<div class=lbl>{tx[0]}</div>" if tx else ""}</div>'
        return cible + ('<svg viewBox="0 0 100 60" preserveAspectRatio="none" style="position:absolute;inset:0;width:100%;height:100%;overflow:visible">'
                        '<path class="ar" d="M4 54 C16 18 30 12 50 28" stroke="var(--acc)" stroke-width="2.4" fill="none" stroke-linecap="round" stroke-dasharray="70" stroke-dashoffset="70"/>'
                        '<path class="ah" d="M44 21 L51 29 L42 32" stroke="var(--acc)" stroke-width="2.4" fill="none" stroke-linecap="round" stroke-linejoin="round" opacity="0"/></svg>')
    if k == "chiffres":
        bars = "".join(f'<div class="br" style="flex:1;height:{h}%;border-radius:calc(var(--u) * 1) calc(var(--u) * 1) 0 0;background:{"var(--acc)" if i == 3 else "var(--tileb)"}"></div>' for i, h in enumerate([30, 52, 40, 92]))
        return (f'<div class="big cnt" style="position:absolute;right:2%;top:0;font-size:calc(var(--u) * {14 if VERT else 8});color:var(--acc)">{m.get("chiffre", "+85 %")}</div>'
                f'<div style="position:absolute;left:4%;right:42%;bottom:2%;top:12%;display:flex;gap:9%;align-items:flex-end">{bars}</div>'
                + (f'<div style="position:absolute;right:2%;top:{38 if VERT else 30}%;width:36%;text-align:right;font-weight:600;font-size:calc(var(--u) * {4.4 if VERT else 2.4});font-family:var(--ft),sans-serif">{tx[0]}</div>' if tx else ""))
    if k == "etiquettes":
        fond = media_tag(md[0], sid, 0, dur) if md else '<div class="ln" style="top:16%;width:70%"></div><div class="ln" style="top:34%;width:50%"></div>'
        pos = [("left:2%;top:12%"), ("right:1%;top:42%"), ("left:6%;top:72%"), ("right:6%;top:84%")]
        return f'<div class="tile" style="left:20%;top:2%;width:60%;height:96%">{fond}</div>' + "".join(f'<div class="tag" style="{pos[i % 4]}">{t}</div>' for i, t in enumerate(tx or ["Rapide", "Gratuit", "Simple"]))
    if k == "saisie":
        q = tx[0] if tx else "Écris-moi un script"
        rep = media_tag(md[0], sid, 0, dur) if md else "".join(f'<div class="ln" style="top:{18 + 24 * i}%;width:{w}%"></div>' for i, w in enumerate([70, 55, 64]))
        return (f'<div class="tile champ" style="left:3%;right:3%;top:2%;height:30%;display:flex;align-items:center;padding:0 5%;font:600 calc(var(--u) * {5 if VERT else 2.8}) var(--ft),sans-serif">'
                f'<span class="typ" style="overflow:hidden;white-space:nowrap;display:inline-block;width:0">{q}</span><span class="cur" style="display:inline-block;width:.15em;height:1.1em;background:var(--acc);margin-left:.15em"></span></div>'
                f'<div class="tile rep" style="left:3%;right:18%;top:40%;height:58%">{rep}</div>')
    if k == "liste":
        return '<div class="liste">' + "".join(f'<div class="it"><i></i><span>{t}</span></div>' for t in tx) + "</div>"
    if k == "media":
        return f'<div class="tile" style="inset:0">{media_tag(md[0], sid, 0, dur) if md else ""}{f"<div class=lbl>{tx[0]}</div>" if tx else ""}</div>'
    # cartes (par défaut) : une à trois cartes qui se chevauchent
    n = max(1, len(md) or 2)
    geo = [("left:2%;top:4%;width:54%;height:80%"), ("left:40%;top:16%;width:58%;height:82%"), ("left:20%;top:10%;width:56%;height:84%")]
    out = []
    for i in range(min(n, 3)):
        cont = media_tag(md[i], sid, i, dur) if i < len(md) else '<div class="ln" style="top:16%;width:60%"></div><div class="ln" style="top:32%;width:40%"></div>'
        lbl = f'<div class="lbl">{tx[i]}</div>' if i < len(tx) else ""
        out.append(f'<div class="tile" style="{geo[i]}">{cont}{lbl}</div>')
    return "".join(out)

def titre_html(t):
    acc = {"couleur-italique": "acc-c acc-f", "couleur": "acc-c", "italique": "acc-f", "pave": "acc-p", "souligne": "acc-u"}.get(ACCENT, "acc-c acc-f")
    def mot(txt, cls=""):
        inner = "".join(f'<span class="ch">{c}</span>' for c in txt) if ANIM == "machine" else txt
        if "acc-u" in cls:
            inner += '<i class="ul"></i>'
        w = f'<span class="w {cls}">{inner}</span>'
        return f'<span class="mk">{w}</span>' if ANIM == "masque" else w
    faible = " ".join(mot(x) for x in t.get("faible", "").split())
    fort = " ".join(mot(x) for x in t.get("fort", "").split())
    cle = " ".join(mot(x, acc) for x in t.get("cle", "").split())
    return f'<div class="ttl"><div class="weak">{faible}</div><div class="strong">{fort} {cle}</div></div>'

# ---------- Scènes ----------
SCENES = PLAN["scenes"]
hosts, comps = [], 0
for i, s in enumerate(SCENES):
    s.setdefault("id", f"s{i + 1:02d}")
    page = s.get("page", "partage")
    if page == "visage" and not s.get("titre") and not s.get("motion"):
        continue
    sid, d = s["id"], round(s["fin"] - s["debut"], 3)
    corps = ""
    if page in ("partage", "motion"):
        corps += '<div class="gridbg"></div>'
    if page == "media" and s.get("media"):
        plein = media_tag(s["media"], sid, 9, d, s.get("cadrage", "50% 50%"))
        corps += ('<div class="tile" style="inset:0;border:0;border-radius:0;box-shadow:none">' + plein + '</div>'
                  '<div style="position:absolute;inset:0;background:linear-gradient(rgba(0,0,0,.55),transparent 35%,transparent 60%,rgba(0,0,0,.6))"></div>')
    if s.get("titre"):
        corps += titre_html(s["titre"])
    m = s.get("motion")
    if m:
        corps += f'<div class="mz" style="{ZONE.get(page, ZONE["partage"])}">{motion_html(m, sid, d)}</div>'
    titre_t = (s.get("titre") or {}).get("t", 0.12)
    html = f"""<template>
  <style>
{FONTS_CSS}
{KIT_CSS}
    #root {{ {VARS}{TTL.get(page, "")} }}
  </style>
  <div id="root" data-composition-id="{sid}" data-width="{W}" data-height="{H}">
    {corps}
  </div>
  <script>
{KIT_JS}
    (() => {{
      const tl = gsap.timeline({{ paused: true }});
      const R = document.querySelector('[data-composition-id="{sid}"]');
      kitEntree(tl, R, {json.dumps(TRANS)});
      kitTitre(tl, R, {json.dumps(ANIM)}, {titre_t}, {ECART});
      {f"kitMotion(tl, R.querySelector('.mz'), {json.dumps(m, ensure_ascii=False)}, {d});" if m else ""}
      kitSortie(tl, R, {json.dumps(TRANS)}, {d});
      tl.set({{}}, {{}}, {d});
      window.__timelines["{sid}"] = tl;
    }})();
  </script>
</template>
"""
    sortie = PROJ / "compositions" / f"{sid}.html"
    if not (s.get("sur_mesure") and sortie.exists()):  # une scène écrite à la main n'est jamais écrasée
        sortie.write_text(html, encoding="utf-8")
    hosts.append(f'      <div id="{sid}" class="clip scene-host" data-composition-id="{sid}" data-composition-src="compositions/{sid}.html" '
                 f'data-start="{s["debut"]}" data-duration="{d}" data-track-index="2" data-track-kind="graphics" data-width="{W}" data-height="{H}"></div>')
    comps += 1

def page_at(t):
    for s in SCENES:
        if s["debut"] <= t < s["fin"]:
            return s.get("page", "partage")
    return SCENES[-1].get("page", "partage") if SCENES else "visage"

# ---------- Sous-titres (mots de la voix, temps de la vidéo) ----------
MOTS = json.loads((BASE / PLAN["mots"]).resolve().read_text(encoding="utf-8")) if PLAN.get("mots") else []
MOTS = [{"texte": w.get("text", w.get("texte", "")).strip(), "debut": float(w["start"] if "start" in w else w["debut"]),
         "fin": float(w["end"] if "end" in w else w["fin"])} for w in MOTS if (w.get("text") or w.get("texte", "")).strip()]
groupes = []
if CAPS != "aucun" and MOTS:
    taille = {"mot-unique": 1, "bandeau": 3, "mot-geant": 4, "karaoke": 5, "classique": 7}.get(CAPS, 1)
    cur = []
    for i, w in enumerate(MOTS):
        cur.append(w)
        pause = i + 1 < len(MOTS) and MOTS[i + 1]["debut"] - w["fin"] > 0.35
        court = CAPS == "mot-unique" and len(w["texte"]) <= 2 and i + 1 < len(MOTS) and not pause
        if (len(cur) >= taille or pause or i == len(MOTS) - 1) and not court:
            groupes.append(cur); cur = []
    for gi, g in enumerate(groupes):
        nxt = groupes[gi + 1][0]["debut"] if gi + 1 < len(groupes) else min(TOTAL, g[-1]["fin"] + 0.4)
        groupes[gi] = {"mots": g, "debut": round(g[0]["debut"], 3), "fin": round(min(nxt, g[-1]["fin"] + 0.6), 3)}
    def g_html(G):
        txt = [w["texte"] for w in G["mots"]]
        if CAPS == "karaoke":
            return '<div class="g">' + " ".join(f"<span>{t}</span>" for t in txt) + "</div>"
        if CAPS == "bandeau":
            return f'<div class="g">{" ".join(txt).upper()}</div>'
        if CAPS == "mot-geant":
            return f'<div class="g"><small>{" ".join(txt[:-1])}</small><b>{txt[-1]}</b></div>'
        return f'<div class="g">{" ".join(txt)}</div>'
    segs, prev = [], None  # position des sous-titres selon la mise en page
    for s in SCENES:
        p = s.get("page", "partage")
        if p != prev:
            segs.append((s["debut"], round(CAP_TOP.get(p, 0.7) * H)))
            prev = p
    cap_html = f"""<template>
  <style>
{FONTS_CSS}
{KIT_CSS}
    #root {{ {VARS} }}
    #root .caps {{ top: 0; }}
  </style>
  <div id="root" data-composition-id="captions" data-width="{W}" data-height="{H}">
    <div class="caps cap-{ {"mot-unique": "one", "karaoke": "kara", "bandeau": "band", "mot-geant": "geant", "classique": "cls"}.get(CAPS, "one") }">{"".join(g_html(G) for G in groupes)}</div>
  </div>
  <script>
{KIT_JS}
    (() => {{
      const tl = gsap.timeline({{ paused: true }});
      const R = document.querySelector('[data-composition-id="captions"]');
      const caps = R.querySelector(".caps");
      {"".join(f'tl.set(caps, {{ y: {y} }}, {t});' for t, y in segs)}
      kitSousTitres(tl, R, {json.dumps(CAPS)}, {json.dumps([{"debut": G["debut"], "fin": G["fin"], "mots": [{"debut": w["debut"], "fin": w["fin"]} for w in G["mots"]]} for G in groupes])});
      tl.set({{}}, {{}}, {TOTAL});
      window.__timelines["captions"] = tl;
    }})();
  </script>
</template>
"""
    (PROJ / "compositions" / "captions.html").write_text(cap_html, encoding="utf-8")

# ---------- Caméra : une seule vidéo, déplacée entre plein cadre, carte et caché ----------
CAM = PLAN.get("camera")
cam_html, cam_js = "", []
if CAM:
    ratio = float(CAM.get("ratio", 16 / 9))
    if ratio >= W / H:
        H0, W0 = H, round(H * ratio)
    else:
        W0, H0 = W, round(W / ratio)
    fx, fy = CAM.get("cadrage", [0.5, 0.4])  # point du rush à garder au centre en plein cadre (visage)
    def geo(page):
        if page == "partage":
            cx, cy, cw, ch = CARTE
            k = max(cw / W0, ch / H0)
            x, y = cx + (cw - W0 * k) / 2, cy + (ch - H0 * k) * 0.35
            return dict(x=round(x, 1), y=round(y, 1), scale=round(k, 4)), f"inset({cy}px {W - cx - cw}px {H - cy - ch}px {cx}px round {RAYON}px)", 1
        x = min(0, max(W - W0, W / 2 - W0 * fx))
        y = min(0, max(H - H0, H / 2 - H0 * fy))
        return dict(x=round(x, 1), y=round(y, 1), scale=1), "inset(0px 0px 0px 0px round 0px)", (0 if page == "motion" or page == "media" else 1)
    prev = None
    for s in SCENES:
        p = s.get("page", "partage")
        if p == prev:
            continue
        g, clip, op = geo(p)
        g_js = ", ".join(f"{k}: {v}" for k, v in g.items())
        if prev is None:
            cam_js += [f'tl.set("#camv", {{ {g_js} }}, 0);', f'tl.set("#camclip", {{ clipPath: "{clip}", opacity: {op} }}, 0);']
        else:
            t0 = max(0, s["debut"] - 0.15)
            cam_js += [f'tl.to("#camv", {{ {g_js}, duration: 0.3, ease: "power3.inOut" }}, {t0});',
                       f'tl.to("#camclip", {{ clipPath: "{clip}", opacity: {op}, duration: 0.3, ease: "power3.inOut" }}, {t0});']
        prev = p
    ms = f' data-media-start="{CAM["debut_media"]}"' if CAM.get("debut_media") else ""
    cam_html = (f'      <div id="camclip"><div id="camwrap"><video id="camv" class="clip" src="{CAM["src"]}" data-start="0" data-duration="{TOTAL}"{ms} '
                f'data-track-index="1" muted playsinline style="position:absolute;left:0;top:0;width:{W0}px;height:{H0}px;transform-origin:0 0"></video></div></div>')

# ---------- Sons ----------
sons = []
if PLAN.get("voix"):
    sons.append(f'      <audio id="voix" class="clip" src="{PLAN["voix"]}" data-start="0" data-duration="{TOTAL}" data-track-index="10" data-volume="1"></audio>')
mu = PLAN.get("musique")
if mu:
    sons.append(f'      <audio id="musique" class="clip" src="{mu["src"]}" data-start="0" data-duration="{TOTAL}" data-track-index="11" data-volume="{mu.get("volume", 0.2)}" data-fade-out="{mu.get("fondu", 1.2)}"></audio>')
for i, fx in enumerate(PLAN.get("sfx", [])):
    sons.append(f'      <audio id="fx{i:03d}" class="clip" src="{fx["src"]}" data-start="{fx["t"]}" data-duration="{fx.get("duree", 1.5)}" data-track-index="{30 + i % 8}" data-volume="{fx.get("volume", 0.4)}"></audio>')

index = f"""<!doctype html>
<html lang="fr">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
{FONTS_CSS}
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: {W}px; height: {H}px; overflow: hidden; background: {BG}; }}
      #root {{ position: relative; width: 100%; height: 100%; background: {BG}; }}
      #camclip {{ position: absolute; inset: 0; z-index: 5; overflow: hidden; }}
      #camwrap {{ position: absolute; inset: 0; }}
      .scene-host {{ z-index: 10; }}
      .captions-host {{ z-index: 20; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="{W}" data-height="{H}">
{cam_html}
{chr(10).join(hosts)}
{'      <div id="captions" class="clip captions-host" data-composition-id="captions" data-composition-src="compositions/captions.html" data-start="0" data-duration="' + str(TOTAL) + '" data-track-index="3" data-track-kind="captions" data-width="' + str(W) + '" data-height="' + str(H) + '"></div>' if groupes else ""}
{chr(10).join(sons)}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      {chr(10).join("      " + l for l in cam_js).strip()}
      tl.set({{}}, {{}}, {TOTAL});
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
(PROJ / "index.html").write_text(index, encoding="utf-8")
print(f"{comps} scènes, {len(groupes)} groupes de sous-titres, {len(sons)} sons -> {PROJ}")
