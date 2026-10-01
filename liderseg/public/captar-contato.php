<?php
declare(strict_types=1);
header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');
function respond(int $code, bool $ok, string $message): void {
    http_response_code($code);
    echo json_encode(['ok' => $ok, 'message' => $message], JSON_UNESCAPED_UNICODE);
    exit;
}
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    header('Allow: POST');
    respond(405, false, 'Método não permitido.');
}
if ((int) ($_SERVER['CONTENT_LENGTH'] ?? 0) > 8192) respond(413, false, 'Envio muito grande.');
foreach (['name', 'whatsapp', 'company', 'submission_id'] as $field) {
    if (isset($_POST[$field]) && !is_string($_POST[$field])) respond(422, false, 'Dados inválidos.');
}
if (!empty($_POST['company'])) respond(422, false, 'Envio inválido.');
$name = trim($_POST['name'] ?? '');
$phone = preg_replace('/\D/', '', $_POST['whatsapp'] ?? '');
if (strlen($phone) === 13 && str_starts_with($phone, '55')) $phone = substr($phone, 2);
$id = $_POST['submission_id'] ?? '';
if (strlen($name) < 2 || strlen($name) > 400 || preg_match('/[\x00-\x1F]/', $name) || !preg_match('//u', $name) || !preg_match('/^[1-9]{2}9\d{8}$/', $phone) || !preg_match('/^[a-f0-9-]{36}$/i', $id)) {
    respond(422, false, 'Informe nome e WhatsApp válidos.');
}
// Configuração fora da pasta pública. Não coloque credenciais no diretório dist.
$configPath = dirname(__DIR__) . '/liderseg-contact-config.php';
if (!is_file($configPath) || !function_exists('curl_init')) respond(503, false, 'Formulário indisponível no momento.');
$config = require $configPath;
$url = $config['apps_script_url'] ?? '';
$secret = $config['secret'] ?? '';
if (!preg_match('~^https://script\.google\.com/macros/s/[A-Za-z0-9_-]+/exec$~', $url) || strlen($secret) < 32) respond(503, false, 'Formulário indisponível no momento.');
// Limite por IP usando arquivos temporários bloqueados, sem armazenar dados do contato.
$ratePath = sys_get_temp_dir() . '/liderseg-contact-' . hash_hmac('sha256', $_SERVER['REMOTE_ADDR'] ?? 'unknown', $secret);
$rateFile = @fopen($ratePath, 'c+');
if (!$rateFile || !flock($rateFile, LOCK_EX)) respond(503, false, 'Tente novamente mais tarde.');
$rate = json_decode(stream_get_contents($rateFile), true) ?: ['start' => time(), 'count' => 0];
if (time() - $rate['start'] >= 600) $rate = ['start' => time(), 'count' => 0];
if ($rate['count'] >= 10) { fclose($rateFile); respond(429, false, 'Aguarde alguns minutos antes de tentar novamente.'); }
$rate['count']++;
ftruncate($rateFile, 0);
rewind($rateFile);
fwrite($rateFile, json_encode($rate));
fclose($rateFile);
$curl = curl_init($url);
curl_setopt_array($curl, [
    CURLOPT_POST => true,
    CURLOPT_POSTFIELDS => json_encode(['secret' => $secret, 'name' => $name, 'whatsapp' => $phone, 'submission_id' => $id], JSON_UNESCAPED_UNICODE),
    CURLOPT_HTTPHEADER => ['Content-Type: application/json'],
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_FOLLOWLOCATION => true,
    CURLOPT_MAXREDIRS => 3,
    CURLOPT_PROTOCOLS => CURLPROTO_HTTPS,
    CURLOPT_REDIR_PROTOCOLS => CURLPROTO_HTTPS,
    CURLOPT_CONNECTTIMEOUT => 5,
    CURLOPT_TIMEOUT => 25,
]);
$body = curl_exec($curl);
$code = curl_getinfo($curl, CURLINFO_HTTP_CODE);
curl_close($curl);
$result = is_string($body) ? json_decode($body, true) : null;
if ($code !== 200 || !is_array($result) || ($result['ok'] ?? false) !== true) respond(502, false, 'Não foi possível confirmar o envio. Tente novamente.');
respond(200, true, 'Contato recebido.');
