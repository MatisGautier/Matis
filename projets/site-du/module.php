<?php
require __DIR__ . '/inc/app.php';
$u = exiger_connexion();
$module_actif = strtoupper((string) ($_GET['m'] ?? 'M00'));
if (!isset(MODULES[$module_actif])) {
    $module_actif = 'M00';
}
$liste = cours_par_module()[$module_actif];
$titre_page = $module_actif . ' · ' . MODULES[$module_actif];
require __DIR__ . '/inc/entete.php';
?>
<h1><span class="code"><?= $module_actif ?></span> <?= h(MODULES[$module_actif]) ?></h1>
<?php if (!$liste): ?>
  <p class="vide-message">Les cours de ce module sont en préparation. Ils apparaîtront ici automatiquement.</p>
<?php else: ?>
<ol class="liste-cours">
  <?php foreach ($liste as $c): ?>
  <li>
    <a href="cours.php?p=<?= h($c['presentation']) ?>">
      <span class="numero"><?= h($c['ordre']) ?></span>
      <span class="titre"><?= h($c['titre']) ?></span>
      <span class="infos">
        <?php if ($c['statut'] !== 'Validé'): ?><span class="pastille">En relecture</span><?php endif; ?>
        <?php if ($c['diapos']): ?><?= h($c['diapos']) ?> diapos<?php endif; ?>
        <?php if ($c['maj']): ?> · mis à jour le <?= h($c['maj']) ?><?php endif; ?>
      </span>
    </a>
  </li>
  <?php endforeach; ?>
</ol>
<?php endif; ?>
<?php require __DIR__ . '/inc/pied.php';
