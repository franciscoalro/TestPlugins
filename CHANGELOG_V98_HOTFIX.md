# MaxSeries v98 - Hotfix Release

**Data**: 16/01/2026  
**Tipo**: Hotfix  
**Prioridade**: Alta

---

## 🔥 Hotfix: abyss.to Support

### Problema Identificado
O domínio `playerembedapi.link` começou a redirecionar para `abyss.to`, um novo serviço de hospedagem de vídeos. Isso causava falha na extração porque o WebView não estava configurado para interceptar URLs desse domínio.

**Sintoma**:
```
MaxSeries-Extraction: Falha na extração
  ├─ Extractor: PlayerEmbedAPI
  ├─ Error: Falha ao interceptar URL de vídeo
```

### Solução Implementada

**Arquivo**: `PlayerEmbedAPIExtractor.kt`

**Mudanças**:
1. Adicionado `abyss\.to` ao regex de interceptação do WebView
2. Atualizado validação de URL capturada para aceitar `abyss.to`

**Antes**:
```kotlin
interceptUrl = Regex("""\\.mp4|\\.m3u8|storage\\.googleapis\\.com|googlevideo\\.com|cloudatacdn\\.com""")

if (captured.contains(".mp4") || captured.contains(".m3u8") || captured.contains("googleapis")) {
```

**Depois**:
```kotlin
// Intercepta MP4, M3U8, Google Cloud Storage E abyss.to (novo domínio)
interceptUrl = Regex("""\\.mp4|\\.m3u8|storage\\.googleapis\\.com|googlevideo\\.com|cloudatacdn\\.com|abyss\\.to""")

// Aceitar MP4, M3U8, googleapis OU abyss.to
if (captured.contains(".mp4") || captured.contains(".m3u8") || 
    captured.contains("googleapis") || captured.contains("abyss.to")) {
```

---

## ✅ Resultado Esperado

PlayerEmbedAPI agora deve:
1. Detectar redirecionamento para abyss.to
2. Interceptar corretamente URLs do domínio
3. Extrair vídeos com sucesso

---

## 📦 Build

```
BUILD SUCCESSFUL in 19s
8 actionable tasks: 8 up-to-date
```

**Arquivo gerado**: `MaxSeries.cs3` (v98)

---

## 🚀 Deploy

### Quick Deploy
```powershell
# Copiar artifact
Copy-Item "MaxSeries\build\MaxSeries.cs3" -Destination "." -Force

# Atualizar plugins.json
# version: 98
# description: "MaxSeries v98 - Hotfix: abyss.to support"

# Commit e push
git add .
git commit -m "v98: Hotfix - Add abyss.to support to PlayerEmbedAPI"
git push origin main
```

---

## 🧪 Validação

### Teste no ADB
1. Reproduzir episódio com PlayerEmbedAPI
2. Verificar logs:
```
MaxSeries-Extraction: Extração bem-sucedida
  ├─ Extractor: PlayerEmbedAPI
  ├─ VideoURL: https://...abyss.to...
  ├─ Quality: ...
```

### Resultado Esperado
✅ Extração bem-sucedida com URL contendo `abyss.to`

---

## 📊 Impacto

**Severidade**: Alta  
**Extractors Afetados**: PlayerEmbedAPI  
**Usuários Impactados**: Todos que usam PlayerEmbedAPI  
**Tempo de Fix**: ~10 minutos  

---

## 🔄 Compatibilidade

✅ Mantém todas otimizações v97:
- Cache
- Retry
- Quality Detection
- Error Logging

✅ Sem breaking changes

---

## 📝 Notas

- Este é um hotfix crítico para PlayerEmbedAPI
- Não afeta outros extractors
- Todas as otimizações v97 permanecem ativas
- Recomenda-se atualização imediata

---

**Versão**: v98  
**Tipo**: Hotfix  
**Status**: ✅ Pronto para deploy
