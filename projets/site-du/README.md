# Site du DU de rééducation vestibulaire

Site privé (bdd.kinevestibulaire.fr) qui présente les cours du DU de Matis Gautier :
un onglet par module (M00 à M12), chaque cours affiché en Google Slides intégré,
toujours à jour. Accès réservé aux kinés invités, avec identifiant et mot de passe.

## Fonctionnement

- **Source des cours** : l'onglet `Site` du tableau de la veille (formule QUERY sur l'onglet
  `Diaporamas` : cours « Validé », et en option ceux en relecture). Cet onglet seul est publié
  sur le Web en CSV ; le lien se colle dans la page Administration du site.
- Le site relit ce CSV toutes les 5 minutes : un cours validé ou mis à jour apparaît tout seul,
  sans redéploiement. Les diaporamas intégrés affichent toujours la dernière version.
- Module d'un cours : colonne « Module du DU », sinon son numéro (1-99 → M00, 101 → M01, 1018 → M10).
- **Comptes** : créés dans la page Administration (mot de passe provisoire affiché une fois,
  modifiable par le kiné), stockés hachés dans `data/utilisateurs.json`, jamais dans Git.
- Les diaporamas doivent être partagés « Tous les utilisateurs disposant du lien : lecteur »
  (partage du dossier Drive du DU). Le dossier des notes DIU de Matis n'hérite pas des partages.

## Fichiers

| Fichier | Rôle |
|---|---|
| `index.php` | accueil : les 13 modules et le nombre de cours |
| `module.php?m=M06` | les cours d'un module |
| `cours.php?p=<id>` | un cours : diaporama intégré, plein écran, PDF |
| `connexion.php`, `deconnexion.php`, `mot-de-passe.php` | compte |
| `installation.php` | première visite : création du compte administrateur |
| `admin.php` | kinés ayant accès, lien CSV, affichage des cours en relecture |
| `inc/app.php` | sessions, comptes, lecture et cache du CSV |
| `data/` | comptes, réglages, cache (non servi, non versionné) |

Sécurité : mots de passe hachés, jeton anti-CSRF, 8 essais de connexion par IP et par quart d'heure,
cookies `HttpOnly`/`SameSite`, HTTPS forcé, `inc/` et `data/` interdits par `.htaccess`, pages non indexées.

## Déploiement (OVH, PHP 8, FileZilla)

1. Envoyer tout le contenu de ce dépôt (sauf `.git`) dans le dossier du sous-domaine `bdd.kinevestibulaire.fr`.
2. Droits du dossier `data/` : 755 (écriture par PHP).
3. Ouvrir https://bdd.kinevestibulaire.fr : la page d'installation crée le compte administrateur.
4. Administration → coller le lien CSV de l'onglet `Site`
   (Google Sheets : Fichier › Partager › Publier sur le Web › onglet « Site » › CSV › Publier).
5. Ajouter les kinés.

Test local : `php -S 127.0.0.1:8080` dans ce dossier.
