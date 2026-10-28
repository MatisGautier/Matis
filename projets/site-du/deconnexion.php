<?php
require __DIR__ . '/inc/app.php';
$_SESSION = [];
session_destroy();
header('Location: connexion.php');
