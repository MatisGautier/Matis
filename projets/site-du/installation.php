<?php
// Première visite : création du compte administrateur. Désactivée dès qu'un compte existe.
require __DIR__ . '/inc/app.php';
if (installe()) {
    header('Location: index.php');
    exit;
}
$erreur = '';
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    verifier_jeton();
    $id = strtolower(trim((string) ($_POST['identifiant'] ?? '')));
    $mdp = (string) ($_POST['mot_de_passe'] ?? '');
    if (!identifiant_valide($id)) {
        $erreur = 'Identifiant : 2 à 40 caractères, lettres minuscules, chiffres, point, tiret.';
    } elseif (strlen($mdp) < 10) {
        $erreur = 'Mot de passe : 10 caractères au minimum.';
    } elseif ($mdp !== ($_POST['confirmation'] ?? '')) {
        $erreur = 'Les deux mots de passe sont différents.';
    } else {
        $compte = ['nom' => trim((string) ($_POST['nom'] ?? '')), 'hash' => password_hash($mdp, PASSWORD_DEFAULT),
            'admin' => true, 'version' => 1, 'cree_le' => date('d/m/Y')];
        ecrire_json(FICHIER_COMPTES, [$id => $compte]);
        connecter($id, $compte);
        header('Location: admin.php');
        exit;
    }
}
$titre_page = 'Installation';
require __DIR__ . '/inc/entete.php';
?>
<form class="carte-formulaire" method="post">
  <h1>Installation</h1>
  <p class="discret">Créez le compte administrateur (le vôtre). Cette page disparaît ensuite.</p>
  <?php if (!is_writable(DOSSIER_DATA)): ?><p class="erreur">Le dossier <code>data</code> n'est pas accessible en écriture sur l'hébergement.</p><?php endif; ?>
  <?php if ($erreur): ?><p class="erreur"><?= h($erreur) ?></p><?php endif; ?>
  <?= champ_jeton() ?>
  <label>Nom affiché <input name="nom" value="<?= h($_POST['nom'] ?? '') ?>" placeholder="Matis Gautier"></label>
  <label>Identifiant <input name="identifiant" value="<?= h($_POST['identifiant'] ?? '') ?>" placeholder="matis" required></label>
  <label>Mot de passe (10 caractères minimum) <input type="password" name="mot_de_passe" autocomplete="new-password" required></label>
  <label>Confirmation <input type="password" name="confirmation" autocomplete="new-password" required></label>
  <button class="bouton">Créer le compte</button>
</form>
<?php require __DIR__ . '/inc/pied.php';
