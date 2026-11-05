# Contrôle qualité avant de montrer

L'utilisateur ne doit jamais être le premier à voir un défaut. Avant **chaque** aperçu, passe cette liste, puis
les acquis du profil un par un. Note dans ton message d'aperçu ce que tu n'as pas pu vérifier.

## 1. Les acquis du profil

Ouvre `acquis.md` et applique la colonne « vérification » de chaque acquis. Un seul acquis raté = on ne montre pas.

## 2. Image (sur les images fixes de `npx hyperframes snapshot`)

- [ ] Les proportions de la référence ou du profil : titres et éléments **grands**, rien de petit perdu dans le
      vide. Mesurer en pixels, pas à l'œil.
- [ ] Texte lisible sur un téléphone : contraste, taille, rien ne passe sur un fond chargé sans ombre.
- [ ] Rien n'est coupé par les bords (zones de sécurité : 60 px sur les côtés, 220 px en bas en 9:16 pour
      l'interface des réseaux).
- [ ] Sous-titres jamais sur la bouche ; pas de sous-titre qui répète un titre affiché.
- [ ] Détourage : pas de liseré clair, pas de tête coupée, masque synchronisé (regarder **pendant un geste
      rapide**, à taille réelle).
- [ ] Transitions sans flash, sans image noire, sans liseré (un zoom qui repasse sous 1 laisse un bord noir).
- [ ] Peau naturelle (ni grise, ni verte, ni orange), même couleur d'un plan à l'autre.
- [ ] Vrais logos, vraies photos, aucun emoji, aucune faute d'orthographe dans les textes.
- [ ] Rien de figé trop longtemps : un changement visuel au rythme du profil.

## 3. Temps

- [ ] Chaque animation tombe sur son mot (vérifier 3 ou 4 instants au hasard sur les images fixes, avec le mot
      prononcé à cet instant).
- [ ] Aucun mot coupé aux raccords (écouter n'est pas possible : vérifier sur l'onde que chaque coupe tombe dans
      un silence).
- [ ] La fin : appel à l'action lisible au moins 2 s, pas de coupe sèche sur le dernier mot.

## 4. Son (`python <skill>/scripts/mixcheck.py montage/index.html`)

- [ ] -16 LUFS intégrés (±1), crête sous -1,5 dBTP, aucune saturation.
- [ ] La musique s'entend sous la voix sans la gêner (volume 0,15 à 0,25 après normalisation à -16 LUFS), et du
      médium audible (pas 90 % de l'énergie sous 400 Hz).
- [ ] Chaque bruitage tombe une image après son action ; pas de son sur chaque élément qui entre.
- [ ] Le style de son du profil (calme, suspense, énergique) et aucun son déjà refusé.

## 5. Technique

- [ ] `npx hyperframes check` : zéro erreur.
- [ ] Les médias sont dans `montage/assets/`, les chemins relatifs, les crédits écrits.
- [ ] Les fichiers temporaires inutiles sont supprimés.

## 6. Le message d'aperçu

Trois à cinq lignes : ce qui a été fait, **ce qu'il faut regarder** (avec les instants), ce qui est nouveau par
rapport à ses habitudes, ce qui est incertain. Rappelle qu'il faut écouter au casque.
