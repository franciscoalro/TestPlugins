# PlayerEmbedAPI Burp Suite Analysis - v123

## Data da Análise
18 de Janeiro de 2026

## Arquivo Analisado
`C:\Users\KYTHOURS\Desktop\logsburpsuit\2026-01-18-162104_json_requests.json`
- Total de requisições: 1352
- Requisições PlayerEmbedAPI: 17
- URLs de vídeo encontradas: 44

## Descobertas Principais

### 1. CDN Real: sssrr.org (NÃO googleapis.com!)
O extrator atual está procurando por `storage.googleapis.com`, mas o PlayerEmbedAPI usa **sssrr.org**:

```
❌ ERRADO (regex atual): storage\.googleapis\.com/mediastorage/.*\.mp4
✅ CORRETO: sssrr\.org
```

### 2. Padrões de URL Identificados

#### Padrão 1: Sora API (Base64 Token)
```
https://*.sssrr.org/sora/{video_id}/{base64_token}
```

Exemplos:
- `https://gi7owxbf32.sssrr.org/sora/216875545/QWRtVDdIZzgyV3N3Um1hZ29NbmVIbXJkTm1nSHZvcEJydjRFc3J3eXhCSVpvODA`
- `https://sj1ahp5h20.sssrr.org/sora/216700976/QzNkdnJrT2xGYzVudW5mbTZHdEc5cFBMaVdncXBFNkd5QXFSQzVCSGt2SmpmbjA`
- `https://twv10byhy49.sssrr.org/sora/239709738/cFk3VlB3VzIrckpEUjgwM2NPQ0Yva1UwNVBUN1YzczlrZTRTQmF5TjBHT011NkM`

#### Padrão 2: Direct File (Hash + Quality)
```
https://*.sssrr.org/{path}/{hash}.{video_id}.{quality}.fd
```

Exemplos:
- `https://vdqv2f3va0.sssrr.org/5/3/d/cf862e0c71437afe3d1b6f99a693f.216700976.3.fd`
- `https://9p7jrkb8.sssrr.org/7/a/2/1d3268f4a5edd9d9db818b5583cd8.216875545.3.fd`
- `https://zgok4xuuu17.sssrr.org/6/3/f/30c68cbbf6e38be8c315a8851c450.239709738.3.fd`

#### Padrão 3: Future Endpoint
```
https://*.sssrr.org/future
```

### 3. Scripts Carregados
Todos os players carregam scripts de:
```
https://statics.sssrr.org/player/jwplayer.min.js
https://statics.sssrr.org/player/jwpsrv.js
https://statics.sssrr.org/player/jwplayer.core.controls.html5.js
```

### 4. Fluxo de Carregamento
1. GET `https://playerembedapi.link/?v={video_id}` → HTML com player
2. HTML carrega scripts JWPlayer de `statics.sssrr.org`
3. JavaScript faz requisições para `*.sssrr.org/sora/` ou `*.sssrr.org/{path}/`
4. Vídeo é servido do CDN sssrr.org

### 5. Problema do Timeout
O ADB log mostrou:
```
Falha ao interceptar URL de vídeo. Final: https://playerembedapi.link/?v=kBJLtxCD3
```

**Causa**: O WebView está parando na página inicial, não esperando o JavaScript carregar e fazer as requisições para sssrr.org.

## Solução Proposta - v124

### 1. Atualizar Regex do WebView
```kotlin
// ANTES (v123):
interceptUrl = Regex("""(?i)(?:storage\.googleapis\.com/mediastorage/.*\.mp4|.*\.m3u8|googlevideo|cloudatacdn|iamcdn|sssrr|valenium|/hls/.*|/video/.*|master\.txt)""")

// DEPOIS (v124):
interceptUrl = Regex("""(?i)sssrr\.org/(?:sora/|future|\d+/[a-f0-9]+/)""")
```

### 2. Aumentar Timeout (já feito em v123)
✅ Timeout já aumentado de 15s → 30s

### 3. Melhorar Script de Captura
O script atual já tenta forçar play, mas pode precisar esperar mais tempo para o JWPlayer carregar.

## Regex Recomendado

### Opção 1: Específico (Recomendado)
```kotlin
Regex("""(?i)sssrr\.org/(?:sora/\d+/[A-Za-z0-9+/=]+|future|\d+/[a-f0-9]/[a-f0-9]/[a-f0-9]/[a-f0-9]+\.\d+\.\d+\.fd)""")
```

### Opção 2: Simples (Mais Abrangente)
```kotlin
Regex("""(?i)sssrr\.org/(?:sora/|future|\d+/)""")
```

### Opção 3: Muito Simples (Captura Tudo)
```kotlin
Regex("""(?i)sssrr\.org/""")
```

## Próximos Passos

1. ✅ Análise Burp Suite completa
2. ⏳ Atualizar regex para sssrr.org (v124)
3. ⏳ Testar com ADB monitoring
4. ⏳ Verificar se timeout de 30s é suficiente
5. ⏳ Release v124

## Arquivos Gerados
- `burp_video_urls.txt` - Todas as 44 URLs de vídeo encontradas
- `analyze-playerembedapi-flow.py` - Script de análise detalhada
- `find-video-urls.py` - Script de busca de URLs

## Conclusão
O problema NÃO é o timeout (embora 30s ajude). O problema principal é que o **regex está procurando googleapis.com quando deveria procurar sssrr.org**.
