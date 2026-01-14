# MaxSeries v78 - Correcao de Busca

## Problema Corrigido

A busca no CloudStream nao retornava resultados ao pesquisar series/filmes do MaxSeries.

### Causa
A pagina de busca do MaxSeries usa estrutura HTML diferente das paginas normais.

## Solucao Implementada

- Novo seletor para pagina de busca
- Nova funcao especifica para busca
- Fallback automatico
- Logs de debug melhorados

## Testes Realizados

Testadas 5 queries diferentes com 100% de sucesso:
- "gerente": 17 resultados
- "chapolin": 2 resultados
- "garota": 30 resultados
- "mil golpes": 4 resultados
- "breaking bad": 3 resultados

## Extractors Suportados (10 total)

1. PlayerEmbedAPI - MP4 direto (PRIORIDADE 1)
2. MyVidPlay - MP4 direto (PRIORIDADE 2)
3. StreamTape - MP4 direto (PRIORIDADE 3)
4. DoodStream - MP4/HLS (PRIORIDADE 4)
5. Mixdrop - MP4/HLS (PRIORIDADE 5)
6. FileMoon - MP4 (PRIORIDADE 6)
7. Uqload - MP4 (PRIORIDADE 7)
8. VidCloud - HLS (PRIORIDADE 8)
9. UpStream - MP4 (PRIORIDADE 9)
10. MegaEmbed - HLS ofuscado (PRIORIDADE 10)

## Como Instalar

1. Baixe o arquivo MaxSeries.cs3
2. No CloudStream, va em Configuracoes > Extensoes
3. Clique em + e selecione o arquivo baixado
4. Ative a extensao

## Como Usar a Busca

1. Abra a busca no CloudStream
2. Digite o nome da serie/filme
3. Os resultados aparecerao automaticamente

## Changelog v78

- Busca corrigida
- Nova funcao toSearchResultFromSearch()
- Fallback para seletor normal
- Logs de debug melhorados
- Documentacao completa adicionada

Data: 13 de Janeiro de 2026
Versao: v78
Status: Testado e Funcional
