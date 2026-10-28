# Projet : site du DU (à faire plus tard, avec une équipe d'agents codeurs)

Demande de Matis (27/10/2026) : mettre en ligne les cours du DU de rééducation vestibulaire sur un site public, par exemple sur un sous-domaine de son site.

- Un onglet par module (M00 à M12), et dans chaque onglet tous les cours du module.
- Le site se met à jour tout seul quand un cours est validé ou mis à jour (onglet « Diaporamas » du tableau = source de vérité).

Pistes techniques à valider le moment venu :
- site statique (GitHub Pages ou hébergement OVH existant), sous-domaine via un enregistrement DNS chez OVH ;
- cours intégrés via « Publier sur le web » de Google Slides, ou export PDF ;
- seuls les cours au statut `Validé` sont publiés ;
- mentions : sources et crédits d'images visibles, avertissement « contenu de formation, ne remplace pas un avis médical », droits des images (Wikimedia : licence et crédit).

## Décisions de Matis

- 27/10/2026 : affichage des cours en Google Slides intégrés au site. Le site se met à jour tout seul à chaque mise à jour d'un cours.
- 27/10/2026 : site réservé aux kinés, avec un mot de passe. Matis prépare les accès dans les jours à venir.
- Lancement prévu dès que les premiers modules (M00 à M02) sont validés, sans attendre la fin du DU.

À ne pas oublier : les présentations intégrées doivent être partagées par lien. Une personne qui récupère ce lien peut ouvrir le cours sans mot de passe. Si c'est gênant, on affichera des exports (images ou PDF) servis par le site protégé.
- 27/10/2026 : public très restreint (Matis et quelques kinés). On retient l'option simple : Google Slides intégrés, avec un mot de passe sur le site.

## Avancement

- 28/10/2026 : le sous-domaine bdd.kinevestibulaire.fr est créé par Matis. Le site est écrit en PHP, avec comptes kinés, un onglet par module et les cours en Google Slides intégrés. Il est livré en zip pour FileZilla. Matis n'a pas besoin du dépôt GitHub « site-DU » : le code source est gardé ici, dans `projets/site-du/`.
- Source des cours : onglet `Site` du tableau, qui filtre l'onglet `Diaporamas` avec une formule QUERY. Cet onglet est publié en CSV.
- Le dossier « Notes du DIU de Matis » n'hérite pas des partages : il reste privé même si le dossier du DU est partagé par lien.

## Mises à jour du site (consigne de Matis, 28/10/2026)

Matis met lui-même les fichiers en ligne avec FileZilla.
- Les cours se mettent à jour tout seuls, via l'onglet `Site` et Google Slides : aucun envoi de fichier n'est nécessaire.
- Si le code du site doit changer, Mage modifie `projets/site-du/` et envoie à Matis un message qui précise les fichiers à remplacer, avec le zip.
- Ne jamais écraser le dossier `data/` du serveur : il contient les comptes et les réglages.
