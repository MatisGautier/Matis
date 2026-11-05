# Archive : règles de l'ère Google Slides (jusqu'au 05/11/2026)

Ces sections ne s'appliquent plus. Les cours sont des pages Notion (`notion.md`). Elles sont gardées ici pour mémoire : si un ancien cours doit être refait en diaporama à la demande de Matis, c'est la seule référence pour la mise en page et la construction.

## 6. Mise en page : propre, visuelle, pas que des tableaux

**Demande de Matis (28/10/2026) : des diapos beaucoup plus propres et variées.**

**Style de référence (28/10/2026) : les cours du DIU que Matis a suivi**, par exemple « Conséquences d'un déficit vestibulaire sur le développement de l'enfant » :
- peu de texte et en grand : **3 à 5 lignes courtes** par diapo, 10 mots environ par ligne ;
- des **sous-points** en retrait, commençant par « - » (exemple : « - schéma corporel erroné ») ;
- une **ligne de conclusion en gras** en bas, qui commence par « > » (champ `conclusion`) ;
- des **diapos d'affirmation** : une phrase seule, en grand, au centre (« Enfant ≠ petit adulte », « Vestibulopathie ≠ vertige ») : c'est la diapo `section`. On en met une à chaque grande partie ;
- les **chiffres clés en cercles** colorés (diapo `cercles`, 3 ou 4 chiffres avec leur libellé) ;
- un **titre en capitales bleues** avec, au-dessus, un petit **surtitre** gris : la partie en cours, rempli automatiquement avec le titre de la dernière diapo `section` ;
- les études présentées simplement : « Étude : **13 enfants** (âge moyen 10 ans) vs contrôles », puis les résultats en sous-points.

Ce que donnent les diapos modèles (version 3) :
- le **logo de Matis en haut à droite** de chaque diapo ;
- les **sources dans un encadré gris en bas** de la diapo, alimenté par le champ `sources`.

Règles de mise en page :
- **Jamais de source dans le texte** des puces : pas de « (Auteur 2020) » ni de PMID dans les phrases. Tout va dans `sources`, donc dans l'encadré.
- **Variété obligatoire** dans chaque cours :
  - **au plus 1 diapo sur 5 en `tableau`**, et jamais deux tableaux de suite. Une comparaison à 2 volets se fait en **`colonnes`** (deux cartes côte à côte) ;
  - au moins **1 diapo sur 2 avec un visuel** : `flux`, `image`, `chiffres`, `colonnes` ou `retenir` ;
  - une diapo **`retenir`** (message clé encadré) à la fin de chaque grande partie, en plus de « L'essentiel ».
- **Une idée par diapo**, 3 à 5 puces courtes. Au-delà, coupe en deux diapos.
- Le lexique (M00) peut utiliser plus de tableaux, mais il alterne avec des diapos `colonnes`, `retenir` et des schémas toutes les 3 ou 4 diapos.

### Schémas : au moins un toutes les 2 diapos de contenu

Les schémas viennent des **diapos modèles** (section 7). Limites à respecter :
- **`flux`** : des étapes reliées par des flèches, pour un mécanisme, une voie nerveuse, un déroulé ou un arbre décisionnel. **3 à 5 étapes**, textes courts (une étape peut tenir sur 2 lignes avec `\n`). Avec des puces, le flux s'affiche verticalement à droite ; sans puces, horizontalement en pleine largeur.
- **`image`** : une illustration de **Wikimedia Commons** (anatomie, coupes, voies), toujours avec un crédit (auteur, licence).
  - Cherche le fichier avec WebSearch (`site:commons.wikimedia.org <sujet>`). Relève son nom exact, son auteur et sa licence (CC BY, CC BY-SA ou domaine public seulement).
  - Calcule l'adresse : `f=Nom_du_fichier.png; h=$(printf %s "$f" | md5sum | cut -c1-2); echo https://upload.wikimedia.org/wikipedia/commons/${h:0:1}/$h/$f`.
  - Exemple qui fonctionne : `https://upload.wikimedia.org/wikipedia/commons/1/14/Blausen_0329_EarAnatomy_InternalEar.png`, crédit « Blausen.com staff (2014), Wikimedia Commons, CC BY 3.0 ».
  - Les planches de Gray (domaine public) sont précieuses pour l'anatomie.
  - **Figures d'articles (demande de Matis, 31/10/2026 : « complète bien avec des schémas des articles »)** : utilise aussi les figures d'articles **en accès libre sous licence CC BY ou CC BY-SA** (vérifie la licence avec `get_copyright_status` ou sur la page PMC de l'article ; jamais une figure d'un article sous droits, même cité). Tracés de VNG, courbes de vHIT, enregistrements de fauteuil rotatoire, schémas de vascularisation, arbres décisionnels publiés : c'est ce qui rend un cours de DU concret. Adresse de l'image : le fichier de la figure sur `europepmc.org` ou `ncbi.nlm.nih.gov/pmc` (lien direct vers le .jpg ou le .png). Crédit obligatoire : « Figure <n>, <Premier auteur> et al., <revue> <année>, PMID <n>, CC BY 4.0 ». Vise **au moins 2 figures d'articles** dans chaque cours de tests (M05) ou d'anatomie (M01, M02), quand il en existe.
  - **Tu n'as pas besoin d'ouvrir l'image toi-même** : ton environnement bloque Wikimedia et Europe PMC, mais c'est Google Slides qui télécharge l'image depuis l'adresse, pas toi. Trouve l'adresse avec WebSearch (ou calcule-la pour Wikimedia, ci-dessus), passe-la à `replaceAllShapesWithImage`, et regarde seulement si Slides l'accepte. Ne renonce pas aux figures parce que l'adresse ne s'ouvre pas chez toi.
  - Si l'image est refusée, remplace-la par un `flux` ou un tableau.
- **`chiffres`** : **2 ou 3** grands chiffres clés, à droite des puces.
- La diapo **`tableau`** pour les comparaisons à plusieurs critères et le vocabulaire : **2 ou 3 colonnes, 9 lignes au maximum** (en-tête compris), textes courts. Avec modération (voir plus haut).
- La diapo **`colonnes`** : deux cartes côte à côte (périphérique / central, canalolithiase / cupulolithiase, adulte / enfant…), chacune avec un titre et 2 à 5 puces (380 caractères au maximum par carte).
- La diapo **`cercles`** (dans `schema`, sans puces) : `{"type": "cercles", "elements": [["5-8 %", "Prévalence des vertiges chez l'enfant (3-10 ans)"], ...]}`, 3 ou 4 éléments.
- Le champ **`conclusion`** d'une diapo de puces : une phrase courte affichée en gras en bas (« > … »).
- La diapo **`retenir`** : une phrase forte encadrée (`message`, 320 caractères au maximum) et 1 à 3 puces en dessous.
- Conclusion (« > … ») : **55 caractères au maximum**, une seule ligne ; sur deux lignes, elle touche l'encadré des sources.
- Diapo de puces avec conclusion : au plus 8 lignes de texte (environ 5 puces d'une ligne et demie) ; au-delà, le corps passe en 19 pt (`remplir.py` le fait tout seul), et s'il ne tient toujours pas, coupe la diapo en deux.
- Après une construction ratée ou reprise, **supprime toutes les diapos en trop** : la présentation ne contient que les diapos du plan.
- Titre : 34 caractères au maximum (au-delà, il passe sur deux lignes et chevauche le texte). Si un titre plus long est indispensable, mets-le en 19 pt (`remplir.py` le fait tout seul ; à la main, `updateTextStyle` fontSize 19 sur la zone du titre).
- Texte des puces : 360 caractères au maximum en pleine largeur (texte en 22 pt), 300 à côté d'un schéma.

## 7. Construire un cours : copie du modèle, duplication, remplacement de textes

Tous les cours partent de la présentation **« Modèle DU »** (son identifiant est dans les paramètres de ta tâche). Elle contient, en fin de présentation, des **diapos modèles masquées** (identifiants commençant par `M` : `Mtitre`, `Msection`, `Mtexte`, `Mplan`, `Mrefs`, `Mimage`, `Mimageseule`, `Mfluxv3` à `Mfluxv5`, `Mfluxh3` à `Mfluxh5`, `Mchiffres2`, `Mchiffres3`, `Mcercles3`, `Mcercles4`, `Mcolonnes2`, `Mretenir`, `Mtab2`, `Mtab3`) avec des textes à remplacer : `{{TITRE}}`, `{{PUCES}}`, `{{SOURCES}}`, `{{NUM}}`, `{{E1}}`…, `{{C1}}`/`{{L1}}`…, `{{T1}}`/`{{P1}}`, `{{T2}}`/`{{P2}}` (colonnes), `{{MESSAGE}}` (retenir), `{{SURTITRE}}`, `{{CONCLUSION}}`, `{{a1}}`… (tableaux), `{{IMAGE}}`, `{{CREDIT}}`, `{{LEGENDE}}`.

**Une fois le cours construit, supprime ces diapos modèles de la copie du cours** (`deleteObject` sur chaque identifiant commençant par `M`) : masquées dans Slides, elles sortent quand même quand Matis télécharge le cours en PDF (remarque de Matis, 30/10/2026). Ne touche jamais aux diapos modèles de la présentation « Modèle DU » elle-même.

Chaque diapo du cours = 3 petites requêtes + des remplacements de texte :
1. `duplicateObject` du modèle, avec `objectIds` = `{"<Modèle>": "<prefixe><num sur 3 chiffres>diapo", "<Modèle>_corps": "…diapo_corps"}` (et `"<Modèle>_tab": "…diapo_tab"` pour un tableau ; `"Mcolonnes2_c1": "…diapo_c1", "Mcolonnes2_c2": "…diapo_c2"` pour des colonnes) ;
2. `updateSlidesPosition` vers `insertionIndex` = numéro de la diapo − 1 ;
3. `updateSlideProperties` `isSkipped: false` (la copie hérite du masquage) ;
4. un `replaceAllText` par texte, **toujours avec `pageObjectIds` = [la nouvelle diapo]** ; le gras se met ensuite avec `updateTextStyle` sur `…diapo_corps` (plages de caractères) ; l'image avec `replaceAllShapesWithImage` (`containsText` `{{IMAGE}}`) ; les lignes de tableau inutilisées avec `deleteTableRow`.

Le script **`scripts/remplir.py plan.json sortie/ [prefixe] [premiere_diapo]`** fait tout cela et écrit `sortie/paquet_01.json` (10 diapos), `paquet_02.json`… à envoyer chacun avec **un** `update_presentation`, recopié à l'identique. Format du plan : en tête de `scripts/construire_diapos.py`. S'il refuse un schéma ou un texte trop long, il affiche « ATTENTION » : corrige le plan jusqu'à `OK`. Depuis le 29/10/2026, Matis a autorisé `remplir.py` et `ajuster_mise_en_page.py` dans le script d'installation de son environnement : écris le plan avec l'outil Write, place-toi dans `diaporamas/` avec un `cd` à part, puis lance le script dans sa propre commande commençant par `python3 scripts/`.

**Si l'exécution du script est refusée**, écris toi-même les requêtes en suivant exactement le schéma ci-dessus : c'est simple et léger. Ne t'arrête pas pour autant et n'attends pas d'autorisation : construis au moins 25 diapos par passage, par paquets de 5 à 10 diapos (un `update_presentation` par paquet), note dans N où tu en es (ex. `40/100`), et le passage suivant reprend à la diapo suivante. Un cours « En cours » avec 0 diapo construite après un passage est un échec.

1. **Premier passage** :
   - fais la recherche, écris le **plan JSON complet**, vérifie-le avec le script ;
   - enregistre le plan sur Drive, dans le dossier du module : `create_file` avec `textContent`, `contentMimeType: application/json`, `disableConversionToGoogleType: true`, titre « plan – <Ordre>. <Titre>.json ». **Un plan de 60 à 100 diapos est long : s'il ne passe pas en un fichier, découpe-le en deux** (« … (diapos 1-50).json » et « … (diapos 51-100).json », chacun un JSON valide avec sa propre liste `diapos`). Le plan sur Drive est obligatoire : sans lui, une mise à jour devient impossible ;
   - crée la présentation : **`copy_file` de « Modèle DU »** dans le dossier du module, titre « <Ordre>. <Titre> », et note son lien en F ;
   - envoie les paquets, à la suite : un cours entier tient en un seul passage (environ 5 paquets) ;
   - après chaque paquet, mets à jour N (« 20/43 »).
2. **Si un passage s'arrête avant la fin** : au passage suivant, relis le plan sur Drive (`read_file_content`), regarde les diapos présentes (`read_presentation`, `fields: ["slides.objectId"]`), et relance le script avec le même préfixe et `premiere_diapo` = première diapo manquante.
3. **À la fin** : supprime les 21 diapos modèles `M…` de la présentation du cours, écris G et N (« 43/43 »), puis passe le statut à `À relire`.

**Cours construits avant le 28/10/2026 au soir (modèles version 1)** : leurs diapos modèles internes sont anciennes (schémas en étapes déformés, pas de logo, sources sans encadré). Pour les refaire, ne réutilise pas l'ancienne présentation :
- crée une **nouvelle copie de « Modèle DU »** dans le dossier du module ;
- reprends le plan sur Drive en appliquant la section 6 (variété, colonnes, retenir, pas de source dans le texte) et reconstruis tout ;
- remplace le lien en F ;
- mets l'ancienne présentation et l'ancien plan à la corbeille.

**Mise à jour ou correction lourde d'un cours existant** (sa présentation n'a plus de diapos modèles) :
- relis son plan sur Drive et modifie-le ;
- crée une **nouvelle copie de « Modèle DU »** dans le dossier du module et reconstruis-y tout le cours, puis supprime ses diapos modèles `M…` ;
- remplace le lien en F, mets l'ancienne présentation à la corbeille ;
- remplace le plan sur Drive (corbeille pour l'ancien).

Une petite correction (texte, taille, position) se fait directement dans la présentation, sans reconstruire. Pour ajouter une diapo, duplique une diapo du cours de même type (`duplicateObject`) et remplace ses textes.


## 12. Partage des cours (décision de Matis, 03/11/2026)

Chaque nouvelle présentation de cours doit être partagée **dès sa création**, et non laissée privée :
- **Accès** : « toute personne disposant du lien » en **lecteur** (`share_file` avec `permissionId: "anyoneWithLink"`, `role: "reader"`). C'est ce lien qu'affiche le site.
- **Téléchargement interdit aux lecteurs** : `update_file` avec `downloadRestriction: {"restrictedReader": true}`. Matis reste seul à pouvoir modifier et télécharger.
- Si l'un de ces deux appels est refusé, ne tente pas de contournement : signale-le dans ton bilan (« partage du cours <numéro> à faire à la main »), et le relecteur le vérifiera.
- Ne partage jamais le dossier « Notes du DIU » ni les plans JSON : ils restent privés.
