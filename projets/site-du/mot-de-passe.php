<?php
require __DIR__ . '/inc/app.php';
$u = exiger_connexion();
$message = $erreur = '';
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    verifier_jeton();
    $mdp = (string) ($_POST['nouveau'] ?? '');
    if (!password_verify((string) ($_POST['actuel'] ?? ''), $u['hash'])) {
        $erreur = 'Mot de passe actuel incorrect.';
    } elseif (strlen($mdp) < 10) {
        $erreur = 'Nouveau mot de passe : 10 caractères au minimum.';
    } elseif ($mdp !== ($_POST['confirmation'] ?? '')) {
        $erreur = 'Les deux mots de passe sont différents.';
    } else {
        $tous = comptes();
        $tous[$u['id']]['hash'] = password_hash($mdp, PASSWORD_DEFAULT);
        $tous[$u['id']]['version'] = ($tous[$u['id']]['version'] ?? 0) + 1;
        ecrire_json(FICHIER_COMPTES, $tous);
        connecter($u['id'], $tous[$u['id']]);
        $message = 'Mot de passe changé.';
    }
}
$titre_page = 'Mot de passe';
require __DIR__ . '/inc/entete.php';
?>
<form class="carte-formulaire" method="post">
  <h1>Changer mon mot de passe</h1>
  <?php if ($message): ?><p class="succes"><?= h($message) ?></p><?php endif; ?>
  <?php if ($erreur): ?><p class="erreur"><?= h($erreur) ?></p><?php endif; ?>
  <?= champ_jeton() ?>
  <label>Mot de passe actuel <input type="password" name="actuel" autocomplete="current-password" required></label>
  <label>Nouveau mot de passe (10 caractères minimum) <input type="password" name="nouveau" autocomplete="new-password" required></label>
  <label>Confirmation <input type="password" name="confirmation" autocomplete="new-password" required></label>
  <button class="bouton">Enregistrer</button>
</form>
<?php require __DIR__ . '/inc/pied.php';
