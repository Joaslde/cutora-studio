
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
| Musique de fond | **Catalogue du skill** (`musique/catalogue.json`, choisi par `scripts/musique.py`), nappe composée en secours | Voir § 4 |

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

## 4. Musique de fond

Le skill a son **catalogue** : `musique/catalogue.json`, plusieurs centaines de morceaux Mixkit (licence gratuite,
usage commercial compris, sans crédit obligatoire), chacun classé (ambiances, instruments, genres) et **mesuré**
(tempo, énergie, régularité, voix chantée probable, début utile). Les mesures remplacent l'oreille : tu ne peux pas
écouter, le catalogue l'a fait pour toi. Ne prends jamais un morceau au hasard ni le premier venu.

### 4.1 Lire la vidéo avant de chercher

Avant toute recherche, écris en 3 lignes ce que la vidéo demande, d'après **trois sources** :

1. **Le script** (transcription) : le sujet, et surtout le ton. Une confidence, une méthode, une alerte, une
   réussite, une blague ? Le message final (rassurer, pousser à agir, faire réfléchir) ?
2. **Les images** (planches de la vidéo ou captures) : visage posé ou en mouvement, écran partagé, extérieur, bureau,
   couleurs chaudes ou froides, luxe ou quotidien.
3. **Le rythme** : débit de parole (mots par minute dans la transcription), nombre de coupes par minute du montage
   prévu, durée. Débit lent et peu de coupes : 60 à 95 BPM. Débit normal : 90 à 115. Montage nerveux : 110 à 140.

Traduis ensuite en **une ou deux familles** (`python <skill>/scripts/musique.py familles` les liste) : calme,
inspirant, motivant, pro, reflexion, suspense, sombre, epique, leger, decale, tech, chill, elegant, dramatique,
festif. Exemple : « dire non sans culpabiliser » : récit personnel puis déclic, débit posé, visage fixe :
`reflexion` puis `inspirant`, 75 à 100 BPM, énergie basse.

Si le style de la personne précise déjà une musique (style.md, gouts.md), il passe avant ta lecture.

### 4.2 Choisir dans le catalogue

```powershell
python <skill>/scripts/musique.py choisir <projet> --familles reflexion,inspirant --tempo 75-100 --energie basse --duree <durée de la vidéo> --profil <atelier>/profils/<nom>
```

Options utiles : `--instruments piano,strings`, `--genres corporate-music`, `--eviter dark,scary` (ce que la personne
a refusé), `--n 8`. Le script écarte les morceaux **déjà utilisés** par cette personne, ceux avec une voix chantée
(elle se bat avec la voix off), garde un seul morceau par auteur pour que la sélection soit variée, et explique
chaque choix. Il écrit `<projet>/musique/ecoute.html`.

### 4.3 Faire écouter, sous la voix

1. Ouvre `ecoute.html` pour la personne (chaque morceau démarre à son début utile).
2. Pour les 2 ou 3 favoris, fabrique un **essai sous la vraie voix**, car une musique seule et une musique sous une
   voix sont deux choses :
   `python <skill>/scripts/musique.py essai <projet> <id> --voix <voix.wav> --duree 30`
3. Demande par une question à choix : « Laquelle on garde ? 1, 2, 3, ou d'autres propositions ». Si la personne
   n'aime aucune, demande en un mot ce qui ne va pas (trop triste, trop joyeux, trop présent, trop lent) et relance
   avec une famille ou un tempo différent.
4. Une fois choisi : `python <skill>/scripts/musique.py prendre <projet> <id> --profil <dossier du profil>`
   (téléchargement, note dans `musiques-utilisees.json` pour ne jamais la resservir, ligne dans `CREDITS.md`).

En mode autonome (la personne a dit « choisis pour moi » ou son autonomie le permet), prends le premier du
classement, annonce-le en une ligne avec la raison, et propose de changer.

### 4.4 Placer la musique

- Commencer au **début utile** du morceau (mesuré, pas de silence d'entrée), fondu d'entrée de 1 à 2 s.
- Morceau plus court que la vidéo : enchaîner un second morceau de la même famille au point de bascule du script
  (fondu croisé de 2 s), plutôt qu'une boucle qui s'entend.
- Respiration : baisser la musique d'environ 3 dB sous les phrases clés, la remonter dans les silences et les
  transitions, couper ou suspendre une seconde avant la révélation.
- Fin : sur le CTA ou la dernière phrase, fondu de sortie de 2 à 3 s, jamais une coupe sèche.
- Niveau : piste normalisée à -16 LUFS, puis volume 0,3 à 0,4 sous la voix (environ 8 à 10 dB plus bas que la voix). Plus bas, la musique
  disparaît sur les haut-parleurs d'un téléphone ou d'un ordinateur : la personne croit qu'il n'y en a pas. Pas d'horreur (stridences, cris,
  piano dissonant) sauf demande explicite.
- Sur téléphone, une musique à 90 % sous 400 Hz est inaudible : préférer un morceau avec du médium.

### 4.5 Nappe composée (secours)

Si rien ne convient dans le catalogue, ou pour une pub très calée sur l'image : nappe composée
(`<skill>/scripts/synth_bed.py`, `synth_nappe_calme.py`), sections qui suivent le montage (étouffée au début,
ouverture au point de bascule, suspension avant la phrase clé, résolution sur le CTA).

## 5. Vérifier le mixage sans rendre la vidéo

`python scripts/mixcheck.py <projet>/index.html` reconstruit le mixage avec ffmpeg (mêmes débuts, durées,
volumes, fondus) et donne la loudness intégrée et la crête. Cible maison : **-16 LUFS**, crête sous **-1,5 dBTP**
après limiteur final. Si une crête dépasse, trouver l'instant et baisser le son responsable (pas toute la piste).

Je ne peux pas écouter : je mesure. Toujours le dire à l'utilisateur et lui laisser juger à l'oreille.

## 6. Ce que le profil doit retenir

- La musique choisie (famille, id, volume) et celles refusées (avec leur id et la raison), avec ses mots (« ça fait horreur »,
  « c'était mieux avant »).
- La densité des bruitages qu'il supporte : un son sur chaque élément qui entre est presque toujours refusé.
- Les sons qui lui plaisent (gardés dans `profils/<nom>/sons/` avec leur licence) pour les réutiliser.
