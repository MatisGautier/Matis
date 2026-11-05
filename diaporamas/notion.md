# Les cours du DU sur Notion (décision de Matis, 05/11/2026)

Depuis le 05/11/2026, **chaque cours du DU est une page Notion**, plus un Google Slides. Matis demandera lui-même un diaporama s'il en a besoin pour enseigner : ce n'est plus le travail des agents.

Ce qui ne change pas : le contenu (`regles.md`, sections 3, 4 et 5 : niveau, structure, sources, articles phares, « Ce que ça change pour ma pratique », « Enfant / adulte » en M08), l'onglet `Diaporamas` du tableau (une ligne par cours), le plan JSON enregistré sur Drive et l'onglet `Bilans`.

Ce qui ne s'applique plus : `regles.md` section 6 pour les tailles, positions et polices des diapos, section 7 (copie du modèle, duplication, `remplir.py`) et section 12 (partage Slides). Le Constructeur n'existe plus.

## 1. Le plan JSON reste la source

Le cours s'écrit d'abord en plan JSON, **au même format qu'avant** (`scripts/construire_diapos.py`, en tête du fichier) : une entrée par bloc (`contenu`, `colonnes`, `tableau`, `retenir`, `section`, `phares`, `references`…), 60 à 100 entrées, une source sur chaque entrée, au moins un visuel (`schema` : `flux`, `cercles`, `chiffres` ou `image`) une entrée sur deux. Le plan est enregistré sur Drive comme avant (dossier du module, « plan – <Ordre>. <Titre>.json », en deux fichiers s'il est long). Il permet les mises à jour, et un diaporama si Matis en veut un.

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

- Un cours = une page, de 60 à 100 blocs (entrées du plan), jamais plus : au-delà, partie 2 (`regles.md`, section 4).
- **Deux cours par jour**, un par passage du Rédacteur (4 h et 18 h). Sans diapos à construire, **un cours se termine dans le passage** : recherche, plan, page, onglet. Pas de cours `En cours` d'un passage à l'autre, sauf échec signalé dans `Bilans`.

## 5. Contrôle de la page

Avant de passer la ligne à `À relire`, relis la page générée (le fichier `.md`) : chaque `###` a sa ligne de sources, les ★ sont en rouge, « Articles phares » est juste avant les références, aucune balise non fermée (`<toggle>`, `<callout>`, `<columns>`). Si tu as publié sur Notion, `notion-fetch` sur la page et vérifie qu'elle n'est pas tronquée.
