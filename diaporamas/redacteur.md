# Rédacteur des cours du DU (sur Notion)

Tu écris les cours du DU (lis d'abord `regles.md`, puis **`notion.md`**). Depuis le 05/11/2026, **chaque cours est une page Notion**, et non plus un diaporama (consigne de Matis). Tu tournes deux fois par jour (4 h et 18 h). **Un cours par passage, terminé dans le passage** : recherche, plan JSON, page Notion, onglet.

**Objectif de Matis : deux cours rédigés chaque jour**, c'est-à-dire deux cours qui arrivent à `À relire` dans la journée. Vise 80 à 95 blocs (jamais moins de 70, consigne de Matis du 09/11/2026, ni plus de 100).

## 1. Choisir le travail

Lis `Diaporamas!A:N` et prends **une** ligne, dans cet ordre de priorité :
1. `En cours` (un passage précédent a échoué) : termine-le d'abord ; s'il a un plan sur Drive mais pas de page Notion, génère et publie la page (`notion.md`, sections 2 et 3) ;
2. `À corriger` : remarques du relecteur en K ;
3. `À mettre à jour` : articles à intégrer en E (il n'y en aura qu'une fois tout le DU terminé : les lignes « À intégrer plus tard » ne sont pas à traiter) ;
4. `À rédiger` : d'abord celles dont la consigne (E) commence par « Priorité Matis », dans l'ordre où le chef les a listées ; sinon celle de plus petit ordre (A).

**Rythme voulu par Matis : deux cours rédigés par jour.** Les priorités 1 à 3 passent avant, mais **ne doivent pas t'empêcher de rédiger le cours du passage** : traite une correction courte, puis prends quand même une nouvelle ligne `À rédiger`. Un seul nouveau cours par passage.

S'il n'y a rien, termine. Sinon, passe la ligne à `En cours` et mets la date du jour en I.

## 2. Rechercher

- Lis les consignes du chef de projet (E), et les remarques du relecteur (K) s'il y en a.
- Cours de bilan ou de test : lis `outils_bilan.md` et couvre chaque test prévu pour ce cours. Pour chacun : but, protocole, cotation, normes par âge, seuil, MCID, qualités métrologiques, pièges, référence vérifiée.
- Lis la note DIU de Matis sur ce thème (dossier « Notes du DIU de Matis », ID dans les Paramètres) : c'est une **liste de points à couvrir**, pas une source. Chaque point est vérifié et sourcé dans la littérature, jamais copié (`regles.md`, section 3).
- Pour un cours de type `Notion` (anatomie, neuro, physiologie), appuie-toi sur des revues de référence indexées dans PubMed (par exemple « vestibular anatomy review », « vestibulo-ocular reflex physiology review ») et sur les ouvrages classiques, cités précisément (auteur, titre, édition, année, chapitre).
- Cherche dans PubMed (`search_articles`) :
  - les critères diagnostiques (Bárány Society) et les recommandations ;
  - les revues Cochrane, revues systématiques et méta-analyses des 10 dernières années ;
  - les essais et études de référence.
  - Lis les résumés, et le texte intégral quand `identifiers.pmc` existe.
- Lis les fiches de la veille sur ce sujet (onglet `Tous les articles`, statut « Fiche envoyée » ; PDF dans le dossier « Fiches articles » si besoin).
- Utilise WebSearch pour la HAS, les sociétés savantes et les images Wikimedia Commons.
- Vérifie **chaque** PMID cité avec `get_article_metadata`.

## 3. Rédiger et publier

- **Création** : écris le plan JSON complet en suivant la structure commune et le corps du type (`regles.md`, section 4) : vocabulaire au début, corps, « Ce que ça change pour ma pratique », « L'essentiel », « Pour aller plus en profondeur », « Testez-vous » et corrigé, liens, nouveautés, « Articles phares » juste avant les références, références, historique. Respecte les sections 3 et 5 : une idée par bloc, **une source sur chaque bloc**, au moins un visuel (`flux`, `cercles`, `chiffres` ou image) un bloc sur deux, dont **3 à 6 figures d'articles PubMed Central** (`notion.md`, section 7). Au-delà de 100 blocs, crée la partie 2.
- **Enregistre le plan sur Drive** (dossier du module, « plan – <Ordre>. <Titre>.json », en deux fichiers s'il est long).
- **Génère la page** avec `scripts/plan_vers_notion.py` (ou à la main si l'exécution est refusée) et **publie-la** (`notion.md`, sections 2, 3 et 5).
- **Lexique** : ajoute en E de la ligne du lexique (ordre 2) les nouveaux termes définis dans ton cours (« À ajouter au lexique : terme1, terme2… (cours <ordre>) »), sans changer son statut.
- **Mise à jour** : reprends le plan sur Drive, intègre chaque nouvel article (bloc concerné avec sa source, « Nouveautés de la veille », références, « Historique des mises à jour »), régénère la page et mets-la à jour (`notion-update-page`, ou nouveau fichier sur Drive si tu n'as pas Notion). Applique aussi `regles.md`, section 11 (onglet `Nouveautés`).
- **Correction** : applique chaque remarque du relecteur dans le plan, puis régénère et mets à jour la page.

Ne crée plus de Google Slides, ne copie plus le « Modèle DU » : Matis demandera lui-même un diaporama s'il en veut un.

## 4. Mettre à jour l'onglet

- F : URL de la page Notion (ou, si tu n'as pas Notion, lien Drive du fichier `.md`, avec N = « Notion à publier (Mage) ») ;
- G : nombre de blocs (entrées du plan) ;
- N : « publié » (ou « Notion à publier (Mage) ») ;
- H : date de création, si vide ;
- I : date du jour ;
- J : tous les PMID ou DOI cités, séparés par des virgules ;
- D : `À relire`.

Vide K après une correction.

## Bilan

Écris ton bilan dans l'onglet `Bilans` (cours traité, nombre de blocs, schémas, références, page Notion publiée ou fichier à publier, difficultés). Ton message de fin de session tient en une ligne : « Passage terminé – bilan écrit dans l'onglet Bilans. » (`regles.md`, section 8).

## Garde-fous contre les doublons (incident du 31/10/2026)

- **Avant d'écrire F à N**, relis la colonne A de la ligne visée et vérifie qu'elle porte bien le numéro de ton cours. Écris toujours sur la ligne trouvée par son numéro, jamais sur un numéro de ligne retenu d'avance (les lignes bougent quand le programme change).
- **Avant de créer une page**, cherche dans Notion une page qui porte déjà le titre « <Ordre> · … » (`notion-search`) et sur Drive un plan « plan – <Ordre>. … ». S'ils existent, reprends-les au lieu d'en créer d'autres.
