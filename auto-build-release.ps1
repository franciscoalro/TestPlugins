# Auto Build and Release MaxSeries v156
# Tenta build a cada hora ate funcionar, depois cria release automaticamente

param(
    [int]$MaxAttempts = 24,  # Tentar por 24 horas
    [int]$IntervalMinutes = 60  # Intervalo de 1 hora
)

$ErrorActionPreference = "Continue"
$attempt = 1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  AUTO BUILD & RELEASE v156" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Configuracao:" -ForegroundColor Yellow
Write-Host "  Max tentativas: $MaxAttempts" -ForegroundColor White
Write-Host "  Intervalo: $IntervalMinutes minutos" -ForegroundColor White
Write-Host "  Tempo maximo: $($MaxAttempts * $IntervalMinutes / 60) horas" -ForegroundColor White
Write-Host ""

while ($attempt -le $MaxAttempts) {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$timestamp] Tentativa $attempt/$MaxAttempts" -ForegroundColor Cyan
    
    # FASE 1: Limpar builds anteriores
    Write-Host "  [1/5] Limpando builds anteriores..." -ForegroundColor Yellow
    ./gradlew.bat clean | Out-Null
    
    # FASE 2: Tentar build
    Write-Host "  [2/5] Tentando build..." -ForegroundColor Yellow
    $buildOutput = ./gradlew.bat MaxSeries:make 2>&1 | Out-String
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  OK BUILD FUNCIONOU!" -ForegroundColor Green
        
        # FASE 3: Verificar se .cs3 foi criado
        $cs3Path = "MaxSeries\build\MaxSeries.cs3"
        if (Test-Path $cs3Path) {
            Write-Host "  OK Arquivo .cs3 criado!" -ForegroundColor Green
            
            # FASE 4: Calcular SHA256
            Write-Host "  [3/5] Calculando SHA256..." -ForegroundColor Yellow
            $hash = (Get-FileHash $cs3Path -Algorithm SHA256).Hash
            Write-Host "  SHA256: $hash" -ForegroundColor White
            
            # FASE 5: Verificar tamanho
            $size = (Get-Item $cs3Path).Length
            $sizeKB = [math]::Round($size / 1KB, 2)
            Write-Host "  Tamanho: $sizeKB KB" -ForegroundColor White
            
            # FASE 6: Criar release no GitHub
            Write-Host "  [4/5] Criando release v156 no GitHub..." -ForegroundColor Yellow
            
            # Verificar se gh CLI está instalado
            $ghInstalled = Get-Command gh -ErrorAction SilentlyContinue
            
            if ($ghInstalled) {
                # Usar GitHub CLI
                $releaseNotes = Get-Content "RELEASE_NOTES_V162.md" -Raw
                gh release create v162 $cs3Path `
                    --title "MaxSeries v162 - Parser Fix" `
                    --notes "$releaseNotes"
                
                if ($LASTEXITCODE -eq 0) {
                    Write-Host "  OK Release criada com sucesso!" -ForegroundColor Green
                } else {
                    Write-Host "  AVISO Criar release manualmente em:" -ForegroundColor Yellow
                    Write-Host "  https://github.com/franciscoalro/TestPlugins/releases/new" -ForegroundColor Cyan
                }
            } else {
                Write-Host "  INFO GitHub CLI nao instalado" -ForegroundColor Yellow
                Write-Host "  Abrir navegador para criar release manual..." -ForegroundColor Yellow
                Start-Process "https://github.com/franciscoalro/TestPlugins/releases/new"
                Write-Host ""
                Write-Host "  INSTRUCOES:" -ForegroundColor Cyan
                Write-Host "  1. Tag version: v156" -ForegroundColor White
                Write-Host "  2. Title: MaxSeries v156 - MegaEmbed V8" -ForegroundColor White
                Write-Host "  3. Upload: MaxSeries\build\MaxSeries.cs3" -ForegroundColor White
                Write-Host "  4. Publish release" -ForegroundColor White
            }
            
            # FASE 7: Sucesso!
            Write-Host ""
            Write-Host "========================================" -ForegroundColor Green
            Write-Host "       SUCESSO TOTAL!" -ForegroundColor Green
            Write-Host "========================================" -ForegroundColor Green
            Write-Host ""
            Write-Host "Arquivo: $cs3Path" -ForegroundColor White
            Write-Host "Tamanho: $sizeKB KB" -ForegroundColor White
            Write-Host "SHA256: $hash" -ForegroundColor White
            Write-Host ""
            Write-Host "Proximo passo:" -ForegroundColor Cyan
            Write-Host "  Testar no CloudStream3!" -ForegroundColor White
            Write-Host ""
            
            # Salvar informacoes em arquivo
            @"
MaxSeries v156 Build Info
=========================
Data: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
Tentativa: $attempt
Arquivo: $cs3Path
Tamanho: $sizeKB KB
SHA256: $hash
"@ | Out-File "build_info_v156.txt"
            
            exit 0
            
        } else {
            Write-Host "  ERRO Arquivo .cs3 nao encontrado!" -ForegroundColor Red
        }
        
    } else {
        Write-Host "  FALHOU Build falhou (JitPack ainda instavel)" -ForegroundColor Red
        
        # Verificar se é erro de JitPack
        if ($buildOutput -match "jitpack|Could not find|Read timed out") {
            Write-Host "  Motivo: JitPack timeout/indisponivel" -ForegroundColor Yellow
        }
    }
    
    # Aguardar antes da proxima tentativa (exceto na ultima)
    if ($attempt -lt $MaxAttempts) {
        Write-Host ""
        Write-Host "  Aguardando $IntervalMinutes minutos ate proxima tentativa..." -ForegroundColor Gray
        Write-Host "  (Ctrl+C para cancelar)" -ForegroundColor Gray
        Write-Host ""
        
        Start-Sleep -Seconds ($IntervalMinutes * 60)
    }
    
    $attempt++
}

# Se chegou aqui, todas as tentativas falharam
Write-Host ""
Write-Host "========================================" -ForegroundColor Red
Write-Host "  TODAS AS TENTATIVAS FALHARAM" -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Red
Write-Host ""
Write-Host "Tentativas: $MaxAttempts" -ForegroundColor White
Write-Host "Tempo decorrido: $($MaxAttempts * $IntervalMinutes / 60) horas" -ForegroundColor White
Write-Host ""
Write-Host "Recomendacao:" -ForegroundColor Yellow
Write-Host "  1. Verificar status do JitPack: https://jitpack.io" -ForegroundColor White
Write-Host "  2. Tentar novamente mais tarde" -ForegroundColor White
Write-Host "  3. Ou usar biblioteca local (ver SOLUCAO_SEM_JITPACK.md)" -ForegroundColor White
Write-Host ""
exit 1
