# Découvrir et créer un style (couche 1)

But : en 5 à 20 minutes, en savoir assez sur le goût de la personne pour que le **premier montage soit déjà
bluffant**. La plupart des gens ne savent pas décrire un style de montage, et beaucoup n'ont pas d'avis tant qu'on ne
leur montre rien. Donc on **montre**, ils **pointent**.

Une personne peut avoir **plusieurs styles** (ses reels, ses pubs, ses tutos). Chaque style a son dossier.

## 1. Les dossiers

```text
<atelier>/profils/<personne>/
├── acquis.md  gouts.md  consignes.md  journal.md     valables pour tous ses styles
├── charte/   broll/   sons/                          ses fichiers (logo, polices, photos, plans, sons aimés)
└── styles/
    └── <style>/                                      un dossier par style
        ├── style.md        le style écrit (modèle : profil-modele/style.md)
        ├── acquis.md       les acquis propres à ce style
        ├── choix.json      tout ce qu'il a fait sur la page de choix
        └── references/     les analyses de ses vidéos modèles
```

Personne nouvelle : copie `<skill>/profil-modele/` vers `<atelier>/profils/<personne>/` (sans `style.md`), et
mets `profil_actif` à jour dans `~/cutora-studio.json`.

## 2. La page de choix (l'onboarding visuel)

Lance-la **en arrière-plan** (elle attend que la personne ait fini) :

```powershell
python <skill>/scripts/choix_serveur.py --profil "<atelier>/profils/<personne>"
```

Elle s'ouvre dans le navigateur (`http://localhost:8765`, le port suivant s'il est pris). Dis à la personne :
« Je t'ai ouvert une page dans ton navigateur. Choisis ce qui te plaît, passe ce que tu veux, et clique sur
Enregistrer à la fin. Je m'occupe du reste. »

La page est aux couleurs de Cutora (charte de la marque, Montserrat, logo). **Chaque carte est une mini-vidéo
animée qui montre le résultat de cette option**, combinée aux choix déjà faits, sans qu'il ait besoin de cliquer
pour voir : les polices, les couleurs, les tailles, les animations et les mises en page changent réellement d'une
carte à l'autre.

Ce que la page propose, dans l'ordre (chaque étape peut être **passée**, ou remplie par **« Choisis pour moi »**,
qui prend la recommandation de l'ambiance choisie) :

| Étape | Ce qu'on y choisit |
|---|---|
| Départ | **Je choisis mon style** (pas à pas), **J'ai une vidéo modèle** (va droit aux liens), **Style Cutora par défaut** (va droit au récapitulatif). Et le **nom du style**. |
| Ambiance | Une ambiance complète qui préremplit tout : Cutora (par défaut), Sobre premium, Créateur énergique, Documentaire, Tech minimal, Éditorial chaud |
| Format | Les 5 formats de [formats.md](formats.md) en mini-vidéos (visage qui parle, main qui se lève et fait sortir une carte, bascule plein visage et écran partagé, plans qui s'enchaînent, zoom sur un clic). Une vraie vidéo s'affiche à la place si `choix/exemples/F1.mp4`... existe |
| Couleurs | 9 palettes (Cutora en premier), ou **ses couleurs de marque** : une ligne par couleur (fond, couleur forte, couleur 2, puis jusqu'à 5), chacune avec un carré à cliquer (pipette) et son code hexadécimal synchronisés en direct, un aperçu qui change en direct et une confirmation visible |
| Polices | 13 associations toutes faites, ou sa propre association **par rôle** : police forte (titres et mots forts), police normale (petits mots et textes), police d'accent (le mot mis en valeur), parmi une trentaine de polices gratuites |
| Taille | Taille des titres : normal, grand, très grand |
| Mot clé | Couleur et police d'accent (signature Cutora), couleur, police d'accent, pavé de couleur, trait qui se dessine |
| Sous-titres | Un mot à la fois, karaoké, bandeau, mot géant, classique, aucun |
| Texte | Flou vers net, glissement, machine à écrire, révélation, pop |
| Transitions | Coupe franche, zoom, glissement flou, fondu |
| Rythme | Calme, naturel, rapide (les autres aperçus s'accélèrent ou ralentissent) |
| Motion design | Plusieurs choix : cartes, téléphone, icônes en orbite, flèches dessinées, chiffres, étiquettes, saisie en direct, texte derrière la personne |
| Son | Musique (calme, suspense discret, énergique, aucune, avec un croquis sonore à écouter) et densité des bruitages |
| Références | **Les liens de ses vidéos modèles**, ses mots sur ce qu'il veut faire ressentir, une note libre |
| Récapitulatif | Tout relire, puis Enregistrer |

Quand il clique sur Enregistrer, le serveur écrit `styles/<style>/choix.json`, affiche son contenu et s'arrête :
tu es prévenu par la fin de la commande. Si le navigateur ne peut pas joindre le serveur, la page télécharge
`choix.json` dans ses Téléchargements : va le chercher là.

Sans navigateur : pose les mêmes questions une par une, avec 3 options et ta recommandation en premier.

## 3. Tout apprendre de ce qu'il a fait sur la page

`choix.json` contient ses choix, mais aussi **comment** il les a faits. Lis tout :

- `references` : des liens. **Analyse-les tout de suite** ([analyse-reference.md](analyse-reference.md)), sans
  attendre qu'il le redemande. Ce qu'une référence mesure l'emporte sur un choix « par défaut », pas sur un choix
  qu'il a fait lui-même (dans ce cas, signale l'écart et demande).
- `ses_mots` et `note` : copie-les tels quels dans `style.md` (section Qui) et dans `gouts.md`. Ce sont ses
  meilleures boussoles.
- `couleurs` et `polices` : les valeurs exactes (codes hexadécimaux, familles, graisses, italique, capitales) à
  reprendre telles quelles dans `style.md` et dans le CSS du montage (`head.html`). Les polices viennent de Google
  Fonts : télécharge-les dans `montage/assets/fonts/` si HyperFrames ne les a pas.
- `vraiment_choisi` : les étapes où il a cliqué lui-même. Ce sont ses vrais goûts, à respecter en priorité.
- `etat` : l'état complet de la page, qui sert à la rouvrir préremplie (§ 8). Ne le recopie pas ailleurs.
- `etapes_passees` et `choisi_pour_moi` : il n'a pas d'avis sur ces points. Prends la recommandation, marque-la
  `(par défaut)`, et ce sont les premières questions du bilan de goût.
- `hesitations` : les étapes où il a changé d'avis plusieurs fois. Il y tient mais ne sait pas trancher : au
  moment de la planche de style, montre-lui les deux options côte à côte sur son contenu.
- `parcours` : l'ordre et l'heure de chaque clic, les musiques écoutées. Une étape choisie en 2 secondes est un
  goût franc ; une musique écoutée trois fois avant de choisir « aucune » en dit long.
- `depart` : « reference » = il fait confiance aux exemples, montre-lui des comparaisons plutôt que des
  descriptions ; « defaut » = il veut aller vite, n'ajoute pas de questions.

Écris ce que tu en déduis dans `gouts.md`, marqué `(déduit de la page de choix, à confirmer)`.

## 4. Les deux autres portes (à combiner avec la page)

**Références en fichiers** (une vidéo enregistrée sur son téléphone, un reel qu'il ne peut pas lier) : qu'il les
dépose dans `styles/<style>/references/`. 2 ou 3 vidéos du même créateur valent mieux qu'une. Après l'analyse,
montre ce que tu as compris en 6 lignes et demande ce qu'il faut changer (« même style, mais mes couleurs » est
une demande normale).

**Charte graphique** : logo (SVG ou PNG), codes couleur, polices (fichiers si elles ne sont pas gratuites), document
de charte. Rangés dans `profils/<personne>/charte/`. Sans code couleur, lis les couleurs sur le logo et fais-les
confirmer. Une charte l'emporte sur les couleurs et les polices choisies sur la page, sauf s'il dit le contraire.

## 5. Écrire le style

Remplis `styles/<style>/style.md` à partir du modèle, avec tout ce qui a été choisi, mesuré ou dit. Chaque ligne
dit **d'où elle vient** : `(choix)`, `(référence <ref>, mesuré)`, `(charte)`, `(par défaut)`, `(déduit, à confirmer)`.

Ce qui n'a été ni choisi ni mesuré : prends **le style Cutora par défaut** ([style-defaut.md](style-defaut.md)),
qui est une base éprouvée, et marque `(par défaut)`.

## 6. La planche de style (avant le premier montage)

Avant de monter une vraie vidéo, montre une **planche de style** : un aperçu HyperFrames de 8 à 10 secondes (ou
3 images fixes) qui applique le style sur **son** contenu : un titre avec ses mots importants, un sous-titre, un
élément de motion design, sa caméra si le format en a une. S'il a déjà un rush, utilise-le.

> « Voilà ton style appliqué à ta vidéo. Je garde tout, ou je change une chose ? »

Ses hésitations de la page : montre les deux options côte à côte sur cette planche. Chaque remarque ici va tout de
suite dans le style ([apprentissage.md](apprentissage.md)). Deux ou trois allers-retours sur la planche coûtent
beaucoup moins cher qu'un montage refait.

## 7. Aider quelqu'un qui ne sait pas ce qu'il veut

- Ne demande jamais « qu'est-ce que tu veux ? ». Montre 2 ou 3 possibilités, nommées par l'effet qu'elles
  produisent (« sérieux et premium », « rapide et punchy »), pas par leur technique.
- Pars de son métier et de son public : un coach sportif, un avocat et un développeur n'appellent pas la même
  direction. Propose celle qui colle, en disant pourquoi en une phrase.
- Montre des exemples, demande lequel lui ressemble le plus, puis ce qu'il changerait. La deuxième réponse est
  souvent la plus riche.
- S'il hésite entre deux options, monte les deux sur le même passage de 5 secondes, côte à côte.
- Note ses mots à lui (« pro mais pas froid ») : ce sont les meilleures boussoles pour la suite.

## 8. Modifier un style existant

Un style n'est jamais figé : il évolue avec chaque vidéo. Deux façons de le modifier :

1. **Une petite modification** (« le jaune plutôt orange », « titres plus petits », « plus de musique ») : applique-la
   directement dans `styles/<style>/style.md`, avec la source `(correction du <date>)`, et note-la dans le journal
   ([apprentissage.md](apprentissage.md)). La vidéo en cours et toutes les suivantes en tiennent compte.
2. **Une grosse modification** (« je veux revoir mes couleurs et mes polices », « refais mon style ») : rouvre la
   page **préremplie** avec ce style, en arrière-plan :

   ```powershell
   python <skill>/scripts/choix_serveur.py --profil "<atelier>/profils/<personne>" --style "<nom du style>"
   ```

   Il change ce qu'il veut et enregistre. L'ancien `choix.json` est gardé à côté (`choix-<date>-<n>.json`). Compare
   l'ancien et le nouveau, et ne reporte dans `style.md` **que ce qui a changé** : les règles apprises en montage
   (acquis, corrections) restent, sauf si la nouvelle page les contredit explicitement (dans ce cas, demande).

`style.md` est la référence du style ; `choix.json` est seulement ce qu'il a cliqué un jour sur la page.
