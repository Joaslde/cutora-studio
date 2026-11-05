# Apprendre à apprendre (couche 2)

Cette fiche est la plus importante du skill. Elle s'applique à **toute personne** et à **chaque échange**.
Le but : que chaque vidéo soit meilleure que la précédente, que l'on ne refasse jamais deux fois la même erreur,
et que l'on finisse par anticiper le goût de la personne avant qu'elle parle.

Principe : une correction n'est pas une tâche à faire, c'est une **information sur un goût**. On fait la tâche,
et on garde l'information.

## 1. Les fichiers du profil (`<atelier>/profils/<personne>/`)

Une personne a des fichiers communs à tous ses styles, et un dossier par style dans `styles/<style>/`.

| Fichier | Contenu | Quand on l'écrit |
|---|---|---|
| `styles/<style>/style.md` | Un style : format, charte, typographie, mouvements, rythme, son, cadrage, avec la source de chaque ligne | Découverte, puis à chaque règle de style nouvelle |
| `styles/<style>/acquis.md` | Les acquis propres à ce style (proportions, mise en page) | Correction qui ne vaut que pour ce style |
| `acquis.md` | Les règles **à ne jamais perdre**, valables pour tous ses styles, chacune avec l'erreur qui l'a fait naître et la façon de la vérifier | À chaque correction qui pourrait se reproduire |
| `journal.md` | Une entrée datée par retour : ce qu'il a dit (ses mots), ce qu'on a compris, ce qu'on a changé | À chaque retour, sans exception |
| `gouts.md` | Le portrait du goût : ce qui le fait réagir en bien ou en mal, ses mots, ses tendances | Au bilan de goût, et quand une tendance se confirme |
| `consignes.md` | Comment dérusher et monter ses rushs (prises, silences, ordre, durée, B-roll) | Étape 4 de l'onboarding, puis à chaque correction de dérush |
| `styles/<style>/choix.json` | Tout ce qu'il a fait sur la page de choix (choix, étapes passées, hésitations, parcours) | Découverte |
| `styles/<style>/references/` | Les analyses de références et leurs images clés | Analyse d'une référence |
| `charte/` | Logo, polices, couleurs, photos de la personne | Découverte, ou quand il en donne |

Ces fichiers sont dans l'atelier, jamais dans le dossier du skill (une mise à jour du skill les effacerait).

## 2. À chaque remarque : le protocole en 6 étapes

1. **Noter ses mots exacts** dans `journal.md` (date, vidéo, version, citation). Ses mots valent plus que ta
   reformulation : « ça fait horreur » et « trop sombre » ne disent pas la même chose.
2. **Trouver le vrai problème**, derrière la solution qu'il propose. « Mets la musique moins fort » peut vouloir
   dire « elle est trop présente » ou « elle est désagréable ». Si deux lectures sont possibles, demande-lui en
   une question à choix, ou montre les deux.
3. **Classer** :
   - **ponctuel** : ne vaut que pour cette vidéo (« enlève ce mot ici ») ;
   - **règle de style** : vaut pour toutes ses vidéos (« les titres sont trop petits ») ;
   - **acquis** : une erreur qui ne doit plus jamais revenir (« la tête est coupée pendant les gestes ») ;
   - **goût** : une préférence qui dit quelque chose de lui (« c'était mieux avant », « trop amusant »).
   En cas de doute entre ponctuel et règle, demande : « Je le garde pour toutes tes vidéos, ou seulement
   celle-ci ? » La réponse se demande une fois ; ensuite on sait.
4. **Écrire au bon endroit** :
   - règle de style : modifier la ligne de `styles/<style>/style.md` (pas ajouter une ligne contradictoire),
     source `(correction du <date>)`. Si elle vaut pour tous ses styles (« jamais de musique d'horreur »), elle
     va dans `gouts.md` ou `acquis.md` de la personne ; en cas de doute, demande ;
   - acquis : nouvelle entrée dans `acquis.md` avec le **symptôme**, la **cause**, la **règle**, la
     **vérification** (comment le contrôler avant de montrer) ;
   - goût : `gouts.md`.
5. **Corriger** dans une nouvelle version, en vérifiant que la correction n'en casse pas une autre (relis
   `acquis.md`).
6. **Généraliser** : demande-toi si l'erreur vient d'une méthode. Si oui, la règle va aussi dans la fiche du skill
   concernée **seulement si elle vaut pour tout le monde** (une proportion mal mesurée, un piège technique). Une
   préférence personnelle reste dans le profil. En cas de doute, elle reste dans le profil.

Puis dis-le en une phrase : « Noté pour toutes tes prochaines vidéos : titres plus grands. »

## 3. Les contradictions

- Le plus récent gagne, mais on ne l'efface pas : la règle remplacée passe en bas de `style.md`, section
  « Essayé puis abandonné », avec la date et la raison. Cela évite d'y revenir en boucle.
- « C'était mieux avant » : reviens à la version précédente sur ce point précis, et note **ce qui a été refusé**
  (c'est souvent plus instructif que ce qui a été demandé).
- Une demande qui contredit un acquis : applique-la, mais signale-le en une phrase (« Avant, tu m'avais demandé
  l'inverse : je change la règle pour de bon ? »).
- Un goût de la personne peut céder à la demande d'un client final : note la vidéo comme exception, ne change pas le
  profil.

## 4. Anticiper (ce qui fait la différence)

Avant chaque nouveau montage :

1. Relis `style.md` et `acquis.md` du style, `acquis.md`, `gouts.md`, `consignes.md` de la personne et les
   10 dernières entrées du journal.
2. Écris pour toi la liste des 5 erreurs que cette personne a le plus souvent corrigées. Vérifie-les avant de
   montrer.
3. Applique ses tendances aux situations nouvelles. S'il a refusé deux fois un son « amusant », un nouveau
   bruitage sera sobre sans qu'il ait à le dire. S'il a demandé deux fois « plus grand », les nouveaux éléments
   partent grands.
4. Quand tu fais un choix qu'il n'a jamais validé, signale-le dans le message d'aperçu (« Nouveau : j'ai essayé
   un compteur qui s'anime, dis-moi s'il te plaît »). Sa réponse devient une règle.

## 5. Le bilan de goût (après chaque vidéo validée)

Trois questions maximum, sous forme de choix, de préférence visuels :

- une sur ce qui a le plus plu (« Qu'est-ce que tu as préféré : les transitions, la musique, les titres ? ») ;
- une sur un point marqué `(par défaut)` ou `(déduit, à confirmer)` dans le profil ;
- une ouverte facultative : « Une chose que tu veux plus souvent, ou plus jamais ? »

Pour une préférence difficile à dire, montre une **comparaison A/B** : deux images fixes ou deux extraits de
3 secondes côte à côte, qui ne diffèrent que sur un point.

Ensuite :

- mets à jour `gouts.md` (ce qui le fait réagir, ses mots, ses tendances confirmées) ;
- passe les lignes confirmées de `(par défaut)` à `(confirmé le <date>)` ;
- tous les 5 bilans, relis tout le profil, fusionne les doublons, supprime ce qui est dépassé, et résume-lui ce
  que tu as appris de lui en 5 lignes. Il doit s'y reconnaître.

## 6. Ce qu'on apprend d'une personne (la grille)

Le goût se lit sur ces axes. Pour chacun, le profil finit par avoir une valeur et la preuve qui la soutient.

| Axe | De quoi il s'agit |
|---|---|
| Énergie | calme, posé, ou rapide, punchy (coupes, transitions, musique) |
| Densité | beaucoup d'éléments à l'écran ou peu, de l'air ou du plein |
| Échelle | éléments grands et affirmés, ou petits et discrets |
| Sérieux | sobre, premium, institutionnel, ou ludique, coloré, humoristique |
| Réalisme | vraies images, vraies interfaces, vraies photos, ou formes abstraites et illustrations |
| Son | nappe calme, suspense, énergique, silence ; bruitages réalistes ou synthétiques ; discrets ou marqués |
| Présence du visage | toujours visible, en alternance, ou absent |
| Texte | beaucoup (mot par mot, titres) ou peu ; où il se place ; quelles polices |
| Couleurs | sa palette, la couleur des mots importants, fond clair ou sombre |
| Exigence de finition | ce qu'il remarque (liserés, synchronisation, proportions, son) : là où il faut vérifier deux fois |
| Façon de travailler | veut voir le plan avant, ou le résultat directement ; combien d'options à la fois |

## 7. Le niveau attendu

Un acquis bien écrit dit le symptôme, la cause, la règle et la vérification. Exemple réel, après trois versions d'une
même vidéo :

| Règle | Né de | Vérification avant de montrer |
|---|---|---|
| Masque de détourage synchronisé image par image avec le rush | « La tête est coupée pendant les gestes rapides » (v2) | Arrêt sur image pendant 3 gestes rapides, à taille réelle |
| Titres et graphismes grands (ligne principale d'au moins 70 px) | « Les éléments sont trop petits, perdus dans le noir » | Mesurer en pixels sur les images fixes |
| Nappe calme et continue, pas de suspense | « C'était mieux avant » | Lire la piste de musique dans le projet |
