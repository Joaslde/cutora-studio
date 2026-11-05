# Table de correspondance : un choix de la page, son effet exact dans la vidéo

Chaque choix de la page de choix (`choix.json`) a un effet précis dans le montage. Le générateur
(`modele-montage/build.py`) l'applique automatiquement ; cette table sert à savoir **quoi modifier** quand la personne
corrige quelque chose, et à garder la vidéo fidèle à ce qu'elle a vu sur la page. Les aperçus de la page et la vidéo
utilisent le même kit (`modele-montage/kit.css`, `kit.js`).

| Clé de `choix.json` | Valeur | Effet dans la vidéo | Où le changer |
|---|---|---|---|
| `format` | F1 à F5 | Mise en page dominante des scènes ([formats.md](formats.md)) : F1 et F3 surtout `visage` et `media`, F2 alternance `partage` / `visage`, F4 `motion` et `media`, F5 capture d'écran en `media` avec bulle caméra | `page` de chaque scène du plan |
| `couleurs.fond` | hex | Fond de toutes les scènes, voile des médias | `--bg` (build.py, `VARS`) |
| `couleurs.forte` | hex | Mot clé, étiquettes, halos, compteur, barre active, curseur de saisie | `--acc` |
| `couleurs.secondaire` | hex | Idée opposée, second plan | `--acc2` |
| `polices.forte` | famille, graisse, capitales | Ligne principale des titres, sous-titres « un mot à la fois » et « mot géant », étiquettes, chiffres | `--ff`, `--fw`, `--fmaj` |
| `polices.normale` | famille, graisse | Petits mots du titre, karaoké, classique, légendes | `--ft`, `--ftw` |
| `polices.accent` | famille, italique | Le mot clé (`cle`) quand le mot clé utilise la police d'accent | `--fa`, `--faw`, `--fai` |
| `taille_titres` | normal / grand / très grand | Ligne principale : 7,1 / 9,5 / 12,4 % de la largeur en vertical (77 / 103 / 134 px en 1080) | `TAILLE` dans build.py |
| `mot_cle` | couleur-italique / couleur / italique / pave / souligne | Classe du mot `cle` : `acc-c acc-f`, `acc-c`, `acc-f`, `acc-p`, `acc-u` (trait qui se dessine) | `titre_html` |
| `sous_titres` | mot-unique / karaoke / bandeau / mot-geant / classique / aucun | Groupes de 1 / 5 / 3 / 4 / 7 mots ; classes `cap-one`, `cap-kara`, `cap-band`, `cap-geant`, `cap-cls` ; position selon la page (55 % en partage, 76 % sur le visage en vertical) | `CAP_TOP`, `kit.css` |
| `apparition_texte` | flou-net / glisse / machine / masque / pop | `kitTitre` : flou 10 px vers net en 0,42 s ; montée de 0,9 em ; lettre par lettre (0,045 s) ; sortie d'un masque ; rebond `back.out(3)` | `kit.js` |
| `transitions` | coupe / zoom / glisse-flou / fondu | `kitEntree` et `kitSortie` de chaque scène : rien ; échelle 0,7 vers 1 ; glissement latéral avec flou 14 px ; fondu 0,5 s | `kit.js` |
| `rythme` | calme / naturel / rapide | Écart entre les mots du titre (0,18 / 0,12 / 0,08 s) ; et surtout, dans le plan : une scène toutes les 4 à 6 s / 2 à 4 s / 1 à 2 s | `ECART`, découpage du plan |
| `motion_design` | liste | Les `type` de motion à utiliser en priorité dans le plan, dans cet ordre de préférence | `motion.type` des scènes |
| `musique` | calme / suspense / energique / aucune | Nappe composée (`scripts/synth_nappe_calme.py`, `synth_bed.py`) ou piste libre ([bruitages-musique.md](bruitages-musique.md)), volume 0,2 | `musique` du plan |
| `bruitages` | discrets / marques / aucun | Discrets : un whoosh sur les changements de page et un son sur 2 ou 3 vrais moments. Marqués : en plus, un son sur chaque entrée de carte, étiquette, chiffre | `sfx` du plan |
| `references` | liens | Analysées ([analyse-reference.md](analyse-reference.md)) ; leurs mesures complètent ou remplacent les valeurs par défaut | `style.md` |

## Quand la personne corrige

| Elle dit | Tu changes |
|---|---|
| « Les titres sont trop petits / trop gros » | `taille_titres` dans `style.md` (et la ligne `TAILLE` si une valeur intermédiaire est demandée) |
| « Je ne vois pas les mots importants » | `mot_cle` vers `pave` ou `couleur-italique`, ou une couleur forte plus contrastée |
| « Les sous-titres cachent le visage » | `CAP_TOP` de la page `visage` (plus bas), ou `sous_titres` vers `classique` |
| « Ça va trop vite / trop lent » | Le découpage du plan (durée des scènes), puis `rythme` |
| « Les animations sont trop molles » | `apparition_texte` vers `pop` ou `masque`, `transitions` vers `coupe` |
| « Je veux ma police » | `polices` (fichier `.woff2` de sa police dans `assets/fonts/` et la famille dans le style) |

Chaque correction qui vaut pour la suite est écrite dans `styles/<style>/style.md` ([apprentissage.md](apprentissage.md)).
