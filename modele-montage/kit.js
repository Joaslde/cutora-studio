// Kit d'animation Cutora Studio (GSAP), identique à celui de la page de choix, mais calé sur le temps réel de la voix.
// Tout est déterministe (pas de hasard, pas de minuterie) : la vidéo rendue est identique à l'aperçu.
const $k = (s, r) => r.querySelector(s);
const $$k = (s, r) => [...r.querySelectorAll(s)];
const cssv = (el, n) => getComputedStyle(el).getPropertyValue(n).trim();

// Titre : les mots arrivent un par un selon le style (flou-net, glisse, machine, masque, pop)
function kitTitre(tl, root, kind, t, ecart = 0.12) {
  const ws = $$k(".ttl .w", root);
  if (!ws.length) return t;
  let fin;
  if (kind === "machine") {
    const ch = $$k(".ttl .ch", root);
    tl.fromTo(ch, { opacity: 0 }, { opacity: 1, duration: 0.01, stagger: 0.045 }, t);
    fin = t + ch.length * 0.045;
  } else {
    if (kind === "glisse") tl.fromTo(ws, { opacity: 0, y: "0.9em" }, { opacity: 1, y: 0, duration: 0.45, ease: "power3.out", stagger: ecart }, t);
    else if (kind === "masque") tl.fromTo(ws, { yPercent: 115 }, { yPercent: 0, duration: 0.5, ease: "power4.out", stagger: ecart }, t);
    else if (kind === "pop") tl.fromTo(ws, { opacity: 0, scale: 0 }, { opacity: 1, scale: 1, duration: 0.45, ease: "back.out(3)", stagger: ecart }, t);
    else tl.fromTo(ws, { opacity: 0, filter: "blur(10px)", y: "0.3em", scale: 0.9 }, { opacity: 1, filter: "blur(0px)", y: 0, scale: 1, duration: 0.42, ease: "power3.out", stagger: ecart }, t);
    fin = t + ws.length * ecart + 0.4;
  }
  const ul = $$k(".ttl .ul", root);
  if (ul.length) tl.fromTo(ul, { scaleX: 0 }, { scaleX: 1, duration: 0.35, ease: "power2.out" }, fin);
  return fin;
}

// Entrée « pop » d'un élément (flou vers net, légère montée d'échelle)
function kitPop(tl, el, t, o = {}) {
  if (!el || (el.length === 0)) return;
  tl.fromTo(el, { opacity: 0, scale: o.s ?? 0.82, filter: "blur(10px)", y: o.y ?? 0, x: o.x ?? 0, rotation: o.r0 ?? 0 },
    { opacity: 1, scale: 1, filter: "blur(0px)", y: 0, x: 0, rotation: o.r ?? 0, duration: o.d ?? 0.4, ease: o.e ?? "power3.out", stagger: o.st ?? 0 }, t);
}

// Éléments de motion design : cartes, téléphone, orbite, flèches, chiffres, étiquettes, saisie, liste, media
// m = { type, t, textes: [], medias: [], chiffre, mots_t: [] }  (mots_t : instants locaux où chaque élément arrive)
function kitMotion(tl, mz, m, dur) {
  if (!mz) return;
  const t = m.t ?? 0.5, at = (i, def) => (m.mots_t && m.mots_t[i] != null ? m.mots_t[i] : def);
  const k = m.type;
  if (k === "telephone") {
    kitPop(tl, $k(".phone", mz), t, { y: 60, s: 0.9 });
    tl.fromTo($k(".halo", mz), { opacity: 0, scale: 0.6 }, { opacity: 0.55, scale: 1.1, duration: 1.2, ease: "sine.inOut", yoyo: true, repeat: Math.max(1, Math.floor(dur / 1.2) - 1) }, t);
    tl.fromTo($k(".phone", mz), { scale: 1 }, { scale: 1.05, duration: Math.max(0.5, dur - t), ease: "none", immediateRender: false }, t + 0.4);
  } else if (k === "orbite") {
    kitPop(tl, $k(".tag", mz), t, { s: 0.3, e: "back.out(2)" });
    $$k(".ic", mz).forEach((el, i) => kitPop(tl, el, at(i, t + 0.3 + i * 0.12), { s: 0.4, e: "back.out(2)" }));
    tl.fromTo($k(".orb", mz), { rotation: 0 }, { rotation: 40, duration: dur, ease: "none" }, 0);
    $$k(".ic", mz).forEach((el) => tl.fromTo(el, { rotation: 0 }, { rotation: -40, duration: dur, ease: "none", immediateRender: false }, 0));
  } else if (k === "fleches") {
    kitPop(tl, $k(".tg", mz), t);
    tl.fromTo($k(".ar", mz), { strokeDashoffset: 70 }, { strokeDashoffset: 0, duration: 0.6, ease: "power1.inOut" }, t + 0.35);
    tl.fromTo($k(".ah", mz), { opacity: 0 }, { opacity: 1, duration: 0.08 }, t + 0.95);
  } else if (k === "chiffres") {
    tl.fromTo($$k(".br", mz), { scaleY: 0, transformOrigin: "50% 100%" }, { scaleY: 1, duration: 0.55, ease: "power3.out", stagger: 0.15 }, t);
    const c = $k(".cnt", mz), cible = parseFloat(String(m.chiffre || "85").replace(/[^\d.,-]/g, "").replace(",", ".")) || 85;
    const pre = String(m.chiffre || "+85 %").match(/^[^\d-]*/)[0], suf = String(m.chiffre || "+85 %").match(/[^\d.,]*$/)[0];
    const o = { v: 0 };
    tl.fromTo(o, { v: 0 }, { v: cible, duration: 1.2, ease: "power2.out", onUpdate: () => (c.textContent = pre + Math.round(o.v) + suf) }, t + 0.2);
  } else if (k === "etiquettes") {
    kitPop(tl, $k(".tile", mz), t);
    $$k(".tag", mz).forEach((el, i) => tl.fromTo(el, { opacity: 0, scale: 0.3, rotation: -8 }, { opacity: 1, scale: 1, rotation: i % 2 ? 3 : -3, duration: 0.4, ease: "back.out(2.5)" }, at(i, t + 0.4 + i * 0.45)));
  } else if (k === "saisie") {
    kitPop(tl, $k(".champ", mz), t);
    const s = $k(".typ", mz), n = (s.textContent || "").length;
    tl.fromTo(s, { width: 0 }, { width: "auto", duration: Math.min(2.2, 0.06 * n), ease: `steps(${Math.max(1, n)})` }, t + 0.3);
    tl.fromTo($k(".cur", mz), { opacity: 1 }, { opacity: 0, duration: 0.25, repeat: 7, yoyo: true }, t);
    kitPop(tl, $k(".rep", mz), t + 0.5 + Math.min(2.2, 0.06 * n), { y: 30 });
  } else if (k === "liste") {
    $$k(".it", mz).forEach((el, i) => kitPop(tl, el, at(i, t + i * 0.5), { x: -40, s: 1 }));
  } else if (k === "media") {
    kitPop(tl, $k(".tile", mz), t, { y: 40, s: 0.9 });
    tl.fromTo($k(".tile img, .tile video", mz), { scale: 1 }, { scale: 1.1, duration: Math.max(0.5, dur), ease: "none" }, 0);
  } else {  // cartes
    const cs = $$k(".tile", mz);
    cs.forEach((el, i) => kitPop(tl, el, at(i, t + i * 0.5), { y: 40 }));
    if (cs.length > 1) tl.to(cs[cs.length - 1], { boxShadow: "0 0 7cqw " + cssv(mz, "--acc"), duration: 0.3 }, at(cs.length - 1, t + (cs.length - 1) * 0.5) + 0.4);
  }
}

// Entrée et sortie de scène selon la transition choisie
function kitEntree(tl, root, kind) {
  if (kind === "zoom") tl.fromTo(root, { scale: 0.7, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.35, ease: "power2.out" }, 0);
  else if (kind === "glisse-flou") tl.fromTo(root, { xPercent: 100, filter: "blur(14px)" }, { xPercent: 0, filter: "blur(0px)", duration: 0.35, ease: "power2.out" }, 0);
  else if (kind === "fondu") tl.fromTo(root, { opacity: 0 }, { opacity: 1, duration: 0.5 }, 0);
}
function kitSortie(tl, root, kind, fin) {
  if (kind === "zoom") tl.to(root, { scale: 1.8, opacity: 0, duration: 0.3, ease: "power2.in" }, fin - 0.32);
  else if (kind === "glisse-flou") tl.to(root, { xPercent: -100, filter: "blur(14px)", duration: 0.3, ease: "power2.in" }, fin - 0.32);
  else if (kind === "fondu") tl.to(root, { opacity: 0, duration: 0.45 }, fin - 0.47);
}

// Sous-titres : groupes de mots avec leurs instants (temps de la vidéo)
function kitSousTitres(tl, root, kind, groupes) {
  const acc = cssv(root, "--acc");
  $$k(".g", root).forEach((g, gi) => {
    const G = groupes[gi];
    tl.set(g, { opacity: 0 }, 0).set(g, { opacity: 1 }, G.debut).set(g, { opacity: 0 }, G.fin);
    if (kind === "karaoke") $$k("span", g).forEach((s, i) => { tl.set(s, { color: acc }, G.mots[i].debut).set(s, { color: "#ffffff" }, G.mots[i].fin); });
    if (kind === "mot-unique") tl.fromTo(g, { scale: 0.85 }, { scale: 1, duration: 0.08, immediateRender: false }, G.debut);
    if (kind === "mot-geant") { const b = $k("b", g); if (b) tl.fromTo(b, { opacity: 0, scale: 0.3 }, { opacity: 1, scale: 1, duration: 0.3, ease: "back.out(2.5)", immediateRender: false }, G.mots[G.mots.length - 1].debut); }
  });
}
