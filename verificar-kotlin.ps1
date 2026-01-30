# Verificador de Código Kotlin para CloudStream
# Executa verificações antes do build

param(
    [string]$ExtractorFile = "",
    [switch]$VerificarTodos = $false
)

Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  VERIFICADOR DE CÓDIGO KOTLIN - CloudStream Extractors" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan

$Erros = 0
$Avisos = 0

function Verificar-Arquivo {
    param([string]$Arquivo)
    
    Write-Host "`n📄 Verificando: $Arquivo" -ForegroundColor Yellow
    
    if (-not (Test-Path $Arquivo)) {
        Write-Host "   ❌ Arquivo não encontrado!" -ForegroundColor Red
        return
    }
    
    $Conteudo = Get-Content $Arquivo -Raw
    $NomeArquivo = Split-Path $Arquivo -Leaf
    
    # Verificações CRÍTICAS (erros que impedem build)
    $VerificacoesCriticas = @(
        @{
            Padrao = 'ExtractorLink\s*\('
            Descricao = "Uso antigo de ExtractorLink() - deve usar newExtractorLink()"
            Correcao = "Use: newExtractorLink(source, name, url, type) { }"
            Critico = $true
        },
        @{
            Padrao = 'callback\s*\(\s*ExtractorLink'
            Descricao = "Callback com ExtractorLink antigo"
            Correcao = "Use: callback.invoke(newExtractorLink(...) { })"
            Critico = $true
        },
        @{
            Padrao = 'override\s+val\s+name\s*=\s*"[^"]*"\s*$'
            Descricao = "Falta 'var' ou declaração incorreta de 'name'"
            Correcao = "Use: override var name = \"Nome\""
            Critico = $true
        },
        @{
            Padrao = 'override\s+val\s+mainUrl'
            Descricao = "mainUrl deve ser 'var' não 'val'"
            Correcao = "Use: override var mainUrl = \"...\""
            Critico = $true
        },
        @{
            Padrao = 'import\s+com\.lagradost\.cloudstream3\.ExtractorLink(?!Type)'
            Descricao = "Import incorreto de ExtractorLink"
            Correcao = "Não importe ExtractorLink diretamente, use newExtractorLink()"
            Critico = $false
        }
    )
    
    # Verificações de BOAS PRÁTICAS
    $VerificacoesBoasPraticas = @(
        @{
            Padrao = 'Log\.d\s*\(\s*"[^"]*"\s*,\s*"'
            Descricao = "Uso de Log.d encontrado - ótimo para debugging"
            Tipo = "Info"
        },
        @{
            Padrao = 'VideoUrlCache\.(put|get)'
            Descricao = "Cache de URLs implementado - bom para performance"
            Tipo = "Info"
        },
        @{
            Padrao = 'runCatching\s*\{'
            Descricao = "Tratamento de erros com runCatching - boa prática!"
            Tipo = "Info"
        },
        @{
            Padrao = 'app\.get\s*\([^)]+\)\s*\.text'
            Descricao = "Chamada HTTP direta - considere adicionar timeout"
            Sugestao = "Adicione: timeout = 15 (segundos)"
            Tipo = "Aviso"
        },
        @{
            Padrao = 'Regex\s*\(\s*"""'
            Descricao = "Regex com raw string (""") - boa prática para escaping"
            Tipo = "Info"
        }
    )
    
    # Verificar problemas críticos
    Write-Host "   🔍 Verificando erros críticos..." -ForegroundColor Gray
    foreach ($Check in $VerificacoesCriticas) {
        if ($Conteudo -match $Check.Padrao) {
            Write-Host "   ❌ ERRO: $($Check.Descricao)" -ForegroundColor Red
            Write-Host "      💡 Correção: $($Check.Correcao)" -ForegroundColor Cyan
            $script:Erros++
        }
    }
    
    # Verificar boas práticas
    Write-Host "   🔍 Verificando boas práticas..." -ForegroundColor Gray
    foreach ($Check in $VerificacoesBoasPraticas) {
        if ($Conteudo -match $Check.Padrao) {
            $Cor = if ($Check.Tipo -eq "Info") { "Green" } else { "Yellow" }
            Write-Host "   $($Check.Tipo -eq 'Info' ? '✅' : '⚠️') $($Check.Descricao)" -ForegroundColor $Cor
            if ($Check.Sugestao) {
                Write-Host "      💡 $($Check.Sugestao)" -ForegroundColor Cyan
            }
            if ($Check.Tipo -eq "Aviso") { $script:Avisos++ }
        }
    }
    
    # Verificações específicas de estrutura
    Write-Host "   🔍 Verificando estrutura da classe..." -ForegroundColor Gray
    
    # Verificar se estende ExtractorApi
    if ($Conteudo -match 'class\s+\w+\s*:\s*ExtractorApi\s*\(\)') {
        Write-Host "   ✅ Estende ExtractorApi corretamente" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️ Verificar: classe deve estender ExtractorApi()" -ForegroundColor Yellow
        $script:Avisos++
    }
    
    # Verificar método getUrl
    if ($Conteudo -match 'override\s+suspend\s+fun\s+getUrl\s*\(') {
        Write-Host "   ✅ Método getUrl declarado corretamente (suspend)" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Método getUrl deve ser 'override suspend fun'" -ForegroundColor Red
        $script:Erros++
    }
    
    # Verificar parâmetros do getUrl
    $ParametrosEsperados = @('url', 'referer', 'subtitleCallback', 'callback')
    $ParametrosOk = $true
    foreach ($Param in $ParametrosEsperados) {
        if ($Conteudo -notmatch "getUrl\s*\([^)]*$Param") {
            Write-Host "   ❌ Parâmetro '$Param' não encontrado em getUrl" -ForegroundColor Red
            $ParametrosOk = $false
            $script:Erros++
        }
    }
    if ($ParametrosOk) {
        Write-Host "   ✅ Parâmetros de getUrl corretos" -ForegroundColor Green
    }
    
    # Verificar uso de callback
    $MatchesCallback = [regex]::Matches($Conteudo, 'callback\.invoke\s*\(')
    if ($MatchesCallback.Count -gt 0) {
        Write-Host "   ✅ callback.invoke encontrado ($($MatchesCallback.Count) ocorrências)" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️ Nenhum callback.invoke encontrado - extractor não retornará links" -ForegroundColor Yellow
        $script:Avisos++
    }
}

# Executar verificações
if ($VerificarTodos) {
    Write-Host "`n📁 Modo: Verificando TODOS os extractors..." -ForegroundColor Yellow
    
    $Extractors = Get-ChildItem -Path "MaxSeries\src\main\kotlin\com\franciscoalro\maxseries\extractors" -Filter "*.kt" -Recurse
    
    foreach ($Extractor in $Extractors) {
        Verificar-Arquivo -Arquivo $Extractor.FullName
    }
} elseif ($ExtractorFile) {
    Verificar-Arquivo -Arquivo $ExtractorFile
} else {
    # Verificar o mais recente
    $MaisRecente = Get-ChildItem -Path "MaxSeries\src\main\kotlin\com\franciscoalro\maxseries\extractors" -Filter "*.kt" | 
                   Sort-Object LastWriteTime -Descending | 
                   Select-Object -First 1
    
    if ($MaisRecente) {
        Verificar-Arquivo -Arquivo $MaisRecente.FullName
    }
}

# Relatório final
Write-Host "`n═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  RELATÓRIO FINAL" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan

if ($Erros -eq 0 -and $Avisos -eq 0) {
    Write-Host "`n   ✅ CÓDIGO PRONTO PARA BUILD!" -ForegroundColor Green
} else {
    Write-Host "`n   ❌ Erros encontrados: $Erros" -ForegroundColor Red
    Write-Host "   ⚠️ Avisos: $Avisos" -ForegroundColor Yellow
    
    if ($Erros -gt 0) {
        Write-Host "`n   🛑 CORRIJA OS ERROS ANTES DO BUILD!" -ForegroundColor Red
    } else {
        Write-Host "`n   ✅ Código pode ser buildado, mas atenção aos avisos" -ForegroundColor Yellow
    }
}

Write-Host "`n" -ForegroundColor Cyan
