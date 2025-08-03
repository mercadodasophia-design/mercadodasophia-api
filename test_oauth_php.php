<?php
/**
 * Teste OAuth2 AliExpress em PHP
 * Para verificar se o problema é específico do Python
 */

// Configurações
$app_key = '517616';
$app_secret = 'TTqNmTMs5Q0QiPbulDNenhXr2My18nN4';
$code = '3_517616_r6Crw99S4AdLEpfOX5Q3gaHn1926'; // Use o código que você recebeu

// Função para gerar timestamp no formato correto
function ali_timestamp() {
    // UTC+8 (China timezone)
    $utc = new DateTime('now', new DateTimeZone('UTC'));
    $china_tz = new DateTimeZone('Asia/Shanghai');
    $china_time = $utc->setTimezone($china_tz);
    return $china_time->format('Y-m-d H:i:s');
}

// Função para gerar assinatura MD5
function generate_sign($params, $app_secret) {
    ksort($params);
    $param_string = '';
    foreach ($params as $key => $value) {
        $param_string .= $key . $value;
    }
    $sign_string = $app_secret . $param_string . $app_secret;
    return strtoupper(md5($sign_string));
}

// Testar OAuth2
function test_oauth($app_key, $app_secret, $code) {
    $timestamp = ali_timestamp();
    
    $params = [
        'method' => 'auth.token.create',
        'app_key' => $app_key,
        'code' => $code,
        'timestamp' => $timestamp,
        'sign_method' => 'md5',
        'format' => 'json',
        'v' => '2.0'
    ];
    
    $params['sign'] = generate_sign($params, $app_secret);
    
    echo "🔄 Testando OAuth2 com PHP\n";
    echo "📝 Timestamp: $timestamp\n";
    echo "📝 Parâmetros: " . json_encode($params, JSON_PRETTY_PRINT) . "\n";
    
    // Fazer requisição
    $url = 'https://api-sg.aliexpress.com/rest';
    $post_data = http_build_query($params);
    
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $post_data);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_HTTPHEADER, [
        'Content-Type: application/x-www-form-urlencoded'
    ]);
    
    $response = curl_exec($ch);
    $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    
    echo "📊 Status Code: $http_code\n";
    echo "📄 Response: $response\n";
    
    if ($http_code == 200) {
        $data = json_decode($response, true);
        if (isset($data['access_token'])) {
            echo "✅ SUCCESSO! Access token obtido!\n";
            return $data;
        } else {
            echo "❌ Erro na resposta: " . json_encode($data) . "\n";
        }
    } else {
        echo "❌ Erro HTTP: $http_code\n";
    }
    
    return null;
}

// Executar teste
echo "🚀 TESTE OAUTH2 ALIEXPRESS EM PHP\n";
echo "=====================================\n";
test_oauth($app_key, $app_secret, $code);
?> 