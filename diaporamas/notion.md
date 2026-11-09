# Les cours du DU sur Notion (décision de Matis, 05/11/2026)

Depuis le 05/11/2026, **chaque cours du DU est une page Notion**, plus un Google Slides. Matis demandera lui-même un diaporama s'il en a besoin pour enseigner : ce n'est plus le travail des agents.

Ce qui ne change pas : le contenu (`regles.md`, sections 3, 4 et 5 : niveau, structure, sources, articles phares, « Ce que ça change pour ma pratique », « Enfant / adulte » en M08), l'onglet `Diaporamas` du tableau (une ligne par cours), le plan JSON enregistré sur Drive et l'onglet `Bilans`.

Ce qui ne s'applique plus : `regles.md` section 6 pour les tailles, positions et polices des diapos, section 7 (copie du modèle, duplication, `remplir.py`) et section 12 (partage Slides). Le Constructeur n'existe plus.

## 1. Le plan JSON reste la source

Le cours s'écrit d'abord en plan JSON, **au même format qu'avant** (`scripts/construire_diapos.py`, en tête du fichier) : une entrée par bloc (`contenu`, `colonnes`, `tableau`, `retenir`, `section`, `phares`, `references`…), 70 à 100 entrées, une source sur chaque entrée, au moins un visuel (`schema` : `flux`, `cercles`, `chiffres` ou `image`) une entrée sur deux. Le plan est enregistré sur Drive comme avant (dossier du module, « plan – <Ordre>. <Titre>.json », en deux fichiers s'il est long). Il permet les mises à jour, et un diaporama si Matis en veut un.

## 2. Du plan à la page Notion

1. `cd` dans `diaporamas/` dans une commande à part, puis : `python3 scripts/plan_vers_notion.py <plan.json> [<plan partie 2.json>] > <page.md>`.
2. **Si l'exécution est refusée**, écris toi-même la page en Notion Markdown en suivant exactement la correspondance ci-dessous : c'est du texte simple.

| Entrée du plan | Dans la page Notion |
|---|---|
| `titre` | encadré violet en tête : `<callout icon="🎓" color="purple_bg">` sous-titre, auteur, date |
| `plan` | rien : remplacé par `<table-of-contents />` en tête |
| `section` | ligne `---`, puis `## Titre de la partie` |
| `contenu` | `### Titre`, puces, puis le schéma, puis la conclusion dans `<callout icon="👉" color="yellow_bg">` |
| `colonnes` | `### Titre` puis `<columns><column>…</column></columns>` |
| `tableau` | `### Titre` puis un tableau Markdown |
| `retenir` | `<callout icon="📌" color="green_bg">` titre en gras, message, puces |
| schéma `flux` | `<callout icon="🔀" color="blue_bg">` étapes reliées par « → », légende en italique |
| schéma `cercles` ou `chiffres` | `<columns>`, une colonne par chiffre, chacun dans `<callout icon="📊" color="gray_bg">` |
| schéma `image` | `<image source="URL">crédit</image>` |
| sources | `<p color="gray">Sources : …</p>` sous chaque bloc ; une source ★ en `<span color="red"><b>…</b></span>` |
| « Pour aller plus en profondeur » | tout dans `<toggle heading="h2">🔬 Pour aller plus en profondeur` … `</toggle>` |
| Corrigé du Testez-vous | `<toggle heading="h3">✅ Corrigé (cliquer pour afficher)` … `</toggle>` |
| `phares` | `<callout icon="⭐" color="red_bg">`, chaque article en rouge et gras, **juste avant les références** |
| `references` | `<toggle heading="h3">📚 Références` … `</toggle>`, les ★ en rouge et gras |

Le rouge ne sert qu'aux articles phares. Pas de titre en tête du contenu : le titre est la propriété `title` de la page.

## 3. Publier la page

- **Si tu as les outils Notion** (`notion-create-pages`, chargés via ToolSearch) : crée la page **sous la page du module** (identifiants dans les « Paramètres » de ta tâche), titre « <Ordre> · <Titre> », une icône emoji adaptée. Ensuite, F de l'onglet = l'URL de la page Notion.
- **Sinon** (le connecteur Notion manque dans ta tâche) : dépose la page sur Drive, dans le dossier du module, en texte (`create_file`, `contentMimeType: text/markdown`, `disableConversionToGoogleType: true`), titre « notion – <Ordre>. <Titre>.md ». Écris en F le lien Drive du fichier et en N « Notion à publier (Mage) ». Mage la publie à son passage et remplace F par l'URL Notion.
- Une mise à jour d'une page existante : `notion-update-page` sur la page (URL en F), ou nouveau fichier « notion – … (mise à jour).md » sur Drive si tu n'as pas Notion.

## 4. Taille et rythme

- Un cours = une page, de 70 à 100 blocs (entrées du plan), jamais plus : au-delà, partie 2 (`regles.md`, section 4).
- **Deux cours par jour**, un par passage du Rédacteur (4 h et 18 h). Sans diapos à construire, **un cours se termine dans le passage** : recherche, plan, page, onglet. Pas de cours `En cours` d'un passage à l'autre, sauf échec signalé dans `Bilans`.

## 5. Contrôle de la page

Avant de passer la ligne à `À relire`, relis la page générée (le fichier `.md`) : chaque `###` a sa ligne de sources, les ★ sont en rouge, « Articles phares » est juste avant les références, aucune balise non fermée (`<toggle>`, `<callout>`, `<columns>`). Si tu as publié sur Notion, `notion-fetch` sur la page et vérifie qu'elle n'est pas tronquée.

## 6. Cours sans plan JSON (diaporama seul)

Si un cours n'a qu'un Google Slides (pas de plan sur Drive), on reconstruit la page depuis le diaporama :
1. `read_presentation` (le résultat est enregistré dans un fichier) ;
2. `python3 scripts/extraire_slides.py <fichier> slides.json` (texte et tableaux, diapo par diapo) ;
3. `python3 scripts/slides_vers_notion.py slides.json <ID du diaporama> > page.md` ;
4. relire la page : les schémas `flux` et les colonnes sortent en puces découpées, à remettre en `→` ou en `<columns>` à la main.

Les sources contenant plusieurs références séparées par « ; » ne mettent en rouge que les références ★.

## 7. Figures d'articles (PubMed Central, consigne de Matis du 06/11/2026)

Chaque cours est illustré avec de **vraies figures d'articles**, PubMed en priorité, Wikimedia Commons en complément pour l'anatomie.
1. `python3 scripts/figures_pmc.py <PMID cités dans le cours> > figures.json` : pour chaque article en libre accès, la licence et la liste des figures (numéro, légende, adresse publique sur le dépôt Open Access du NCBI).
2. Licences acceptées (le DU n'est pas vendu) : CC0, CC BY, CC BY-SA, CC BY-NC, CC BY-NC-SA, CC BY-ND, CC BY-NC-ND. Licence « ND » : image telle quelle, jamais recadrée. Une figure marquée « reprinted / reproduced with permission » dans sa légende n'est **jamais** reprise.
3. Choisis 3 à 6 figures qui expliquent quelque chose (schéma, tracé, imagerie, arbre décisionnel), jamais un diagramme de sélection d'études (PRISMA, STARD).
4. Dans la page : `<image source="<url>">Légende en français. Auteur et al., Revue Année, PMID …, fig. n – <licence></image>`, juste sous le `###` du bloc concerné. Pour une page déjà publiée : `notion-update-page`, commande `update_content`, en remplaçant le `###` par le `###` suivi de l'image.
5. Hôtes nécessaires (déjà autorisés dans l'environnement) : pmc.ncbi.nlm.nih.gov, pmc-oa-opendata.s3.amazonaws.com.

## 8. PDF du cours à télécharger (consigne de Matis, 09/11/2026)

Chaque cours validé a son **PDF**, que Matis télécharge depuis un lien **à la fin de la page Notion**. Le PDF contient **tout le cours, sans rien couper ni résumer**, quel que soit son nombre de pages : chaque bloc, chaque figure, l'approfondissement, le Testez-vous et son corrigé, les articles phares et toutes les références. Un cours en plusieurs parties a **un seul PDF avec toutes ses parties** (tous les plans à la suite dans la commande du point 1), refait à la validation de chaque partie, et son lien figure à la fin de la page de chaque partie. C'est le relecteur qui le fait, au moment où il passe la ligne à `Validé`, pour que le PDF corresponde à la version finale.

1. `cd` dans `diaporamas/` dans une commande à part, puis : `python3 scripts/plan_vers_html.py <plan.json> [<plan partie 2.json>] > cours.html` (même contenu et même ordre que la page Notion, images comprises ; les dépliants sont ouverts). **Si l'exécution est refusée**, écris toi-même ce HTML simple à partir du plan, en suivant le script : `<h1>` titre, `<h2>` parties, `<h3>` blocs, `<ul>` puces, `<table>` tableaux, encadrés en `<table>` à une cellule colorée, `<img src="URL">` pour les figures, sources en gris, articles phares en rouge.
2. Dépose-le **dans le dossier Drive du module**, en Google Doc : `create_file` avec `title` « <Ordre>. <Titre> (PDF du cours) », `textContent` = le contenu de `cours.html`, `contentMimeType: text/html`, `parentId` = dossier du module, **sans** `disableConversionToGoogleType` (Drive le convertit en Google Doc).
3. Lien de téléchargement en PDF : `https://docs.google.com/document/d/<ID du Doc>/export?format=pdf`. Contrôle une fois : `download_file_content` sur l'ID avec `exportMimeType: application/pdf` doit renvoyer un PDF (le résultat est enregistré dans un fichier : ne le relis pas en entier, vérifie seulement qu'il existe et que `mimeType` vaut `application/pdf`).
4. Ajoute **à la toute fin de la page Notion**, après l'historique, avec `notion-update-page` :
   `---` puis `<callout icon="📄" color="gray_bg">` **[Télécharger ce cours en PDF](<lien du point 3>)** – version du <date> `</callout>`.
5. Écris le lien du point 3 en colonne **O** (« PDF du cours ») de la ligne.

**Mise à jour d'un cours** (nouvelle validation après `À mettre à jour` ou `À corriger`) : refais les points 1 à 3, mets l'ancien Doc à la corbeille (`trash_file`), remplace le lien à la fin de la page et en O.

**Cours déjà validés sans PDF** (lien Notion en F, O vide) : à chaque passage, après tes relectures, fais le PDF de 2 d'entre eux au maximum, en commençant par le plus ancien.

Le PDF ne compte pas dans les 100 blocs. Si la création du Doc échoue, valide quand même le cours, laisse O vide et signale-le dans `Bilans`.
