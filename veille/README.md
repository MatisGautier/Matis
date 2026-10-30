# Veille vestibulaire

Consignes et programmes des agents de veille scientifique de Matis Gautier, kinésithérapeute vestibulaire.

| Fichier | Rôle |
|---|---|
| `regles.md` | Règles communes : périmètre, sources, score, catégories, tableau, PDF |
| `collecte.md` | Agent Collecte, vers 7 h et 19 h : trouve, trie et note les articles |
| `redaction.md` | Agent Rédaction, vers 7 h 45 : fiches, fiches patients, synthèses (lundi, mercredi, vendredi) et un seul petit mail le matin (noms des nouvelles fiches) ; PDF rangés par catégorie et listés dans l'onglet « Mes fiches » |
| `scripts/generer_pdf.py` | PDF de la fiche brainstorming (2 pages) et des synthèses |
| `scripts/generer_fiche_patient.py` | PDF de la fiche patient (1 page) |
| `scripts/verifier_pdf.py` | Vérifie qu'un PDF est intact avant et après son dépôt |

Chaque tâche planifiée récupère ce dossier (branche `veille`) au démarrage. Ses consignes contiennent seulement les paramètres privés : adresses, identifiants du tableau, des dossiers Drive et des libellés. Pour changer une règle, il suffit de modifier le fichier ici : le prochain passage l'appliquera.
