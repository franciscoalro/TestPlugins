# 🧪 GUIA DE TESTE - MaxSeries v80

**Data:** 14/01/2026  
**Objetivo:** Validar captura de `cf-master.txt` via WebView

---

## 🚀 QUICK START

### 1️⃣ Build do Plugin

```powershell
cd C:\Users\KYTHOURS\Desktop\cloudstream-pre-release
.\gradlew.bat :MaxSeries:assembleRelease
```

**Tempo estimado:** 2-3 minutos

---

### 2️⃣ Localizar o .aar

```powershell
# Caminho do arquivo compilado
MaxSeries\build\outputs\aar\MaxSeries-release.aar
```

---

### 3️⃣ Deploy no Android

**Opção A: Via ADB**
```powershell
adb push MaxSeries\build\outputs\aar\MaxSeries-release.aar /sdcard/Download/
```

**Opção B: Manual**
1. Copiar `.aar` para o dispositivo
2. Abrir Cloudstream Pre-Release
3. Settings → Extensions → Install from file
4. Selecionar `MaxSeries-release.aar`
5. Reiniciar app

---

### 4️⃣ Ativar Logs (ADB)

```powershell
# Limpar logs antigos
adb logcat -c

# Monitorar logs do MaxSeries
adb logcat | findstr /I "MegaEmbed MaxSeries"
```

**Linux/Mac:**
```bash
adb logcat | grep -E "MegaEmbed|MaxSeries"
```

---

### 5️⃣ Testar Episódio

1. Abrir **MaxSeries** no Cloudstream
2. Buscar série (ex: "Breaking Bad")
3. Selecionar episódio qualquer
4. Clicar em **Play**
5. Observar logs no terminal

---

## 📋 LOGS ESPERADOS

### ✅ Sucesso (Captura cf-master.txt)

```
D/MegaEmbedExtractor: === MegaEmbed Extractor v2 - WebView Implementation ===
D/MegaEmbedExtractor: 🎬 URL: https://megaembed.link/#3wnuij
D/MegaEmbedExtractor: 🔗 Referer: https://playerthree.online/episodio/12345
D/MegaEmbedExtractor: 🔄 Tentando método WebView com interceptação...
D/MegaEmbedExtractor: 🌐 Iniciando WebView com interceptação de rede...
D/MegaEmbedExtractor: 🔍 URL interceptada: https://spo3.marvellaholdings.sbs/v4/x6b/3wnuij/cf-master.1767386783.txt
D/MegaEmbedExtractor: ✅ URL de vídeo válida interceptada
D/MegaEmbedExtractor: 📺 Processando como HLS: https://spo3.marvellaholdings.sbs/v4/x6b/3wnuij/cf-master.1767386783.txt
D/MegaEmbedExtractor: ✅ ExtractorLink emitido com sucesso!
D/MegaEmbedExtractor: ✅ WebView interceptação funcionou!
```

**🎯 Indicadores de Sucesso:**
- ✅ `URL interceptada:` contém `cf-master.*.txt`
- ✅ `URL de vídeo válida interceptada`
- ✅ `Processando como HLS`
- ✅ `ExtractorLink emitido com sucesso`

---

### ⚠️ Fallback (JavaScript)

```
D/MegaEmbedExtractor: 🔄 Tentando método WebView com interceptação...
D/MegaEmbedExtractor: ⚠️ URL interceptada não é vídeo válido
D/MegaEmbedExtractor: 🔄 Tentando método WebView com JavaScript...
D/MegaEmbedExtractor: 📜 Iniciando WebView com JavaScript execution...
D/MegaEmbedExtractor: 📜 JS Result Raw: https://spo3.marvellaholdings.sbs/v4/x6b/3wnuij/cf-master.1767386783.txt
D/MegaEmbedExtractor: ✅ JavaScript capturou URL válida: https://spo3.marvellaholdings.sbs/v4/x6b/3wnuij/cf-master.1767386783.txt
D/MegaEmbedExtractor: ✅ WebView JavaScript funcionou!
```

**🎯 Indicadores:**
- ⚠️ Método 1 falhou (normal em alguns casos)
- ✅ Método 2 (JavaScript) funcionou
- ✅ URL capturada é válida

---

### ❌ Erro (Todos os métodos falharam)

```
D/MegaEmbedExtractor: 🔄 Tentando método WebView com interceptação...
D/MegaEmbedExtractor: ⚠️ URL interceptada não é vídeo válido
D/MegaEmbedExtractor: 🔄 Tentando método WebView com JavaScript...
D/MegaEmbedExtractor: ⚠️ JavaScript não capturou URL válida
D/MegaEmbedExtractor: 🔄 Tentando método HTTP direto...
D/MegaEmbedExtractor: ⚠️ HTTP direto falhou
D/MegaEmbedExtractor: ❌ Todos os métodos falharam para: https://megaembed.link/#3wnuij
```

**🔍 Possíveis Causas:**
- ❌ Site mudou estrutura
- ❌ Cloudflare bloqueou WebView
- ❌ URL inválida
- ❌ Timeout (aumentar de 45s para 60s)

---

## 🔍 VALIDAÇÃO DETALHADA

### 1️⃣ Verificar URL Interceptada

**Padrão Esperado:**
```
https://{subdomain}.marvellaholdings.sbs/v4/{hash1}/{hash2}/cf-master.{timestamp}.txt
```

**Exemplos Válidos:**
```
✅ https://spo3.marvellaholdings.sbs/v4/x6b/3wnuij/cf-master.1767386783.txt
✅ https://spo1.marvellaholdings.sbs/v4/abc/xyz123/cf-master.1767400000.txt
✅ https://cdn2.marvellaholdings.sbs/v4/def/456def/cf-master.1767500000.txt
```

**Exemplos Inválidos:**
```
❌ https://megaembed.link/client.js
❌ https://playerthree.online/assets/player.js
❌ https://cloudflare.com/analytics.js
```

---

### 2️⃣ Verificar Headers

**Logs Esperados:**
```
D/MegaEmbedExtractor: Headers enviados:
D/MegaEmbedExtractor:   User-Agent: Mozilla/5.0 (Linux; Android 10; SM-G975F)...
D/MegaEmbedExtractor:   Referer: https://megaembed.link
```

**✅ Correto:**
- `Referer` aponta para `megaembed.link` ou `playerthree.online`
- `User-Agent` é Android

**❌ Incorreto:**
- `Referer` vazio ou null
- `User-Agent` desktop

---

### 3️⃣ Verificar Processamento HLS

**Logs Esperados:**
```
D/MegaEmbedExtractor: 📺 Processando como HLS: https://spo3.marvellaholdings.sbs/v4/x6b/3wnuij/cf-master.1767386783.txt
I/M3u8Helper: Parsing HLS manifest: https://spo3.marvellaholdings.sbs/v4/x6b/3wnuij/cf-master.1767386783.txt
I/M3u8Helper: Found 4 quality levels: 360p, 480p, 720p, 1080p
D/MegaEmbedExtractor: ✅ ExtractorLink emitido com sucesso!
```

**✅ Indicadores:**
- `Processando como HLS` aparece
- `M3u8Helper` processa manifest
- Múltiplas qualidades encontradas
- `ExtractorLink emitido`

---

## 🧪 TESTES ESPECÍFICOS

### Teste 1: Captura de cf-master.txt

**Objetivo:** Confirmar que o regex captura o arquivo correto

**Passos:**
1. Escolher episódio com source `megaembed.link`
2. Clicar em Play
3. Verificar logs

**Resultado Esperado:**
```
🔍 URL interceptada: https://*.marvellaholdings.sbs/v4/*/*/cf-master.*.txt
```

**Status:** ✅ PASS / ❌ FAIL

---

### Teste 2: Headers Corretos

**Objetivo:** Confirmar que Referer está configurado

**Passos:**
1. Observar logs durante playback
2. Procurar por "Headers enviados"

**Resultado Esperado:**
```
Referer: https://megaembed.link
```

**Status:** ✅ PASS / ❌ FAIL

---

### Teste 3: Múltiplas Qualidades

**Objetivo:** Confirmar que HLS é processado corretamente

**Passos:**
1. Após captura de `cf-master.txt`
2. Verificar logs do `M3u8Helper`

**Resultado Esperado:**
```
Found 3+ quality levels
```

**Status:** ✅ PASS / ❌ FAIL

---

### Teste 4: Playback Real

**Objetivo:** Confirmar que vídeo reproduz sem erros

**Passos:**
1. Após ExtractorLink emitido
2. Verificar se vídeo inicia
3. Testar seek (avançar/retroceder)

**Resultado Esperado:**
- ✅ Vídeo inicia em < 5 segundos
- ✅ Seek funciona
- ✅ Áudio sincronizado
- ❌ Sem erro 3003

**Status:** ✅ PASS / ❌ FAIL

---

## 🐛 TROUBLESHOOTING

### Problema 1: "URL interceptada não é vídeo válido"

**Causa:** WebView capturou arquivo JS/CSS em vez de vídeo

**Solução:**
1. Verificar regex de interceptação (linha 102)
2. Adicionar mais padrões específicos
3. Aumentar timeout (linha 112)

**Código:**
```kotlin
// Linha 102-109
interceptUrl = Regex("""\\.m3u8|\\.mp4|master\\.txt|cf-master.*\\.txt|/hls/|/video/|/v4/.*\\.txt|cloudatacdn|sssrr\\.org"""),
```

---

### Problema 2: "Todos os métodos falharam"

**Causa:** Site mudou estrutura ou Cloudflare bloqueou

**Solução:**
1. Verificar se `megaembed.link` está acessível
2. Testar manualmente no navegador
3. Atualizar User-Agent (linha 33)
4. Verificar se Cloudflare mudou proteção

**Teste Manual:**
```powershell
curl -H "Referer: https://playerthree.online" https://megaembed.link/#3wnuij
```

---

### Problema 3: "Erro 3003" no playback

**Causa:** Formato de vídeo não suportado

**Solução:**
1. Verificar se URL é HLS (`.m3u8` ou `master.txt`)
2. Confirmar que `M3u8Helper` está sendo chamado
3. Testar URL diretamente no VLC

**Logs Esperados:**
```
📺 Processando como HLS: ...
```

---

### Problema 4: Timeout (45 segundos)

**Causa:** WebView demorou muito para carregar

**Solução:**
1. Aumentar timeout (linha 112)
2. Verificar conexão de internet
3. Testar em rede mais rápida

**Código:**
```kotlin
// Linha 112
timeout = 60_000L  // Aumentar de 45s para 60s
```

---

## 📊 CHECKLIST DE VALIDAÇÃO

### ✅ Build

- [ ] `gradlew.bat :MaxSeries:assembleRelease` executado
- [ ] `.aar` gerado em `build/outputs/aar/`
- [ ] Sem erros de compilação

### ✅ Deploy

- [ ] `.aar` copiado para dispositivo
- [ ] Plugin instalado no Cloudstream
- [ ] App reiniciado
- [ ] MaxSeries aparece na lista de providers

### ✅ Logs

- [ ] `adb logcat` conectado
- [ ] Filtro `MegaEmbed|MaxSeries` ativo
- [ ] Logs aparecem ao testar episódio

### ✅ Captura

- [ ] URL interceptada contém `cf-master.txt`
- [ ] URL contém `/v4/`
- [ ] URL contém `marvellaholdings.sbs` ou similar
- [ ] Referer configurado corretamente

### ✅ Playback

- [ ] Vídeo inicia sem erro
- [ ] Múltiplas qualidades disponíveis
- [ ] Seek funciona
- [ ] Áudio sincronizado
- [ ] Sem erro 3003

---

## 🎯 CRITÉRIOS DE SUCESSO

### ✅ Mínimo Aceitável

- [x] Build sem erros
- [x] Plugin instalado
- [x] Logs aparecem
- [x] URL interceptada é válida
- [x] Vídeo inicia

### ✅ Ideal

- [x] Todos os itens acima
- [x] Múltiplas qualidades (360p, 480p, 720p, 1080p)
- [x] Seek instantâneo
- [x] Sem buffering excessivo
- [x] Fallback funciona (se método 1 falhar)

---

## 📝 RELATÓRIO DE TESTE

### Template

```markdown
# Teste MaxSeries v80 - [DATA]

## Ambiente
- **Dispositivo:** [Android 10/11/12/13]
- **Cloudstream:** [Pre-Release / Stable]
- **Conexão:** [WiFi / 4G / 5G]

## Resultados

### Build
- Status: ✅ PASS / ❌ FAIL
- Tempo: [X minutos]
- Erros: [Nenhum / Listar]

### Deploy
- Status: ✅ PASS / ❌ FAIL
- Plugin visível: ✅ SIM / ❌ NÃO

### Captura
- URL interceptada: [URL completa]
- Contém cf-master.txt: ✅ SIM / ❌ NÃO
- Padrão /v4/: ✅ SIM / ❌ NÃO
- Referer correto: ✅ SIM / ❌ NÃO

### Playback
- Vídeo iniciou: ✅ SIM / ❌ NÃO
- Tempo para iniciar: [X segundos]
- Qualidades disponíveis: [360p, 480p, 720p, 1080p]
- Seek funciona: ✅ SIM / ❌ NÃO
- Erro 3003: ✅ NÃO / ❌ SIM

## Logs Relevantes
```
[Colar logs aqui]
```

## Conclusão
[SUCESSO / FALHA PARCIAL / FALHA TOTAL]

## Observações
[Notas adicionais]
```

---

## 🔄 PRÓXIMOS PASSOS (Após Teste)

### Se SUCESSO ✅

1. **Documentar versão funcional**
   - Commit com tag `v80-stable`
   - Atualizar README

2. **Deploy em produção**
   - Push para GitHub
   - GitHub Actions compila
   - Release automático

3. **Monitorar issues**
   - Verificar se usuários reportam problemas
   - Ajustar se necessário

---

### Se FALHA ❌

1. **Analisar logs**
   - Identificar ponto de falha
   - Verificar qual método falhou

2. **Ajustar código**
   - Atualizar regex se necessário
   - Aumentar timeout
   - Adicionar mais fallbacks

3. **Re-testar**
   - Build novamente
   - Deploy novamente
   - Validar correção

---

## 📚 REFERÊNCIAS

- **Análise Arquitetura:** `ANALISE-ARQUITETURA-PLAYER.md`
- **Status Implementação:** `STATUS-IMPLEMENTACAO.md`
- **Código Principal:** `MegaEmbedExtractor.kt`
- **Provider:** `MaxSeriesProvider.kt`

---

**✅ GUIA COMPLETO**  
**🧪 PRONTO PARA TESTE**  
**🚀 BOA SORTE!**

---

**Versão:** 1.0  
**Data:** 14/01/2026  
**Autor:** Guia de Teste MaxSeries
