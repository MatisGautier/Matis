<?php
/** @var string $titre_page */
/** @var ?array $u */
/** @var ?string $module_actif */
$u = $u ?? null;
$module_actif = $module_actif ?? null;
?><!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title><?= h($titre_page) ?> · DU de rééducation vestibulaire</title>
<link rel="stylesheet" href="assets/style.css?v=1">
</head>
<body>
<header class="bandeau">
  <a class="marque" href="index.php"><span class="logo" aria-hidden="true">◎</span> DU de rééducation vestibulaire</a>
  <?php if ($u): ?>
  <nav class="compte">
    <span class="qui"><?= h($u['nom'] ?: $u['id']) ?></span>
    <?php if (!empty($u['admin'])): ?><a href="admin.php">Administration</a><?php endif; ?>
    <a href="mot-de-passe.php">Mot de passe</a>
    <a href="deconnexion.php">Se déconnecter</a>
  </nav>
  <?php endif; ?>
</header>
<?php if ($u): ?>
<nav class="onglets" aria-label="Modules">
  <?php foreach (MODULES as $code => $nom): ?>
  <a href="module.php?m=<?= $code ?>"<?= $code === $module_actif ? ' class="actif" aria-current="page"' : '' ?> title="<?= h($nom) ?>"><?= $code ?><span> · <?= h($nom) ?></span></a>
  <?php endforeach; ?>
</nav>
<?php endif; ?>
<main>
