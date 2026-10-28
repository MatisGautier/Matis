<?php
require __DIR__ . '/inc/app.php';
if (!installe()) {
    header('Location: installation.php');
    exit;
}
$suite = (string) ($_GET['suite'] ?? $_POST['suite'] ?? 'index.php');
$suite = ltrim($suite, '/');
if (!preg_match('~^[a-z0-9-]+\.php(\?[A-Za-z0-9=&_%.-]*)?$~', $suite)) {
    $suite = 'index.php';
}
$erreur = '';
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    verifier_jeton();
    if (trop_d_essais()) {
        $erreur = 'Trop de tentatives. Réessayez dans un quart d\'heure.';
    } else {
        $id = strtolower(trim((string) ($_POST['identifiant'] ?? '')));
        $compte = comptes()[$id] ?? null;
        if ($compte && password_verify((string) ($_POST['mot_de_passe'] ?? ''), $compte['hash'])) {
            connecter($id, $compte);
            header('Location: ' . $suite);
            exit;
        }
        noter_essai_rate();
        usleep(600000);
        $erreur = 'Identifiant ou mot de passe incorrect.';
    }
}
$titre_page = 'Connexion';
require __DIR__ . '/inc/entete.php';
?>
<form class="carte-formulaire" method="post" action="connexion.php">
  <h1>Connexion</h1>
  <p class="discret">Espace réservé aux kinésithérapeutes invités.</p>
  <?php if ($erreur): ?><p class="erreur"><?= h($erreur) ?></p><?php endif; ?>
  <?= champ_jeton() ?>
  <input type="hidden" name="suite" value="<?= h($suite) ?>">
  <label>Identifiant <input name="identifiant" autocomplete="username" required autofocus></label>
  <label>Mot de passe <input type="password" name="mot_de_passe" autocomplete="current-password" required></label>
  <button class="bouton">Se connecter</button>
</form>
<?php require __DIR__ . '/inc/pied.php';
