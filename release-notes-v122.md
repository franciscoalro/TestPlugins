# MaxSeries v122 - PlayerEmbedAPI v3.1 (JS Filter Fix)

## 🐛 Bug Fix Crítico

### Problema Resolvido
- ❌ **Antes**: Player tentava reproduzir `core.bundle.js` e outros arquivos JavaScript
- ✅ **Agora**: Filtro ignora completamente arquivos `.js`

## 🔧 Mudanças Técnicas

### PlayerEmbedAPIExtractor.kt v3.1
```kotlin
// Filtro .js adicionado no regex de interceptação
interceptUrl = Regex("""(?i)(?!.*\.js)(?:storage\.googleapis\.com/...)""")

// Validação adicional antes de processar URL
val isJsFile = captured.endsWith(".js") || 
               captured.contains(".js?") || 
               captured.contains("core.bundle") || 
               captured.contains("jwplayer")
```

### Arquivos Ignorados
- `core.bundle.js`
- `jwplayer.js`
- Qualquer arquivo terminando em `.js`
- URLs contendo `.js?` (com query params)

## ✅ O Que Funciona Agora

1. **Apenas vídeos reais são interceptados**
   - MP4 do Google Cloud Storage
   - M3U8 playlists
   - URLs de CDNs válidos

2. **JavaScript é completamente ignorado**
   - Não aparece mais no player
   - Não causa erros de reprodução
   - Não desperdiça tentativas de loading

## 🧪 Como Testar

1. Atualizar para v122 no CloudStream
2. Buscar "Terra de Pecados"
3. Selecionar episódio
4. Clicar em PlayerEmbedAPI
5. **Verificar**: Não deve aparecer `core.bundle.js` no player

## 📊 Compatibilidade

- Mantém todas as melhorias da v121
- Google Cloud Storage prioritário
- Timeout otimizado (15s)
- Cache de URLs (5min)
- Retry logic (2 tentativas)

## 🔄 Atualização Recomendada

**Urgência**: Alta  
**Motivo**: Corrige bug que impedia reprodução em alguns casos

---

**Versão anterior**: v121 (PlayerEmbedAPI v3 Playwright Optimized)  
**Versão atual**: v122 (JS Filter Fix)  
**Próxima versão**: TBD
