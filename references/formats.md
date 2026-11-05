# Les 5 formats de vidéo

Chaque vidéo appartient à un format. Le format décide de la mise en page, du rythme et de la place du motion
design. Le profil dit quel format la personne utilise par défaut ; une vidéo peut en changer si on le demande.
Mesures en 1080x1920 (9:16). En 16:9 (1920x1080), mêmes règles, proportions adaptées.

## F1. Face caméra fixe, motion design autour

La personne parle, **la caméra ne bouge pas** (ou très peu : une poussée lente). Le motion design apparaît
autour d'elle aux moments clés : il suit ses gestes, sa main qui montre, ses mots.

- Cadre : plein écran, la personne au centre ou légèrement décalée pour laisser une zone libre.
- Graphismes : cartes, chiffres, logos, mots clés posés dans l'espace libre, **du côté où elle montre**.
  Un élément qui « sort de sa main » part de la position de la main (repère-la sur les images fixes).
- Option : mots géants **derrière** la personne (détourage), la tête passe devant le texte.
- Sous-titres : en bas ou au niveau du torse, jamais sur la bouche ; masqués quand un titre dit la même chose.
- Rythme : un graphisme toutes les 3 à 6 s, rien entre les deux pour laisser respirer le visage.
- Coupes : celles du dérush ; zoom alterné 1,0 / 1,1 à chaque raccord pour masquer les sauts.

## F2. Navigation (plein visage, écran partagé, motion design)

La vidéo **navigue** entre plusieurs mises en page selon ce qui est dit, en coupe franche ou en transition rapide
(0,3 s, le visage se réduit dans sa carte).

- **Mode A, écran partagé** (environ 70 % du temps) : motion design en haut sur un fond uni (souvent avec une
  grille fine), sous-titre d'un seul mot au milieu, caméra dans une carte arrondie en bas. Option forte : la tête
  détourée **dépasse** du bord haut de la carte.
- **Mode B, plein visage** (environ 30 %) : recadrage serré 9:16, sous-titre au niveau du torse, aucun graphisme.
  Pour les phrases personnelles, les avis, les punchlines, les transitions.
- Option **mode C, motion design plein écran** : quand l'explication demande toute la place (schéma, liste longue).
- Règle mesurée : un passage en plein visage toutes les 6 à 10 s, durée 0,8 à 5 s ; chaque bascule tombe au
  **début d'une phrase**. La fin est en mode A avec l'appel à l'action.

## F3. Montage complet (rushs, B-roll, storytelling)

Vlog, documentaire, présentation de produit, reportage : plusieurs plans, plusieurs lieux, du B-roll.

- Coupes sur le rythme de la voix ou de la musique ; plans de B-roll de 0,5 à 3 s posés **sur le mot qui les
  nomme** (« la ville », « mon bureau », « l'argent »).
- B-roll : d'abord celui de la personne, sinon des vidéos libres trouvées en ligne ([broll-medias.md](broll-medias.md)).
- Étalonnage commun à tous les plans pour qu'ils aient l'air tournés par la même caméra ([image-son.md](image-son.md)).
- Titres, sous-titres et motion design plus discrets : l'image porte le récit.
- Musique plus présente (elle tient le rythme), bruitages d'ambiance réels (rue, clavier, porte).

## F4. Motion design complet, sans visage

Une voix off (fournie, enregistrée, ou générée gratuitement avec `scripts/voix.py`) et uniquement du motion design.

- Découpage en scènes d'environ 20 mots ; **un changement visuel toutes les 1,5 à 3 s**.
- Chaque idée a son image : objet, icône, mockup de téléphone ou d'interface, chiffre, schéma, B-roll dans une carte.
- Le texte apparaît **mot par mot sur la voix**, jamais tout un paragraphe.
- Faux A-roll possible : une vidéo libre de quelqu'un qui parle, dans un téléphone ou une carte, avec de faux
  sous-titres (jamais présenté comme la vraie personne).
- La voix est fusionnée en **une seule piste** de la durée totale (plusieurs clips coupent la voix dans l'aperçu).

## F5. Capture d'écran, tutoriel, démo

Enregistrement d'écran de PC (16:9 le plus souvent), avec ou sans webcam.

- **Zooms progressifs** sur la zone où il se passe quelque chose (clic, champ rempli, résultat), panoramiques
  doux, retour au plan large entre deux actions.
- Mise en valeur : curseur agrandi ou halo sous le curseur, reste de l'écran assombri ou flouté.
- Écran dans un cadre (fenêtre arrondie avec ombre) sur un fond sobre aux couleurs du profil.
- Temps morts coupés ou accélérés (chargements, hésitations de la souris).
- Webcam : petite carte arrondie dans un coin, traitée à part (lumière, peau).
- Image : **pas** de débruitage ni de grain sur l'écran (le texte devient baveux) ; agrandissement net pour un
  texte lisible ([image-son.md](image-son.md) § 3).

## Vidéo longue vers plusieurs shorts

Ce n'est pas un format mais une tâche : trouver dans une vidéo longue les passages de 20 à 60 s qui tiennent seuls
(une idée, une accroche, une chute), les noter, en proposer la liste avec leur accroche, puis monter chaque short
dans le format du profil.
