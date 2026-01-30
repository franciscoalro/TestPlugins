# Execute este script quando:
# 1. Dispositivo estiver conectado via USB
# 2. Estiver pronto para clicar em PlayerEmbedAPI

$adb = "C:\Users\KYTHOURS\Desktop\platform-tools\adb.exe"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Captura de Logs - PlayerEmbedAPI" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar dispositivo
Write-Host "Verificando dispositivo..." -ForegroundColor Yellow
$devices = & $adb devices
Write-Host $devices
Write-Host ""

if ($devices -notmatch "device$") {
    Write-Host "ERRO: Nenhum dispositivo conectado!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Conecte o dispositivo via USB e tente novamente." -ForegroundColor Yellow
    exit
}

Write-Host "Dispositivo conectado!" -ForegroundColor Green
Write-Host ""

# Limpar logs
Write-Host "Limpando logs antigos..." -ForegroundColor Yellow
& $adb logcat -c
Write-Host "Logs limpos!" -ForegroundColor Green
Write-Host ""

# Instruções
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "INSTRUCOES" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "AGORA faca o seguinte:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Abra o filme no Cloudstream" -ForegroundColor White
Write-Host "2. Clique em 'Fontes'" -ForegroundColor White
Write-Host "3. Clique em 'PlayerEmbedAPI HD'" -ForegroundColor White
Write-Host "4. Aguarde aparecer o erro (ERROR 2004)" -ForegroundColor White
Write-Host ""
Write-Host "Pressione ENTER quando o erro aparecer..." -ForegroundColor Yellow
Read-Host

# Capturar logs
Write-Host ""
Write-Host "Capturando logs..." -ForegroundColor Yellow

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$arquivo = "playerembedapi_error_$timestamp.txt"

& $adb logcat -d > $arquivo

Write-Host "Logs completos salvos em: $arquivo" -ForegroundColor Green
Write-Host ""

# Filtrar logs relevantes
Write-Host "Filtrando logs relevantes..." -ForegroundColor Yellow
$arquivoFiltrado = "playerembedapi_error_${timestamp}_filtrado.txt"

Get-Content $arquivo | Select-String -Pattern "PlayerEmbedAPI|WebView|Captured|IMDB|Extract|Context|Loading|ERROR|timeout|MaxSeries" > $arquivoFiltrado

Write-Host "Logs filtrados salvos em: $arquivoFiltrado" -ForegroundColor Green
Write-Host ""

# Análise automática
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ANALISE AUTOMATICA" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$conteudo = Get-Content $arquivoFiltrado -Raw

# 1. Extract chamado?
if ($conteudo -match "EXTRACT CHAMADO") {
    Write-Host "[OK] PlayerEmbedAPI extract() foi chamado" -ForegroundColor Green
    
    # Extrair IMDB ID
    if ($conteudo -match "IMDB: (tt\d+)") {
        Write-Host "[OK] IMDB ID: $($matches[1])" -ForegroundColor Green
    }
} else {
    Write-Host "[ERRO] PlayerEmbedAPI extract() NAO foi chamado" -ForegroundColor Red
    Write-Host "       Possivel causa: Source nao foi detectada" -ForegroundColor Yellow
}

# 2. Context obtido?
if ($conteudo -match "Context obtido") {
    Write-Host "[OK] Context do Android obtido" -ForegroundColor Green
} else {
    Write-Host "[ERRO] Context NAO foi obtido" -ForegroundColor Red
}

# 3. WebView carregou?
if ($conteudo -match "Loading: (https://[^\s]+)") {
    Write-Host "[OK] WebView carregando: $($matches[1])" -ForegroundColor Green
} else {
    Write-Host "[ERRO] WebView NAO carregou URL" -ForegroundColor Red
}

# 4. URLs capturadas?
$capturedMatches = $conteudo | Select-String -Pattern "Captured: (https://[^\s]+)" -AllMatches
if ($capturedMatches) {
    $count = $capturedMatches.Matches.Count
    Write-Host "[OK] $count URL(s) capturada(s):" -ForegroundColor Green
    
    $capturedMatches.Matches | ForEach-Object {
        $url = $_.Groups[1].Value
        Write-Host "     - $url" -ForegroundColor Cyan
        
        # Verificar tipo de URL
        if ($url -match "googleapis\.com.*\.mp4") {
            Write-Host "       [CORRETO] URL final do video (googleapis)" -ForegroundColor Green
        } elseif ($url -match "sssrr\.org") {
            Write-Host "       [INTERMEDIARIO] URL de redirect (sssrr)" -ForegroundColor Yellow
        } elseif ($url -match "playerembedapi\.link") {
            Write-Host "       [INCORRETO] URL do player, nao do video" -ForegroundColor Red
        }
    }
} else {
    Write-Host "[ERRO] Nenhuma URL capturada" -ForegroundColor Red
    Write-Host "       Possivel causa: Timeout ou elemento nao encontrado" -ForegroundColor Yellow
}

# 5. Timeout?
if ($conteudo -match "timeout|Timeout") {
    Write-Host "[AVISO] Timeout detectado" -ForegroundColor Yellow
}

# 6. Erros?
$erros = $conteudo | Select-String -Pattern "ERROR|Error" -AllMatches
if ($erros) {
    Write-Host ""
    Write-Host "[ERROS ENCONTRADOS]" -ForegroundColor Red
    $erros | Select-Object -First 5 | ForEach-Object {
        Write-Host "  $($_.Line)" -ForegroundColor Red
    }
}

# Conclusão
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "CONCLUSAO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($capturedMatches -and $capturedMatches.Matches.Count -gt 0) {
    Write-Host "DIAGNOSTICO: URLs foram capturadas" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Problema provavel: Headers incorretos ou URL intermediaria" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Solucao: Adicionar headers corretos ao ExtractorLink" -ForegroundColor Green
    Write-Host "         ou seguir redirects da URL capturada" -ForegroundColor Green
} else {
    Write-Host "DIAGNOSTICO: Nenhuma URL capturada" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Problema provavel: Timeout ou elemento nao encontrado" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Solucao: Aumentar timeout de 30s para 45s" -ForegroundColor Green
    Write-Host "         ou melhorar selecao de elementos" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ARQUIVOS GERADOS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Logs completos: $arquivo" -ForegroundColor White
Write-Host "Logs filtrados: $arquivoFiltrado" -ForegroundColor White
Write-Host ""
Write-Host "Compartilhe o arquivo filtrado para analise detalhada." -ForegroundColor Yellow
