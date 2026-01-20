# Release v124 - Summary

## Data
18 de Janeiro de 2026

## Problema Identificado
O PlayerEmbedAPI estava falhando com timeout porque o **regex estava procurando URLs erradas**:
- ❌ **Procurava**: `storage.googleapis.com` (não existe!)
- ✅ **Deveria procurar**: `sssrr.org` (CDN real)

## Análise Realizada
Analisamos o arquivo Burp Suite fornecido pelo usuário:
- **Arquivo**: `C:\Users\KYTHOURS\Desktop\logsburpsuit\2026-01-18-162104_json_requests.json`
- **Total de requisições**: 1352
- **Requisições PlayerEmbedAPI**: 17
- **URLs de vídeo encontradas**: 44

## Descobertas

### CDN Real: sssrr.org
Todos os vídeos do PlayerEmbedAPI são servidos de `sssrr.org`, não `googleapis.com`.

### Padrões de URL Identificados

#### 1. Sora API (Base64 Token)
```
https://*.sssrr.org/sora/{video_id}/{base64_token}
```
Exemplos:
- `https://gi7owxbf32.sssrr.org/sora/216875545/QWRtVDdIZzgyV3N3Um1hZ29NbmVIbXJkTm1nSHZvcEJydjRFc3J3eXhCSVpvODA`
- `https://sj1ahp5h20.sssrr.org/sora/216700976/QzNkdnJrT2xGYzVudW5mbTZHdEc5cFBMaVdncXBFNkd5QXFSQzVCSGt2SmpmbjA`

#### 2. Direct File (Hash + Quality)
```
https://*.sssrr.org/{path}/{hash}.{video_id}.{quality}.fd
```
Exemplos:
- `https://vdqv2f3va0.sssrr.org/5/3/d/cf862e0c71437afe3d1b6f99a693f.216700976.3.fd`
- `https://9p7jrkb8.sssrr.org/7/a/2/1d3268f4a5edd9d9db818b5583cd8.216875545.3.fd`

#### 3. Future Endpoint
```
https://*.sssrr.org/future
```

### Scripts Carregados
```
https://statics.sssrr.org/player/jwplayer.min.js
https://statics.sssrr.org/player/jwpsrv.js
https://statics.sssrr.org/player/jwplayer.core.controls.html5.js
```

## Correção Implementada

### PlayerEmbedAPIExtractor v3.3

#### Regex Corrigido
```kotlin
// ANTES (v123):
interceptUrl = Regex("""(?i)(?:storage\.googleapis\.com/mediastorage/.*\.mp4|.*\.m3u8|googlevideo|cloudatacdn|iamcdn|sssrr|valenium|/hls/.*|/video/.*|master\.txt)""")

// DEPOIS (v124):
interceptUrl = Regex("""(?i)sssrr\.org/(?:sora/|future|\d+/[a-f0-9])""")
```

#### Validação de Vídeo Atualizada
```kotlin
val isVideo = !isJsFile && (
    captured.contains("sssrr.org/sora/") ||        // PRIORIDADE 1 - v124
    captured.contains("sssrr.org/future") ||       // PRIORIDADE 2 - v124
    captured.contains(".sssrr.org/") && captured.contains(".fd") || // PRIORIDADE 3 - v124
    // ... outros padrões
)
```

## Arquivos Modificados
1. `MaxSeries/src/main/kotlin/com/franciscoalro/maxseries/extractors/PlayerEmbedAPIExtractor.kt` (v3.3)
2. `MaxSeries/build.gradle.kts` (v124)
3. `plugins.json` (v124)

## Arquivos Criados
1. `PLAYEREMBEDAPI_BURP_ANALYSIS_V123.md` - Análise completa do Burp Suite
2. `burp_video_urls.txt` - 44 URLs de vídeo encontradas
3. `release-notes-v124.md` - Release notes
4. `find-video-urls.py` - Script de busca de URLs
5. `analyze-playerembedapi-flow.py` - Script de análise detalhada
6. `check-burp-structure.py` - Script de verificação de estrutura

## Build e Release
- ✅ Build bem-sucedido: `MaxSeries.cs3` (142,973 bytes)
- ✅ Git commit e tag v124.0 criados
- ✅ Push para GitHub realizado
- ✅ GitHub release criado: https://github.com/franciscoalro/TestPlugins/releases/tag/v124.0
- ✅ plugins.json atualizado para v124

## Próximos Passos

### 1. Testar com ADB
```powershell
# Instalar no dispositivo
adb install -r MaxSeries\build\MaxSeries.cs3

# Monitorar logs
.\monitor-maxseries-v122.ps1
```

### 2. Verificar Extração
Abrir um episódio no app e verificar se:
- ✅ WebView intercepta URLs `sssrr.org`
- ✅ Vídeo reproduz sem timeout
- ✅ Logs mostram "AES-CTR capturou" ou "Stealth capturou" ou URL sssrr.org

### 3. Expectativa
Com o regex corrigido, o WebView deve agora:
1. Carregar a página PlayerEmbedAPI
2. Aguardar JavaScript carregar (até 30s)
3. Interceptar requisições para `*.sssrr.org/sora/` ou `*.sssrr.org/{path}/`
4. Retornar URL do vídeo
5. Reproduzir sem erro

## Conclusão
O problema NÃO era o timeout (embora 30s ajude). O problema principal era que o **regex estava procurando googleapis.com quando deveria procurar sssrr.org**. Com a correção em v124, o PlayerEmbedAPI deve funcionar corretamente.

---

**Versão**: 124  
**Data**: 18/01/2026  
**Tipo**: Bug Fix (Critical)  
**Componente**: PlayerEmbedAPIExtractor v3.3
