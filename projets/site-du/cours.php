<?php
require __DIR__ . '/inc/app.php';
$u = exiger_connexion();
$p = (string) ($_GET['p'] ?? '');
$c = null;
foreach (cours() as $x) {
    if ($x['presentation'] === $p) {
        $c = $x;
        break;
    }
}
if ($c === null) {
    http_response_code(404);
    $titre_page = 'Cours introuvable';
    require __DIR__ . '/inc/entete.php';
    echo '<h1>Cours introuvable</h1><p><a href="index.php">Retour à l\'accueil</a></p>';
    require __DIR__ . '/inc/pied.php';
    exit;
}
$module_actif = $c['module'];
$titre_page = $c['titre'];
$id = rawurlencode($c['presentation']);
require __DIR__ . '/inc/entete.php';
?>
<p class="fil"><a href="module.php?m=<?= $c['module'] ?>"><?= $c['module'] ?> · <?= h(MODULES[$c['module']]) ?></a></p>
<h1><?= h($c['titre']) ?></h1>
<p class="infos">
  <?php if ($c['statut'] !== 'Validé'): ?><span class="pastille">En relecture</span><?php endif; ?>
  Cours <?= h($c['ordre']) ?><?php if ($c['diapos']): ?> · <?= h($c['diapos']) ?> diapos<?php endif; ?><?php if ($c['maj']): ?> · mis à jour le <?= h($c['maj']) ?><?php endif; ?>
</p>
<div class="diaporama">
  <iframe src="https://docs.google.com/presentation/d/<?= $id ?>/embed?start=false&amp;loop=false&amp;delayms=60000"
          title="<?= h($c['titre']) ?>" allowfullscreen loading="lazy"></iframe>
</div>
<p class="actions">
  <a class="bouton" href="https://docs.google.com/presentation/d/<?= $id ?>/present" target="_blank" rel="noopener">Plein écran</a>
  <a class="bouton secondaire" href="https://docs.google.com/presentation/d/<?= $id ?>/export/pdf" target="_blank" rel="noopener">Télécharger en PDF</a>
</p>
<?php require __DIR__ . '/inc/pied.php';
