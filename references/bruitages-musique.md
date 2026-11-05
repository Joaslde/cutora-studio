
# Bruitages et musique des montages

Objectif : des sons **réels, cinématiques et contextuels** (le son de l'objet ou de l'action qu'on voit), jamais
« amusants » ou génériques par défaut. Chaque son tombe sur l'image exacte de son action. Musique : une nappe
sous toute la vidéo, à faible volume mais audible.

## 1. Quelle source choisir (je décide moi-même, dans cet ordre)

| Besoin | Source | Pourquoi |
|---|---|---|
| Un son **signature** de la vidéo de référence (tics d'une flèche, motif précis) | **Synthèse** d'après son spectrogramme (`<skill>/scripts/synth_tick.py`) | Fidèle à la référence sans copier son fichier |
| Un son **réel et précis** (ciseaux, déclencheur, clavier, papier, crayon, porte, foule...) | **Openverse CC0** (`<skill>/scripts/openverse.py`) | Vrais enregistrements Freesound, gratuits, sans crédit en CC0 |
| Openverse ne répond pas (504) ou bloque (429), ou besoin d'un son « cinéma » (impact de bande-annonce, riser, whoosh tunnel) | **Mixkit** (`<skill>/scripts/mixkit_sfx.py`) | Fiable, sons pro, licence gratuite commerciale sans crédit |
| Clic, pop, whoosh d'interface **neutres**, ou travail hors ligne | Bibliothèque **HyperFrames** intégrée : dossier `audio/assets/sfx/` du skill `media-use` (une vingtaine de sons, `manifest.json`) | Immédiate, mais sons « classiques » : à réserver aux UI simples |
| Musique de fond | Nappe **composée** (`<skill>/scripts/synth_bed.py`, calée sur les scènes) ou piste Mixkit / Openverse (`category=music`) | Voir § 4 |

Règles :
- Jamais deux fois le même son générique d'affilée sur des actions différentes : un son par **sens** (ce qu'on voit).
- Openverse : licence `cc0` seulement (CC BY oblige à créditer). Limite gratuite environ 200 recherches par jour,
  requêtes d'**un ou deux mots**, pas de boucles de relance serrées (sinon 429 pour la journée).
- Mixkit : catégories `mixkit.co/free-sound-effects/<categorie>/` (transition, cinematic, impact, click, camera,
  clock, paper, typing, swoosh...), fichier `assets.mixkit.co/active_storage/sfx/<id>/<id>-preview.mp3`.
- Un pack acheté ou offert (ex. pack Instagram) : seulement si sa licence autorise l'usage commercial ; le ranger
  dans `<atelier>/_sons/<nom-du-pack>/` avec sa licence.
- Écrire un `CREDITS.md` à côté des sons (source, id, licence).

## 2. Analyser la référence avant de choisir

1. Spectrogramme zoomé sur chaque moment clé :
   `ffmpeg -ss A -to B -i ref.wav -lavfi "showspectrumpic=s=1400x500:legend=1:scale=log:fscale=lin:stop=11000" zoom.png`
2. Lire : impact grave (bande < 120 Hz), whoosh (large bande qui monte et descend), tics (traits verticaux
   courts répétés : compter, mesurer l'espacement), nappe musicale (lignes horizontales continues).
3. Noter pour chaque son : instant, durée, nombre de coups, bande de fréquence. Le reproduire au même endroit
   par rapport à la voix.

## 3. Découper et caler

- Mesurer chaque son : `python scripts/measure.py <dossier>` donne durée, attaque (50 % de l'enveloppe), pic, fin.
  Un son long ou à plusieurs parties : regarder sa forme d'onde
  (`showwavespic`) et **découper** le bon passage (`ffmpeg -ss -t` + fondus) avant de le placer.
- Point de synchro :
  - impact, clic, coup, déclencheur : l'**attaque** ;
  - whoosh, riser, montée : le **pic** (le moment le plus fort) ;
  - son continu (clavier, rembobinage) : le **début**, ou son pic au milieu de l'action.
- Placement : `debut_audio = instant_action - point_synchro + 0.033` (une image après l'action à 30 i/s).
- Pistes : une piste libre par son qui se chevauche (allocation automatique).

## 4. Musique

- Une nappe continue sous toute la vidéo, **pas d'horreur** (pas de stridences, pas de cris, pas de piano dissonant).
- « Suspense » pour une pub = pulsation de basse en croches discrète + nappe tenue + cordes aiguës en trémolo,
  avec des sections qui suivent le montage (étouffée au début, ouverture au point de bascule, suspension avant la
  phrase clé, résolution sur le CTA). `<skill>/scripts/synth_bed.py` en est un modèle à adapter (accords, temps des
  sections).
- Vérifier l'équilibre : sur un téléphone, une nappe à 90 % sous 400 Hz est inaudible. Viser du médium
  (400 à 1200 Hz) audible.
- Niveau : piste normalisée à -16 LUFS puis volume 0,2 à 0,25 sous la voix.

## 5. Vérifier le mixage sans rendre la vidéo

`python scripts/mixcheck.py <projet>/index.html` reconstruit le mixage avec ffmpeg (mêmes débuts, durées,
volumes, fondus) et donne la loudness intégrée et la crête. Cible maison : **-16 LUFS**, crête sous **-1,5 dBTP**
après limiteur final. Si une crête dépasse, trouver l'instant et baisser le son responsable (pas toute la piste).

Je ne peux pas écouter : je mesure. Toujours le dire à l'utilisateur et lui laisser juger à l'oreille.

## 6. Ce que le profil doit retenir

- La musique choisie (caractère, source, volume) et celles refusées, avec ses mots (« ça fait horreur »,
  « c'était mieux avant »).
- La densité des bruitages qu'il supporte : un son sur chaque élément qui entre est presque toujours refusé.
- Les sons qui lui plaisent (gardés dans `profils/<nom>/sons/` avec leur licence) pour les réutiliser.
