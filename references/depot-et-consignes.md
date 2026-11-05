# Déposer ses rushs, donner ses consignes, viser l'automatisme

But final : la personne dépose ses rushs et ses B-rolls, dit en une phrase de quoi parle la vidéo (ou rien), et
tu montes tout dans son style, sans qu'elle ait à réexpliquer. On y arrive par paliers, en apprenant ses consignes
de montage comme on apprend son style.

## 1. Où déposer

```text
<atelier>/a-monter/                 la boîte de dépôt
├── <nom-de-la-video>/              un dossier par vidéo (ou tout en vrac : tu ranges)
│   ├── rush-01.mp4, rush-02.mp4    les rushs, dans l'ordre de tournage
│   ├── b-roll/                     ses plans d'illustration, photos, captures (facultatif)
│   ├── voix/                       voix off ou musique imposée (facultatif)
│   └── consignes.txt               ce qu'il veut pour cette vidéo, en quelques lignes (facultatif)
```

Au lancement, regarde `a-monter/`. Pour chaque dossier nouveau : crée le projet dans
`<atelier>/projets/<profil>/<date>-<nom>/`, **déplace** (pas de copie : le disque compte) les fichiers dans
`a-roll/`, `b-roll/`, `voix/`, et dis ce que tu as trouvé (« 3 rushs, 4 min 12 au total, 6 B-rolls, une consigne »).

Plusieurs rushs : trie-les par date de tournage (métadonnées, sinon nom), mesure-les, fais une planche de chacun,
et transcris-les tous avant de décider de l'ordre du montage.

**À chaque nouvelle vidéo, le style est précisé.** Avant de monter :
- s'il a nommé le style dans son message ou dans `consignes.txt`, tu le prends sans demander ;
- s'il a **plusieurs styles**, tu demandes par une question à choix « Je monte cette vidéo dans quel style ? »
  (un style par option, le dernier utilisé en premier, plus « Un nouveau style ») ;
- s'il n'en a **qu'un**, tu l'annonces en une ligne (« Je la monte dans ton style *Mes reels* ») et tu continues :
  il peut répondre « non, un autre » s'il veut.

Ne monte jamais une vidéo dans un style deviné en silence.

## 2. Les consignes de montage : ce qui est évident ne se demande pas

Ses consignes générales vont dans `<atelier>/profils/<nom>/consignes.md`.

**Le métier de monteur a des évidences. Tu les appliques sans poser la question**, et tu les écris dans
`consignes.md` avec la source `(par défaut)` :

| Évidence (appliquée sans demander) | Valeur par défaut |
|---|---|
| Blancs et silences | Coupés serré, marges 0,08 s avant la reprise et 0,16 s après la fin de phrase |
| Prises ratées, phrases recommencées | On garde la dernière bonne prise |
| « Euh », hésitations, mots répétés | Coupés |
| Erreurs évidentes (lapsus, phrase abandonnée) | Coupées |
| Ordre des rushs | Ordre de tournage |
| Sous-titres | Fautes de langue corrigées à l'écrit, sens inchangé |
| B-roll | Le sien d'abord, sinon des médias libres de droits, posés sur le mot qui les nomme |
| Accroche | Le début tel quel, sauf s'il est faible : tu le signales dans le message d'aperçu |

Tu ne demandes **que ce qui ne se devine pas**, et seulement si ce n'est pas déjà noté :
- le format de livraison, s'il ne se déduit ni du style ni du rush (vertical pour les réseaux, horizontal pour YouTube) ;
- une durée visée, seulement si le rush est long (plus de 3 minutes) et le style fait pour des vidéos courtes ;
- une seule question ouverte et facultative : « Quelque chose de particulier pour cette vidéo ? (sinon je fais comme
  d'habitude) ».

Résume les évidences en **une ligne** dans ton message, pour qu'il puisse corriger d'un mot : « Je coupe les blancs,
les euh et les ratés en gardant ta dernière prise, comme d'habitude. »

**Ne repose jamais une question dont la réponse est déjà connue.** Avant chaque question, relis `consignes.md`,
`style.md`, `gouts.md` et le journal : si la réponse y est, applique-la. Une préférence donnée une fois vaut pour
toutes les vidéos suivantes, sauf s'il dit le contraire.

Pour une vidéo précise, il peut tout dire en vrac (« coupe la partie où je parle du prix, mets mon B-roll de la
plage au début, fais court »). Applique, puis demande s'il faut en faire une règle : la réponse va dans
`consignes.md` ou reste dans le journal ([apprentissage.md](apprentissage.md)).

Ses consignes de montage s'apprennent comme son style : chaque correction de dérush (« tu as coupé trop serré »,
« garde cette blague ») est notée, classée et généralisée.

## 3. Comprendre vite une nouvelle vidéo

Avant de monter, en silence :

1. Transcris tous les rushs, lis tout.
2. Résume l'idée de la vidéo en une phrase, trouve l'accroche la plus forte, les 3 à 5 parties, la chute.
3. Repère les passages à montrer (chiffres, outils, exemples : motion design ou B-roll) et les passages
   personnels (visage), selon le format du profil.
4. Associe chaque B-roll à une phrase (planches + `bibliotheque.md`).
5. Applique `consignes.md`, puis le profil.

Au niveau d'autonomie 1 et 2, montre ce résumé et ce plan en 6 à 10 lignes avant de monter.

## 4. Le niveau d'autonomie (par profil, dans `~/cutora-studio.json`)

| Niveau | Ce que tu fais | Quand on y passe |
|---|---|---|
| 1. Accompagné | Plan écrit validé avant de monter, aperçu, corrections | Premier montage |
| 2. Confiant | Tu montes directement ; tu montres le plan seulement si un choix est risqué | Après 2 vidéos validées |
| 3. Automatique | Il dépose, tu montes tout, tu contrôles et tu montres le résultat fini (toujours en aperçu, jamais d'export sans accord) | Après 2 vidéos d'affilée validées avec au plus 2 corrections chacune |

- Propose le passage au niveau supérieur, ne l'impose pas : « Tes deux dernières vidéos sont passées presque sans
  retouche. Je peux monter les prochaines directement et te montrer le résultat fini. On fait comme ça ? »
- Une vidéo très corrigée (plus de 5 retours importants) fait redescendre d'un niveau, et tu dis pourquoi.
- Quel que soit le niveau : aperçu avant export, acquis vérifiés, versions conservées.
- Au niveau 3, s'il n'a donné aucune consigne, tu décides seul (durée, accroche, B-roll) selon `consignes.md` et le
  profil, et tu listes en 3 lignes les choix que tu as faits pour qu'il les corrige d'un mot.
