# Le style Cutora par défaut (la base de connaissances)

Ce style sert de point de départ quand la personne n'a rien choisi, a passé des étapes, ou a cliqué « Style Cutora
par défaut ». Il est tiré de deux références mesurées plan par plan (des reels de créateur tech en format
navigation, et une publicité en motion design sur voix off) et de montages validés. Chaque règle a été vérifiée sur
une vraie vidéo.

Il est volontairement **premium et sobre** : fond sombre, une seule couleur forte, mots importants qui ressortent,
mouvements doux qui se posent, aucun effet gratuit. C'est ce qui vieillit le mieux et ce qui est le plus rarement
refusé. Le profil de la personne le remplace point par point.

## 1. Charte

Par défaut, ce sont les couleurs de la marque Cutora :

| Rôle | Couleur |
|---|---|
| Fond (noir mat) | #1A1A1A |
| Texte (blanc cassé) | #FDFBF7 |
| Couleur forte (cuivre) | #B87333, survol ou halo plus clair #D08B44 |
| Couleur 2 (terre cuite) : idée opposée, mots négatifs, éléments barrés | #D96236 |
| Second fond (bleu marine) pour les scènes de contraste | #1F355E, ou #141A26 plus sombre |
| Cartes et blocs | #212121, bordure fine #2E2E2E |

- Fond **noir mat** avec une **grille fine** (carreaux de 40 à 60 px, traits blancs à 6 % d'opacité) visible
  seulement au centre, autour du sujet (masque radial). Jamais de fond uni plat sans texture.
- **Une couleur forte** (le cuivre, ou la couleur de marque de la personne) réservée aux mots importants, aux
  étiquettes, aux halos. Blanc cassé pour le texte. La terre cuite seulement pour une idée opposée (mots négatifs,
  contre-argument), éventuellement sur le second fond marine le temps de la scène.
- **Halo** doux sur chaque média (carte, téléphone, capture) : ombre de 30 à 60 px de flou, blanc bleuté sur noir,
  à la couleur forte quand l'élément est mis en avant.

## 2. Typographie : trois voix

1. **Police forte, pour les titres et les mots forts** : Montserrat 800 à 900 (la police de Cutora), approche
   -0,02em, **grande** : la ligne principale fait au moins 70 px de haut en 1080 de large. Deux lignes : la première
   plus petite (mots faibles), la seconde plus grande avec les mots importants.
2. **Police d'accent, pour le mot clé** : à la couleur forte **et** en **serif italique** (Playfair Display italique)
   glissé dans le titre. Un ou deux mots par titre, jamais plus. Variantes : pavé de couleur derrière le mot, ou
   trait de couleur qui se dessine dessous de gauche à droite.
3. **Police normale, pour les petits mots et la narration** : Montserrat 400 à 500, blanc cassé.

Texte en **escalier** possible : petit mot au-dessus, mot clé plus gros en dessous, décalé.

## 3. Apparition du texte (la signature)

- **Mot par mot, sur la voix** : chaque mot arrive à l'instant où il est prononcé.
- **Flou vers net** : flou de 10 à 12 px vers 0, opacité 0 vers 1, légère montée (échelle 0,85 vers 1 ou 14 px vers
  le haut), 5 à 8 images, ease rapide qui se pose (`power3.out`).
- Sortie : le bloc entier disparaît d'un coup ou en flou rapide (0,2 s). Jamais lettre par lettre en sortie.

## 4. Mise en page selon le format

- **Avec visage (F1, F2)** : alternance écran partagé et plein visage (voir [formats.md](formats.md) F2) : motion
  design en haut, sous-titre d'un mot au milieu, caméra en carte arrondie en bas avec la tête qui dépasse ; plein
  visage pour les avis et les punchlines, un passage toutes les 6 à 10 s.
- **Sans visage (F4)** : un « tableau » toutes les 3 s environ, mais un changement visuel toutes les 1,5 à 2,5 s
  (un mot, un zoom, un objet). Écran vide avec seulement le texte de temps en temps : la respiration.

## 5. Vocabulaire de motion design

Par ordre de fréquence dans les références :

1. **Cartes à coins arrondis** (rayon 24 à 40 px) qui contiennent captures, B-roll, photos. Elles entrent en flou,
   glissent, grossissent jusqu'au plein cadre quand l'image doit prendre toute la place.
2. **Téléphone** (mockup réaliste avec halo) qui montre une vidéo, un profil, une appli. Il change de taille à chaque
   phrase : grand à l'ouverture, petit quand le texte domine. Deux téléphones côte à côte pour comparer.
3. **Hub d'icônes en orbite** autour d'une étiquette centrale : il revient entre chaque partie, l'élément suivant
   grossit et monte pour devenir l'en-tête de la partie.
4. **Étiquettes** (pavé de couleur, texte blanc) épinglées sur les côtés d'une capture, une par mot clé.
5. **Flèches dessinées** qui se tracent vers ce qu'il faut regarder, avec une série de petits tics pendant le tracé.
6. **Saisie en direct** : un champ où le texte se tape au rythme de la voix, puis la réponse apparaît.
7. **Chiffres** dans le titre ou en compteur, pendant qu'une image montre la preuve.
8. **Logos qui se relient** puis qui orbitent.
9. **Curseur** qui clique sur l'élément nommé, **bouton** d'appel à l'action qui arrive du bas en flou.
10. **Objets décoratifs** dans les coins, flous (profondeur de champ), qui dérivent lentement : un par scène, qui
    illustre l'idée. Vraies photos détourées ou formes dessinées, **jamais d'emoji**.

## 6. Mouvement

- Une **poussée lente** continue (échelle 1 vers 1,05 sur la durée de la scène) sur l'élément principal : rien n'est
  jamais figé.
- Changement de carte : l'ancienne sort sur le côté avec un flou de mouvement, la nouvelle entre de l'autre côté.
- Zooms **par paliers** synchronisés sur les mots (zooms secs), pas de zoom continu qui flotte.
- Rotation 3D légère possible (un téléphone posé qui se redresse, une capture inclinée en perspective qui glisse).
- **Pas** de glitch, de tremblement, ni de transition « effet » : coupes franches et entrées propres.

## 7. Rythme

- Bascule de mise en page **au début d'une phrase**, jamais au milieu d'un mot.
- Dérush serré : silences coupés avec marges (0,08 s avant, 0,16 s après), dernière bonne prise gardée.

## 8. Son

- **Nappe calme et continue** sous toute la vidéo (pad ou arpège doux, sans batterie marquée), volume 0,2 après
  normalisation : elle s'entend mais ne gêne jamais la voix. Pas d'horreur, pas de stridences.
- **Whoosh aigu court** (0,2 s, souffle 6 à 16 kHz) sur les bascules de mise en page et les grandes entrées.
- **Impact grave** discret seulement sur les vrais changements de partie (3 à 6 par minute au plus).
- **Petits clics** sur le curseur et le bouton ; **tics** pendant le tracé d'une flèche ; **frappe de clavier**
  pendant une saisie. Pas de son sur chaque élément qui entre.
- Voix à -16 LUFS, crête sous -1,5 dBTP.

## 9. Fin et appel à l'action

- Dernière scène en écran partagé ou en motion design : l'appel à l'action écrit en grand (mot clé à la couleur
  forte), un bouton ou le profil du réseau redessiné à l'identique (photo, nom, chiffres réels, bio), lisible au
  moins 2 secondes.

## 10. Ce que le style par défaut ne fait jamais

Emoji, police fantaisie, plus de deux couleurs fortes, texte qui couvre la bouche, éléments minuscules perdus dans
le vide, transitions « effet », musique d'horreur, son sur chaque apparition, logos imités.
