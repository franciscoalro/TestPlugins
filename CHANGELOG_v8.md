# Changelog - MaxSeries v8

## 🔧 Correções

### CloudStream v9.0 Compatibility
- **Corrigido**: Uso incorreto de `newExtractorLink` com parâmetros `referer` e `quality` como argumentos nomeados
- **Alterado**: Migrado para a nova sintaxe do CloudStream v9.0 onde `referer` e `quality` são definidos dentro de um bloco lambda

### Detalhes Técnicos

**Antes (v7 - Deprecated):**
```kotlin
newExtractorLink(
    source = playerName,
    name = playerName,
    url = streamUrl,
    referer = fixedLink,      // ❌ Erro de compilação
    quality = getQualityFromName(""),  // ❌ Erro de compilação
)
```

**Agora (v8 - CloudStream v9.0):**
```kotlin
newExtractorLink(
    playerName,
    playerName,
    streamUrl
) {
    this.referer = fixedLink           // ✅ Sintaxe correta
    this.quality = Qualities.Unknown.value  // ✅ Sintaxe correta
}
```

## 📦 Arquivos Atualizados
- `MaxSeries/src/main/kotlin/com/franciscoalro/maxseries/MaxSeriesProvider.kt`
- `MaxSeries/build.gradle.kts` (versão 7 → 8)
- `plugins.json` (atualizada descrição e versão)

## 🚀 Status
- ✅ Build passou com sucesso
- ✅ Compatível com CloudStream v9.0
- ✅ Pronto para distribuição

## 📋 Próximos Passos
1. Baixar arquivos .cs3 do GitHub Actions
2. Atualizar CloudstreamRepo com os novos plugins
3. Fazer push das atualizações no repositório de distribuição