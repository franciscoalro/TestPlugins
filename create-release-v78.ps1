# MaxSeries v78 - Create GitHub Release

Write-Host "MaxSeries v78 - Criando Release no GitHub..." -ForegroundColor Cyan

# Verificar se gh CLI esta instalado
$ghInstalled = Get-Command gh -ErrorAction SilentlyContinue
if (-not $ghInstalled) {
    Write-Host "ERRO: GitHub CLI (gh) nao encontrado!" -ForegroundColor Red
    Write-Host "Instale: https://cli.github.com/" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Alternativa: Criar release manualmente em:" -ForegroundColor Yellow
    Write-Host "https://github.com/franciscoalro/TestPlugins/releases/new?tag=v78.0" -ForegroundColor White
    exit 1
}

# Verificar se o arquivo existe
if (-not (Test-Path "MaxSeries.cs3")) {
    Write-Host "ERRO: MaxSeries.cs3 nao encontrado!" -ForegroundColor Red
    exit 1
}

# Release notes
$releaseNotes = @"
# MaxSeries v78 - Correcao de Busca

## Problema Corrigido

A busca no CloudStream **nao retornava resultados** ao pesquisar series/filmes do MaxSeries.

### Causa
A pagina de busca do MaxSeries usa estrutura HTML diferente:
- Paginas normais: ``<article class="item">``
- Pagina de busca: ``<div class="result-item"><article>``

O provider v77 so procurava por ``article.item``, entao nao encontrava nada na busca.

## Solucao Implementada

- Novo seletor: ``.result-item article`` para pagina de busca
- Nova funcao: ``toSearchResultFromSearch()`` especifica para busca
- Fallback: Se nao encontrar, tenta seletor normal
- Logs: Debug melhorado para rastrear problemas

## Testes Realizados

Testadas 5 queries diferentes com **100% de sucesso**:

| Query | Resultados | Status |
|-------|------------|--------|
| "gerente" | 17 | OK |
| "chapolin" | 2 | OK |
| "garota" | 30 | OK |
| "mil golpes" | 4 | OK |
| "breaking bad" | 3 | OK |

## Extractors Suportados (10 total)

1. **PlayerEmbedAPI** - MP4 direto (PRIORIDADE 1)
2. **MyVidPlay** - MP4 direto (PRIORIDADE 2)
3. **StreamTape** - MP4 direto (PRIORIDADE 3)
4. **DoodStream** - MP4/HLS (PRIORIDADE 4)
5. **Mixdrop** - MP4/HLS (PRIORIDADE 5)
6. **FileMoon** - MP4 (PRIORIDADE 6)
7. **Uqload** - MP4 (PRIORIDADE 7)
8. **VidCloud** - HLS (PRIORIDADE 8)
9. **UpStream** - MP4 (PRIORIDADE 9)
10. **MegaEmbed** - HLS ofuscado (PRIORIDADE 10)

## Como Instalar

1. Baixe o arquivo ``MaxSeries.cs3``
2. No CloudStream, va em **Configuracoes > Extensoes**
3. Clique em **+** e selecione o arquivo baixado
4. Ative a extensao

## Como Usar a Busca

1. Abra a busca no CloudStream
2. Digite o nome da serie/filme (ex: "gerente", "chapolin")
3. Os resultados aparecerao automaticamente

## Changelog v78

- Busca corrigida: suporte a ``.result-item``
- Nova funcao ``toSearchResultFromSearch()``
- Fallback para seletor normal
- Logs de debug melhorados
- Documentacao completa adicionada

## Documentacao

- [MAXSERIES_V78_SEARCH_FIX.md](https://github.com/franciscoalro/TestPlugins/blob/main/MAXSERIES_V78_SEARCH_FIX.md) - Detalhes da correcao
- [ANALISE_PROFUNDA_MAXSERIES.md](https://github.com/franciscoalro/TestPlugins/blob/main/ANALISE_PROFUNDA_MAXSERIES.md) - Analise de 5 series

---

**Data**: 13 de Janeiro de 2026  
**Versao**: v78  
**Status**: Testado e Funcional
"@

# Criar release
Write-Host ""
Write-Host "Criando release v78.0..." -ForegroundColor Yellow

gh release create v78.0 `
    --title "MaxSeries v78 - Correcao de Busca" `
    --notes $releaseNotes `
    MaxSeries.cs3

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "SUCESSO! Release v78.0 criada!" -ForegroundColor Green
    Write-Host ""
    Write-Host "URL da release:" -ForegroundColor Cyan
    Write-Host "https://github.com/franciscoalro/TestPlugins/releases/tag/v78.0" -ForegroundColor White
    Write-Host ""
    Write-Host "Arquivo disponivel em:" -ForegroundColor Cyan
    Write-Host "https://github.com/franciscoalro/TestPlugins/releases/download/v78.0/MaxSeries.cs3" -ForegroundColor White
} else {
    Write-Host ""
    Write-Host "ERRO ao criar release!" -ForegroundColor Red
    Write-Host "Crie manualmente em:" -ForegroundColor Yellow
    Write-Host "https://github.com/franciscoalro/TestPlugins/releases/new?tag=v78.0" -ForegroundColor White
}
