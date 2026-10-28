<?php
require __DIR__ . '/inc/app.php';
$u = exiger_connexion();
$par_module = cours_par_module();
$total = array_sum(array_map('count', $par_module));
$titre_page = 'Accueil';
require __DIR__ . '/inc/entete.php';
?>
<section class="intro">
  <h1>Bonjour <?= h($u['nom'] ?: $u['id']) ?></h1>
  <p>Les cours du DU, module par module. Chaque cours est un diaporama sourcé, mis à jour au fil de la littérature scientifique : ce que vous voyez ici est toujours la dernière version.</p>
  <p class="discret"><?= $total ?> cours en ligne.</p>
</section>
<section class="grille-modules">
  <?php foreach (MODULES as $code => $nom): $n = count($par_module[$code]); ?>
  <a class="carte-module<?= $n ? '' : ' vide' ?>" href="module.php?m=<?= $code ?>">
    <span class="code"><?= $code ?></span>
    <span class="nom"><?= h($nom) ?></span>
    <span class="compte"><?= $n ? $n . ' cours' : 'Bientôt' ?></span>
  </a>
  <?php endforeach; ?>
</section>
<?php require __DIR__ . '/inc/pied.php';
