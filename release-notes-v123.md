# MaxSeries v123 - PlayerEmbedAPI v3.2 (Timeout Fix)

## 🐛 Bug Fix Crítico

### Problema Identificado nos Logs ADB
```
Web-view timeout after 15s
Falha ao interceptar URL de vídeo. Final: https://playerembedapi.link/?v=kBJLtxCD3
```

**Causa**: Timeout de 15s era muito curto para o player carregar completamente.

### Solução Implementada
- ✅ **Timeout aumentado**: 15s → 30s
- ✅ **Regex melhorado**: Removido negative lookahead complexo
- ✅ **Filtro .js mantido**: Validação após captura (mais confiável)

## 🔧 Mudanças Técnicas

### PlayerEmbedAPIExtractor.kt v3.2

**Antes (v122)**:
```kotlin
timeout = 15_000L // 15s - Muito curto!
interceptUrl = Regex("""(?i)(?!.*\.js)(?:storage\.googleapis\.com/...)""") // Negative lookahead complexo
```

**Agora (v123)**:
```kotlin
timeout = 30_000L // 30s - Tempo suficiente para player carregar
interceptUrl = Regex("""(?i)(?:storage\.googleapis\.com/mediastorage/.*\.mp4|.*\.m3u8|...)""") // Mais simples e eficaz
```

### Validação .js Melhorada
```kotlin
// Filtro aplicado APÓS captura (mais confiável)
val isJsFile = captured.endsWith(".js") || 
               captured.contains(".js?") || 
               captured.contains("core.bundle") || 
               captured.contains("jwplayer")
```

## ✅ O Que Foi Corrigido

1. **Timeout insuficiente**
   - Player agora tem 30s para carregar
   - Reduz falhas por timeout prematuro

2. **Regex mais robusto**
   - Padrão simplificado sem negative lookahead
   - Melhor compatibilidade com diferentes URLs

3. **Filtro .js mantido**
   - Validação após interceptação
   - Mais confiável que regex complexo

## 📊 Logs Esperados Agora

**Antes (v122)**:
```
Web-view timeout after 15s ❌
Falha ao interceptar URL de vídeo
```

**Agora (v123)**:
```
Web-view timeout after 30s ⏱️
Captured: https://storage.googleapis.com/mediastorage/.../video.mp4 ✅
```

## 🧪 Como Testar

1. Atualizar para v123 no CloudStream
2. Buscar "Terra de Pecados"
3. Selecionar episódio
4. Clicar em PlayerEmbedAPI
5. **Aguardar até 30s** (antes falhava em 15s)
6. Verificar se vídeo carrega

## 🔄 Atualização Recomendada

**Urgência**: Crítica  
**Motivo**: Corrige timeout que impedia extração de vídeos

---

**Versão anterior**: v122 (JS Filter Fix)  
**Versão atual**: v123 (Timeout Fix 30s)  
**Próxima versão**: TBD
