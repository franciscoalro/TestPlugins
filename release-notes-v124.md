# Release Notes - v124

## 🔧 PlayerEmbedAPI - SSSRR.ORG CDN Fix

### Problema Identificado
Análise do Burp Suite revelou que o extrator estava procurando URLs erradas:
- ❌ **ERRADO**: `storage.googleapis.com` (não existe!)
- ✅ **CORRETO**: `sssrr.org` (CDN real)

### Descobertas da Análise Burp Suite
Arquivo analisado: `2026-01-18-162104_json_requests.json`
- Total de requisições: 1352
- Requisições PlayerEmbedAPI: 17
- URLs de vídeo encontradas: 44

**Padrões de URL identificados:**
1. `https://*.sssrr.org/sora/{video_id}/{base64_token}`
2. `https://*.sssrr.org/{path}/{hash}.{video_id}.{quality}.fd`
3. `https://*.sssrr.org/future`

**Scripts carregados:**
- `https://statics.sssrr.org/player/jwplayer.min.js`
- `https://statics.sssrr.org/player/jwpsrv.js`

### Correções Implementadas

#### 1. Regex Corrigido (PlayerEmbedAPIExtractor v3.3)
```kotlin
// ANTES (v123):
interceptUrl = Regex("""(?i)(?:storage\.googleapis\.com/mediastorage/.*\.mp4|.*\.m3u8|googlevideo|cloudatacdn|iamcdn|sssrr|valenium|/hls/.*|/video/.*|master\.txt)""")

// DEPOIS (v124):
interceptUrl = Regex("""(?i)sssrr\.org/(?:sora/|future|\d+/[a-f0-9])""")
```

#### 2. Validação de Vídeo Atualizada
Prioridades atualizadas:
1. ✅ `sssrr.org/sora/` (PRIORIDADE 1)
2. ✅ `sssrr.org/future` (PRIORIDADE 2)
3. ✅ `.sssrr.org/` + `.fd` (PRIORIDADE 3)

#### 3. Timeout Mantido
- ✅ 30 segundos (v123)
- ✅ Filtro .js mantido

### Exemplos de URLs Capturadas
```
https://gi7owxbf32.sssrr.org/sora/216875545/QWRtVDdIZzgyV3N3Um1hZ29NbmVIbXJkTm1nSHZvcEJydjRFc3J3eXhCSVpvODA
https://vdqv2f3va0.sssrr.org/5/3/d/cf862e0c71437afe3d1b6f99a693f.216700976.3.fd
https://twv10byhy49.sssrr.org/future
```

### Arquivos Modificados
- `MaxSeries/src/main/kotlin/com/franciscoalro/maxseries/extractors/PlayerEmbedAPIExtractor.kt` (v3.3)
- `MaxSeries/build.gradle.kts` (v124)

### Documentação
- `PLAYEREMBEDAPI_BURP_ANALYSIS_V123.md` - Análise completa do Burp Suite
- `burp_video_urls.txt` - 44 URLs de vídeo encontradas
- Scripts de análise: `find-video-urls.py`, `analyze-playerembedapi-flow.py`

### Teste Recomendado
```powershell
# 1. Build
.\build-quick.ps1

# 2. Instalar no dispositivo
adb install -r MaxSeries\build\MaxSeries.cs3

# 3. Monitorar logs
.\monitor-maxseries-v122.ps1
```

### Expectativa
Com o regex corrigido para `sssrr.org`, o WebView deve agora interceptar as URLs corretas do CDN e o vídeo deve reproduzir sem timeout.

---

**Data**: 18 de Janeiro de 2026  
**Versão**: 124  
**Tipo**: Bug Fix (Critical)  
**Componente**: PlayerEmbedAPIExtractor
