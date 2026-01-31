# PlayerEmbedAPI Extractor v8 - Testing Guide

## 🎯 Objetivo

Validar que o PlayerEmbedAPIExtractorV8 funciona corretamente antes do deploy.

---

## 📋 Pré-requisitos

- [ ] Python 3.8+ instalado
- [ ] Dependências instaladas: `pip install requests beautifulsoup4`
- [ ] URLs reais de teste do playerembedapi.link

---

## 🧪 Fase 1: Teste Python (Protótipo)

### 1.1 Obter URL de Teste

```bash
# Método 1: Via ADB (se CloudStream já instalado)
adb logcat | grep "playerembedapi"

# Método 2: Via navegador
# 1. Abrir https://maxseries.pics
# 2. Escolher um episódio
# 3. Inspecionar elemento > Network
# 4. Procurar por "playerembedapi.link/?v=..."
```

### 1.2 Executar Extrator Python

```bash
cd tools

# Testar com ID real (substitua ABC123)
python playerembedapi_extractor.py ABC123

# Exemplo de output esperado:
# [1] Fetching: https://playerembedapi.link/?v=ABC123
# [2] HTML size: 45230 bytes
# [3] Trying Method 1: JWPlayer setup...
#   ✓ Found 'file': https://cloudatacdn.com/v4/xy/abc123/index.m3u8
# ✅ SUCCESS
# Video URL: https://cloudatacdn.com/v4/xy/abc123/index.m3u8
```

### 1.3 Validar URL Extraída

```bash
# Testar no VLC
vlc "https://cloudatacdn.com/..."

# Ou via curl (verificar se retorna M3U8)
curl -I "https://cloudatacdn.com/..." | grep "Content-Type"
# Esperado: Content-Type: application/vnd.apple.mpegurl
```

**Critério de Sucesso**: Vídeo reproduz no VLC ✅

---

## 🔨 Fase 2: Build do Plugin

### 2.1 Verificar Código Kotlin

```bash
cd MaxSeries

# Verificar se v8 foi criado
ls src/main/kotlin/com/franciscoalro/maxseries/extractors/PlayerEmbedAPIExtractorV8.kt

# Verificar import no Provider
grep "PlayerEmbedAPIExtractorV8" src/main/kotlin/com/franciscoalro/maxseries/MaxSeriesProvider.kt
```

### 2.2 Build Local

```bash
cd ..
.\gradlew.bat MaxSeries:make

# Esperado:
# BUILD SUCCESSFUL in Xs
# Artifact: MaxSeries/build/MaxSeries.cs3
```

**Se falhar com erro JitPack**: Usar GitHub Actions (ver seção 3).

---

## 🚀 Fase 3: Deploy via GitHub Actions

### 3.1 Commit e Push

```bash
git add .
git commit -m "feat: PlayerEmbedAPI v8 - Pure HTTP extractor"
git push origin main
```

### 3.2 Aguardar Build

```
1. Ir para: https://github.com/franciscoalro/cloudstream/actions
2. Aguardar workflow completar (~3-5 min)
3. Baixar artifact MaxSeries.cs3
```

---

## 📱 Fase 4: Teste no Dispositivo

### 4.1 Instalar Plugin

```bash
# Via ADB
adb push MaxSeries.cs3 /sdcard/Download/
# Abrir CloudStream > Settings > Extensions > Install from file

# Ou via URL (se já no repositório)
# CloudStream > Add Repository > https://franciscoalro.github.io/cloudstream/
```

### 4.2 Monitorar Logs

```bash
# Terminal 1: Logs em tempo real
adb logcat | grep -E "(PlayerEmbedAPI|MaxSeries)"

# Terminal 2: Filtrar apenas v8
adb logcat | grep "PlayerEmbedAPI-v8"
```

### 4.3 Testar Playback

**Passos**:
1. Abrir MaxSeries no CloudStream
2. Escolher um filme/série
3. Clicar em "Play"
4. Observar logs

**Logs Esperados (Sucesso v8)**:
```
PlayerEmbedAPI-v8: === PlayerEmbedAPI v8.0 - Pure HTTP Extraction ===
PlayerEmbedAPI-v8: 📄 HTML fetched in 234ms (45230 bytes)
PlayerEmbedAPI-v8: [Method 1] Trying JWPlayer setup extraction...
PlayerEmbedAPI-v8:   ✓ Found 'file': https://cloudatacdn.com/...
PlayerEmbedAPI-v8: ✅ SUCCESS via JWPlayer Setup
MaxSeriesProvider: ✅✅✅ PlayerEmbedAPI v8 (Pure): 1 links ✅✅✅
```

**Logs Esperados (Fallback v7)**:
```
PlayerEmbedAPI-v8: === PlayerEmbedAPI v8.0 - Pure HTTP Extraction ===
PlayerEmbedAPI-v8: ❌ All extraction methods failed
MaxSeriesProvider: ⚠️ v8 falhou, tentando v7 (WebView)...
PlayerEmbedAPI-v7: 🎯 URL CAPTURADA VIA CONSOLE: https://...
MaxSeriesProvider: ✅ PlayerEmbedAPI v7 (WebView Fallback): 1 links
```

---

## 📊 Fase 5: Análise de Performance

### 5.1 Comparar Tempos

**Criar planilha de testes**:

| Teste | v8 (Pure) | v7 (WebView) | Speedup |
|-------|-----------|--------------|---------|
| Filme 1 | 0.3s | 4.2s | 14x |
| Série 1 Ep1 | 0.4s | 5.1s | 12.7x |
| Série 1 Ep2 | 0.2s | 3.8s | 19x |

**Como medir**:
```bash
# Extrair tempo dos logs
adb logcat | grep "HTML fetched in"
# PlayerEmbedAPI-v8: 📄 HTML fetched in 234ms
```

### 5.2 Taxa de Sucesso

**Testar 20 episódios diferentes**:
```
v8 Sucesso: 17/20 (85%)
v7 Fallback: 3/20 (15%)
Total Sucesso: 20/20 (100%)
```

---

## ✅ Critérios de Aceitação

- [ ] Python prototype extrai URL com sucesso
- [ ] URL extraída reproduz no VLC
- [ ] Build do plugin completa sem erros
- [ ] v8 funciona em ≥70% dos casos
- [ ] v7 fallback funciona nos casos restantes
- [ ] Tempo médio de extração v8 < 1s
- [ ] Nenhum crash no CloudStream

---

## 🐛 Troubleshooting

### v8 sempre falha (0% sucesso)

**Diagnóstico**:
```bash
# Verificar HTML retornado
adb logcat | grep "HTML Preview"
```

**Possíveis causas**:
1. Site mudou estrutura HTML → Atualizar regex
2. Cloudflare bloqueando → Adicionar cookies de sessão
3. JWPlayer não está no HTML → Site migrou para outro player

**Solução**:
```bash
# Re-executar análise
python tools/deobfuscate_js.py https://playerembedapi.link
# Atualizar PlayerEmbedAPIExtractorV8.kt com novos padrões
```

### v8 funciona no Python mas falha no Kotlin

**Diagnóstico**:
```kotlin
// Adicionar debug em PlayerEmbedAPIExtractorV8.kt
Log.d(TAG, "HTML Preview: ${html.take(1000)}")
```

**Possíveis causas**:
1. Headers diferentes → Comparar com Python
2. Timeout muito curto → Aumentar timeout
3. Regex não compila → Testar regex isoladamente

### Build falha com "Unresolved reference: PlayerEmbedAPIExtractorV8"

**Solução**:
```bash
# Verificar package e nome do arquivo
# Arquivo: PlayerEmbedAPIExtractorV8.kt
# Package: com.franciscoalro.maxseries.extractors
# Class: class PlayerEmbedAPIExtractorV8 : ExtractorApi()

# Rebuild
.\gradlew.bat clean
.\gradlew.bat MaxSeries:make
```

---

## 📈 Próximos Passos

Após validação bem-sucedida:

1. [ ] Atualizar versão do plugin (v256)
2. [ ] Documentar mudanças no changelog
3. [ ] Criar PR com descrição detalhada
4. [ ] Monitorar issues de usuários
5. [ ] Considerar aplicar mesma técnica ao MegaEmbed

---

**Última atualização**: 31/01/2026  
**Versão**: 1.0
