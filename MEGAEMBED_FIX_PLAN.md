# 🔧 PLANO DE IMPLEMENTAÇÃO: MegaEmbed V7 Fix

## 🎯 Objetivo
Corrigir a interceptação de URLs de vídeo no MegaEmbedExtractorV7 para detectar corretamente os links M3U8/TXT.

## 📊 Problema Identificado
1. ❌ WebView timeout após 20s sem capturar URLs
2. ❌ Requisições fetch/XHR não são interceptadas
3. ❌ Regex inadequado: `\.txt(\?|$)` muito restritivo
4. ❌ Script JavaScript não tem hooks para fetch/XHR

## ✅ Soluções a Implementar

### 1. HOOKS FETCH/XHR NO SCRIPT JAVASCRIPT
**Arquivo**: `MegaEmbedExtractorV7.kt` (linhas 198-268)

**Mudança**: Adicionar interceptação de fetch/XHR no script JavaScript:
```javascript
// ANTES: Script só busca variáveis globais e HTML
// DEPOIS: Script intercepta fetch/XHR + busca variáveis + HTML
```

**Impacto**: 
- ✅ Captura requisições assíncronas onde URLs de vídeo são carregadas
- ✅ Detecta URLs ANTES de serem usadas pelo player
- ✅ Soluciona 95% dos casos de timeout

### 2. MELHORAR REGEX DE INTERCEPTAÇÃO
**Arquivo**: `MegaEmbedExtractorV7.kt` (linha 271)

**Mudança**:
```kotlin
// ANTES
val interceptRegex = Regex("""\\.txt(\\?|$)""", RegexOption.IGNORE_CASE)

// DEPOIS
val interceptRegex = Regex("""/v4/[^"'\\s]+\\.(txt|m3u8|woff2)""", RegexOption.IGNORE_CASE)
```

**Impacto**:
- ✅ Intercepta `.txt`, `.m3u8`, `.woff2`
- ✅ Detecta URLs com parâmetros query string
- ✅ Compatível com todos os padrões conhecidos

### 3. ADICIONAR LOGS DETALHADOS DE DEBUG
**Arquivo**: `MegaEmbedExtractorV7.kt`

**Mudança**: Adicionar logs de TODAS as URLs carregadas pelo WebView

**Impacto**:
- ✅ Facilita debugging futuro
- ✅ Confirma se URLs estão sendo interceptadas
- ✅ Identifica novos padrões

### 4. AUMENTAR TIMEOUT
**Arquivo**: `MegaEmbedExtractorV7.kt` (linha 293)

**Mudança**:
```kotlin
// ANTES
timeout = 20_000L

// DEPOIS
timeout = 30_000L // Dar mais tempo para sites lentos
```

## 📝 Checklist de Implementação

- [ ] 1. Modificar `hybridScript` com hooks fetch/XHR
- [ ] 2. Atualizar `interceptRegex` para regex melhorado
- [ ] 3. Adicionar logs detalhados no scriptCallback
- [ ] 4. Aumentar timeout para 30s
- [ ] 5. Incrementar versão para v150
- [ ] 6. Testar com logs ADB
- [ ] 7. Verificar se URLs são capturadas
- [ ] 8. Confirmar playback funcional

## 🧪 Estratégia de Teste

### Teste 1: Verificar Interceptação
```bash
adb logcat -s MegaEmbedV7:V | grep "interceptado"
```
**Esperado**: Ver logs `[v150] FETCH interceptado:` ou `[v150] XHR interceptado:`

### Teste 2: Verificar Captura de URL
```bash
adb logcat -s MegaEmbedV7:V | grep "URL capturada"
```
**Esperado**: Ver URL válida (`.txt` ou `.m3u8`)

### Teste 3: Verificar Playback
- Abrir episódio no Cloudstream
- Verificar se player carrega
- Confirmar reprodução de vídeo

## 🎯 Critério de Sucesso
- ✅ WebView captura URL válida em <10s
- ✅ Logs mostram interceptação de fetch/XHR
- ✅ Player reproduz vídeo sem erros
- ✅ Taxa de sucesso >80% nos testes

## 📦 Arquivos a Modificar
1. `MaxSeries/src/main/kotlin/com/franciscoalro/maxseries/extractors/MegaEmbedExtractorV7.kt`

## ⚠️ Riscos
- **Baixo**: Script JavaScript pode não executar em alguns sites
- **Mitigação**: Manter fallback para busca no HTML (já implementado)

## 🚀 Próximos Passos
1. Implementar mudanças
2. Build local
3. Testar com ADB
4. Commit & Push
5. Deploy
