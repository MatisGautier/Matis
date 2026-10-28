<?php
// Cœur du site du DU : session, comptes, réglages, lecture des cours publiés.
declare(strict_types=1);

const DOSSIER_DATA = __DIR__ . '/../data';
const FICHIER_COMPTES = DOSSIER_DATA . '/utilisateurs.json';
const FICHIER_REGLAGES = DOSSIER_DATA . '/reglages.json';
const FICHIER_CACHE = DOSSIER_DATA . '/cours.csv';
const FICHIER_ESSAIS = DOSSIER_DATA . '/essais.json';
const CACHE_SECONDES = 300;          // les cours sont relus toutes les 5 minutes
const ESSAIS_MAX = 8;                // tentatives de connexion par adresse IP et par quart d'heure

const MODULES = [
    'M00' => 'Introduction et vocabulaire',
    'M01' => "Anatomie de l'oreille",
    'M02' => 'Système nerveux et voies vestibulaires',
    'M03' => 'Physiologie et réflexes',
    'M04' => 'Liens et intégration',
    'M05' => 'Examen clinique et tests',
    'M06' => 'Pathologies vestibulaires',
    'M07' => 'Neurologie',
    'M08' => 'Pédiatrie',
    'M09' => 'Gériatrie',
    'M10' => 'Rééducation',
    'M11' => 'Traitements médicaux et chirurgicaux',
    'M12' => 'Pratique professionnelle, cas cliniques et recherche',
];

header('X-Frame-Options: DENY');
header('X-Content-Type-Options: nosniff');
header('Referrer-Policy: same-origin');

session_set_cookie_params([
    'lifetime' => 0,
    'path' => '/',
    'secure' => !empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off',
    'httponly' => true,
    'samesite' => 'Lax',
]);
session_name('du_session');
session_start();

function h(?string $texte): string
{
    return htmlspecialchars((string) $texte, ENT_QUOTES, 'UTF-8');
}

function lire_json(string $fichier, array $defaut = []): array
{
    if (!is_file($fichier)) {
        return $defaut;
    }
    $donnees = json_decode((string) file_get_contents($fichier), true);
    return is_array($donnees) ? $donnees : $defaut;
}

function ecrire_json(string $fichier, array $donnees): void
{
    $tmp = $fichier . '.tmp';
    file_put_contents($tmp, json_encode($donnees, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE), LOCK_EX);
    rename($tmp, $fichier);
}

function comptes(): array
{
    return lire_json(FICHIER_COMPTES);
}

function reglages(): array
{
    return lire_json(FICHIER_REGLAGES, ['csv' => '', 'afficher_en_relecture' => true]);
}

function installe(): bool
{
    return comptes() !== [];
}

// --- Sécurité des formulaires ---

function jeton(): string
{
    if (empty($_SESSION['jeton'])) {
        $_SESSION['jeton'] = bin2hex(random_bytes(32));
    }
    return $_SESSION['jeton'];
}

function champ_jeton(): string
{
    return '<input type="hidden" name="jeton" value="' . h(jeton()) . '">';
}

function verifier_jeton(): void
{
    if (!hash_equals(jeton(), (string) ($_POST['jeton'] ?? ''))) {
        http_response_code(400);
        exit('Formulaire expiré : revenez en arrière et réessayez.');
    }
}

// --- Connexion ---

function utilisateur(): ?array
{
    $id = $_SESSION['utilisateur'] ?? null;
    if ($id === null) {
        return null;
    }
    $compte = comptes()[$id] ?? null;
    // un compte supprimé ou un mot de passe changé ferme les sessions ouvertes
    if ($compte === null || ($compte['version'] ?? 0) !== ($_SESSION['version'] ?? -1)) {
        unset($_SESSION['utilisateur']);
        return null;
    }
    return $compte + ['id' => $id];
}

function exiger_connexion(bool $admin = false): array
{
    if (!installe()) {
        header('Location: installation.php');
        exit;
    }
    $u = utilisateur();
    if ($u === null) {
        header('Location: connexion.php?suite=' . rawurlencode($_SERVER['REQUEST_URI'] ?? 'index.php'));
        exit;
    }
    if ($admin && empty($u['admin'])) {
        http_response_code(403);
        exit('Page réservée à l\'administrateur.');
    }
    return $u;
}

function trop_d_essais(): bool
{
    $ip = $_SERVER['REMOTE_ADDR'] ?? '?';
    $essais = array_filter(lire_json(FICHIER_ESSAIS)[$ip] ?? [], fn($t) => $t > time() - 900);
    return count($essais) >= ESSAIS_MAX;
}

function noter_essai_rate(): void
{
    $ip = $_SERVER['REMOTE_ADDR'] ?? '?';
    $tous = lire_json(FICHIER_ESSAIS);
    foreach ($tous as $cle => $liste) {
        $tous[$cle] = array_values(array_filter($liste, fn($t) => $t > time() - 900));
        if (!$tous[$cle]) {
            unset($tous[$cle]);
        }
    }
    $tous[$ip][] = time();
    ecrire_json(FICHIER_ESSAIS, $tous);
}

function connecter(string $id, array $compte): void
{
    session_regenerate_id(true);
    $_SESSION['utilisateur'] = $id;
    $_SESSION['version'] = $compte['version'] ?? 0;
}

function identifiant_valide(string $id): bool
{
    return (bool) preg_match('/^[a-z0-9._-]{2,40}$/', $id);
}

// --- Cours publiés (onglet « Site » du tableau, publié en CSV) ---

/** Module d'un cours d'après son numéro d'ordre : 1-99 -> M00, 101 -> M01, 1018 -> M10. */
function module_du_numero(string $ordre): string
{
    $n = (int) floor((float) str_replace(',', '.', $ordre));
    return sprintf('M%02d', $n < 100 ? 0 : intdiv($n, 100));
}

function telecharger(string $url): ?string
{
    if (function_exists('curl_init')) {
        $c = curl_init($url);
        curl_setopt_array($c, [CURLOPT_RETURNTRANSFER => true, CURLOPT_FOLLOWLOCATION => true,
            CURLOPT_TIMEOUT => 15, CURLOPT_USERAGENT => 'site-du']);
        $corps = curl_exec($c);
        $ok = curl_getinfo($c, CURLINFO_HTTP_CODE) === 200;
        curl_close($c);
        return $ok && is_string($corps) ? $corps : null;
    }
    $corps = @file_get_contents($url);
    return $corps === false ? null : $corps;
}

/** Liste des cours à afficher. Lit le CSV publié, avec un cache de quelques minutes. */
function cours(): array
{
    $url = reglages()['csv'] ?? '';
    if ($url === '') {
        return [];
    }
    $frais = is_file(FICHIER_CACHE) && filemtime(FICHIER_CACHE) > time() - CACHE_SECONDES;
    if (!$frais) {
        $csv = telecharger($url);
        if ($csv !== null && str_contains($csv, ',')) {
            file_put_contents(FICHIER_CACHE, $csv, LOCK_EX);
        } elseif (is_file(FICHIER_CACHE)) {
            touch(FICHIER_CACHE);   // Google indisponible : on garde l'ancienne liste
        }
    }
    if (!is_file(FICHIER_CACHE)) {
        return [];
    }
    $relecture = !empty(reglages()['afficher_en_relecture']);
    $liste = [];
    $f = fopen(FICHIER_CACHE, 'r');
    $entete = fgetcsv($f, 0, ',', '"', '');
    while (($ligne = fgetcsv($f, 0, ',', '"', '')) !== false) {
        [$ordre, $titre, $statut, $lien, $diapos, $maj, $module, $type] = array_pad($ligne, 8, '');
        $id = presentation_id($lien);
        if ($id === null || $titre === '') {
            continue;
        }
        $statut = trim($statut);
        if ($statut !== 'Validé' && !($relecture && in_array($statut, ['À relire', 'À corriger', 'À mettre à jour'], true))) {
            continue;
        }
        $module = preg_match('/^M\d\d$/', trim($module)) ? trim($module) : module_du_numero($ordre);
        $liste[] = [
            'ordre' => trim($ordre), 'titre' => trim($titre), 'statut' => $statut,
            'presentation' => $id, 'diapos' => trim($diapos), 'maj' => trim($maj),
            'module' => $module, 'type' => trim($type),
        ];
    }
    fclose($f);
    usort($liste, fn($a, $b) => (float) str_replace(',', '.', $a['ordre']) <=> (float) str_replace(',', '.', $b['ordre']));
    return $liste;
}

function presentation_id(string $lien): ?string
{
    return preg_match('~/presentation/d/([A-Za-z0-9_-]{20,})~', $lien, $m) ? $m[1] : null;
}

function cours_par_module(): array
{
    $par = array_fill_keys(array_keys(MODULES), []);
    foreach (cours() as $c) {
        $par[$c['module']][] = $c;
    }
    return $par;
}
