# Release v2.1.0 - PlayerEmbedAPI Ultra-Fast Implementation

## 🚀 Novidades

### PlayerEmbedAPI Extractor
- Extração ultra-rápida: **~200-300ms** (HTTP direto otimizado)
- Fallback WebView: ~10-15s quando necessário
- Regex pré-compiladas para máxima performance

### Suite Kali Linux (6 Ferramentas)
1. **kali_master_analyzer.py** - Análise completa automatizada
2. **kali_js_deobfuscator.py** - Deobfuscação JavaScript
3. **kali_mitm_proxy.py** - Proxy MITM para interceptação
4. **kali_param_fuzzer.py** - Fuzzing de parâmetros
5. **kali_request_manipulator.py** - Manipulação de requests
6. **kali_session_extractor.py** - Análise de sessões

### Arquivos Principais
- **MaxSeriesProvider_Final.kt** - Provider completo otimizado
- **PlayerEmbedAPIExtractor_Final.kt** - Extrator Kotlin para CloudStream

## 📊 Performance

```
HTTP Direto:    ~200-300 ms (99% dos casos)
WebView:        ~10-15 segundos (fallback)
Processamento:  <0.1 ms
Média:          257.58 ms
```

## 🔧 Otimizações
- ✅ Regex pré-compiladas (Pattern.compile)
- ✅ Keep-Alive connections
- ✅ SSL verification off
- ✅ Timeout agressivo (5s HTTP, 30s WebView)
- ✅ Sem parsing complexo (BeautifulSoup)
- ✅ Dispatchers.IO para operações de rede

## 📁 Estrutura de Arquivos

```
MaxSeriesProvider_Final.kt          (24.4 KB)
PlayerEmbedAPIExtractor_Final.kt    (10.3 KB)
kali_*.py                           (6 ferramentas)
*.md                                (10+ documentações)
```

## 📖 Documentação
- Ver arquivos `.md` na raiz do repositório
- **INTEGRACAO_MAXSERIES.md** - Guia de integração passo a passo
- **KALI_TOOLS_GUIDE.md** - Guia completo das ferramentas Kali

## 🎯 Como Usar

### No CloudStream:
1. Copiar `PlayerEmbedAPIExtractor_Final.kt` para `extractors/`
2. Integrar no `MaxSeriesProvider.kt`
3. Buildar: `./gradlew :MaxSeries:build`
4. Instalar `.cs3` gerado

### Ferramentas Python:
```bash
python kali_master_analyzer.py --url 'https://playerembedapi.link/?v=xxx'
```

---

**White Hat Security Research - 2026**
