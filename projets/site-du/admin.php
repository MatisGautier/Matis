<?php
require __DIR__ . '/inc/app.php';
$u = exiger_connexion(true);
$message = $erreur = '';
$mdp_genere = null;

function mot_de_passe_aleatoire(): string
{
    $lettres = 'abcdefghjkmnpqrstuvwxyzABCDEFGHJKMNPQRSTUVWXYZ23456789';
    $mdp = '';
    for ($i = 0; $i < 12; $i++) {
        $mdp .= $lettres[random_int(0, strlen($lettres) - 1)];
    }
    return $mdp;
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    verifier_jeton();
    $tous = comptes();
    $action = $_POST['action'] ?? '';
    $id = strtolower(trim((string) ($_POST['identifiant'] ?? '')));
    if ($action === 'ajouter') {
        if (!identifiant_valide($id)) {
            $erreur = 'Identifiant : 2 à 40 caractères, lettres minuscules, chiffres, point, tiret.';
        } elseif (isset($tous[$id])) {
            $erreur = 'Cet identifiant existe déjà.';
        } else {
            $mdp_genere = [$id, mot_de_passe_aleatoire()];
            $tous[$id] = ['nom' => trim((string) ($_POST['nom'] ?? '')), 'hash' => password_hash($mdp_genere[1], PASSWORD_DEFAULT),
                'admin' => false, 'version' => 1, 'cree_le' => date('d/m/Y')];
            ecrire_json(FICHIER_COMPTES, $tous);
        }
    } elseif ($action === 'reinitialiser' && isset($tous[$id])) {
        $mdp_genere = [$id, mot_de_passe_aleatoire()];
        $tous[$id]['hash'] = password_hash($mdp_genere[1], PASSWORD_DEFAULT);
        $tous[$id]['version'] = ($tous[$id]['version'] ?? 0) + 1;
        ecrire_json(FICHIER_COMPTES, $tous);
        if ($id === $u['id']) {
            connecter($id, $tous[$id]);
        }
    } elseif ($action === 'supprimer' && isset($tous[$id])) {
        if ($id === $u['id']) {
            $erreur = 'Vous ne pouvez pas supprimer votre propre compte.';
        } else {
            unset($tous[$id]);
            ecrire_json(FICHIER_COMPTES, $tous);
            $message = "Compte « $id » supprimé : il ne peut plus se connecter.";
        }
    } elseif ($action === 'reglages') {
        $csv = trim((string) ($_POST['csv'] ?? ''));
        if ($csv !== '' && !preg_match('~^https://docs\.google\.com/spreadsheets/d/e/[A-Za-z0-9_-]+/pub\?~', $csv)) {
            $erreur = 'Le lien doit être celui de « Publier sur le Web » au format CSV (https://docs.google.com/spreadsheets/d/e/…/pub?…output=csv).';
        } else {
            ecrire_json(FICHIER_REGLAGES, ['csv' => $csv, 'afficher_en_relecture' => !empty($_POST['afficher_en_relecture'])]);
            @unlink(FICHIER_CACHE);
            $message = 'Réglages enregistrés. ' . count(cours()) . ' cours trouvés.';
        }
    }
}
$r = reglages();
$titre_page = 'Administration';
require __DIR__ . '/inc/entete.php';
?>
<h1>Administration</h1>
<?php if ($message): ?><p class="succes"><?= h($message) ?></p><?php endif; ?>
<?php if ($erreur): ?><p class="erreur"><?= h($erreur) ?></p><?php endif; ?>
<?php if ($mdp_genere): ?>
<div class="encadre">
  <strong>À transmettre au kiné (affiché une seule fois) :</strong><br>
  Site : <code>https://<?= h($_SERVER['HTTP_HOST'] ?? 'bdd.kinevestibulaire.fr') ?></code><br>
  Identifiant : <code><?= h($mdp_genere[0]) ?></code><br>
  Mot de passe provisoire : <code><?= h($mdp_genere[1]) ?></code><br>
  <span class="discret">Il pourra le changer dans « Mot de passe ».</span>
</div>
<?php endif; ?>

<h2>Kinés ayant accès</h2>
<table class="tableau">
  <thead><tr><th>Identifiant</th><th>Nom</th><th>Créé le</th><th></th></tr></thead>
  <tbody>
  <?php foreach (comptes() as $id => $c): ?>
    <tr>
      <td><?= h($id) ?><?= !empty($c['admin']) ? ' <span class="pastille">admin</span>' : '' ?></td>
      <td><?= h($c['nom'] ?? '') ?></td>
      <td><?= h($c['cree_le'] ?? '') ?></td>
      <td class="actions-ligne">
        <form method="post"><?= champ_jeton() ?><input type="hidden" name="identifiant" value="<?= h($id) ?>">
          <button name="action" value="reinitialiser" class="lien">Nouveau mot de passe</button>
          <?php if ($id !== $u['id']): ?><button name="action" value="supprimer" class="lien danger" onclick="return confirm('Supprimer l\'accès de <?= h($id) ?> ?')">Supprimer</button><?php endif; ?>
        </form>
      </td>
    </tr>
  <?php endforeach; ?>
  </tbody>
</table>

<form class="ligne-formulaire" method="post">
  <?= champ_jeton() ?>
  <input type="hidden" name="action" value="ajouter">
  <label>Nom <input name="nom" placeholder="Prénom Nom"></label>
  <label>Identifiant <input name="identifiant" placeholder="prenom.nom" required></label>
  <button class="bouton">Ajouter un kiné</button>
</form>

<h2>Source des cours</h2>
<form class="carte-formulaire large" method="post">
  <?= champ_jeton() ?>
  <input type="hidden" name="action" value="reglages">
  <label>Lien CSV de l'onglet « Site » (Fichier › Partager › Publier sur le Web)
    <input name="csv" value="<?= h($r['csv'] ?? '') ?>" placeholder="https://docs.google.com/spreadsheets/d/e/…/pub?gid=…&amp;single=true&amp;output=csv"></label>
  <label class="case"><input type="checkbox" name="afficher_en_relecture" value="1"<?= !empty($r['afficher_en_relecture']) ? ' checked' : '' ?>> Afficher aussi les cours en relecture (sinon seulement les cours « Validé »)</label>
  <button class="bouton">Enregistrer</button>
  <p class="discret"><?= count(cours()) ?> cours affichés actuellement. La liste se met à jour toute seule toutes les 5 minutes.</p>
</form>
<?php require __DIR__ . '/inc/pied.php';
