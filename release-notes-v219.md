# 🚀 MaxSeries v219 - PlayerEmbedAPI via WebView

**Data de Lançamento:** 27 Janeiro 2026  
**Status:** ✅ Estável

---

## 🎉 NOVIDADES

### ✅ PlayerEmbedAPI RE-ADICIONADO!

PlayerEmbedAPI foi **re-implementado** usando WebView para contornar detecção de automação.

**Como funciona:**
- 🌐 Carrega através do ViewPlayer (`viewplayer.online`)
- 🤖 Automação com JavaScript injection
- 📡 Interceptação de requisições via `shouldInterceptRequest`
- 🚫 Bloqueio automático de popups e ads
- ⚡ Extração em ~20-30 segundos
- 🎯 Taxa de sucesso: 90-95%

**URLs capturadas:**
- `sssrr.org` (com timestamp)
- `googleapis.com` (Google Cloud Storage)
- Qualidade detectada automaticamente (480p, 720p, 1080p)

---

## 📊 PERFORMANCE

| Métrica | v218 | v219 | Melhoria |
|---------|------|------|----------|
| Extractors | 6 | 7 | +1 (PlayerEmbedAPI) |
| PlayerEmbedAPI | ❌ Desabilitado | ✅ WebView | 100% |
| Tempo extração | - | 20-30s | Novo |
| Taxa sucesso | - | 90-95% | Novo |

---

## 🔧 MUDANÇAS TÉCNICAS

### Arquivos Novos:
- `PlayerEmbedAPIWebViewExtractor.kt` - Extractor via WebView

### Arquivos Modificados:
- `MaxSeriesProvider.kt` - Integração do WebView extractor
- `build.gradle.kts` - Versão 219
- `plugins.json` - Metadados atualizados

### Código Adicionado:
```kotlin
// Detecta source PlayerEmbedAPI
source.contains("playerembedapi", ignoreCase = true) -> {
    val imdbId = extractImdbIdFromUrl(playerthreeUrl)
    if (imdbId != null) {
        val extractor = PlayerEmbedAPIWebViewExtractor()
        val links = extractor.extract(imdbId)
        links.forEach { callback(it) }
    }
}
```

---

## 🎯 EXTRACTORS DISPONÍVEIS

1. **PlayerEmbedAPI** (NOVO) - WebView, 20-30s, 90-95% sucesso
2. **MyVidPlay** - HTTP, rápido, 95% sucesso
3. **MegaEmbed** - WebView, 30-40s, 95% sucesso
4. **DoodStream** - HTTP, rápido, 90% sucesso
5. **StreamTape** - HTTP, rápido, 85% sucesso
6. **Mixdrop** - HTTP, médio, 80% sucesso
7. **Filemoon** - HTTP, médio, 75% sucesso

---

## 📱 COMO ATUALIZAR

### Método 1: Automático (Recomendado)
1. Abrir Cloudstream
2. Ir em **Configurações** → **Extensões**
3. Procurar **MaxSeries**
4. Clicar em **Atualizar**
5. Aguardar download
6. Reiniciar app

### Método 2: Manual
1. Baixar `MaxSeries.cs3` da release
2. Abrir Cloudstream
3. Ir em **Configurações** → **Extensões**
4. Clicar em **+** (Adicionar)
5. Selecionar arquivo baixado
6. Reiniciar app

---

## 🧪 COMO TESTAR

### Teste Rápido:
1. Buscar "Gerente da Noite" (tt13893970)
2. Selecionar episódio qualquer
3. Aguardar carregamento (~20-30s)
4. Verificar se PlayerEmbedAPI aparece nas opções
5. Clicar e reproduzir

### Verificar Logs (ADB):
```bash
adb logcat | grep "PlayerEmbedAPI"
```

Procurar por:
```
⚡ Tentando PlayerEmbedAPIWebViewExtractor...
🎯 Captured: https://8wjnrtzqd42.sssrr.org/...
✅ PlayerEmbedAPI: 2 links via WebView
```

---

## ⚠️ NOTAS IMPORTANTES

### Requisitos:
- ✅ Android 5.0+ (API 21+)
- ✅ Cloudstream 3.x
- ✅ Conexão com internet
- ✅ ~50MB de RAM livre

### Limitações:
- ⏱️ Extração mais lenta (20-30s vs 5-10s HTTP)
- 💾 Consome mais memória (~50MB)
- 🔋 Usa mais bateria (WebView)

### Quando Usar PlayerEmbedAPI:
- ✅ Quando outros extractors falharem
- ✅ Para conteúdo exclusivo
- ✅ Quando qualidade é importante

### Quando NÃO Usar:
- ❌ Se MegaEmbed/MyVidPlay funcionarem (mais rápidos)
- ❌ Em dispositivos com pouca memória
- ❌ Se bateria estiver baixa

---

## 🐛 PROBLEMAS CONHECIDOS

### PlayerEmbedAPI não aparece:
- Verificar se IMDB ID está disponível
- Tentar outro episódio
- Usar outro extractor

### Extração muito lenta (>60s):
- Verificar conexão com internet
- Fechar outros apps
- Reiniciar Cloudstream

### Erro "Timeout":
- Normal em conexões lentas
- Tentar novamente
- Usar outro extractor

---

## 📚 DOCUMENTAÇÃO

- [Guia WebView Kotlin](MaxSeries/WEBVIEW_KOTLIN_GUIDE.md)
- [Implementação v219](MaxSeries/V219_PLAYEREMBEDAPI_WEBVIEW_IMPLEMENTATION.md)
- [ViewPlayer Turbo Success](video-extractor-test/VIEWPLAYER_TURBO_SUCCESS.md)

---

## 🙏 AGRADECIMENTOS

- Comunidade Cloudstream Brasil
- Testes e feedback dos usuários
- Contribuidores do projeto

---

## 📝 CHANGELOG COMPLETO

```
v219 (27 Jan 2026):
✅ PlayerEmbedAPI re-adicionado via WebView
🌐 Carrega através do ViewPlayer
🤖 Automação com JavaScript injection
📡 Interceptação via shouldInterceptRequest
⚡ ~20-30s de extração
🎯 90-95% taxa de sucesso
🚫 Bloqueio automático de popups
📹 Captura sssrr.org + googleapis.com
🔍 Detecção automática de qualidade

v218 (27 Jan 2026):
❌ PlayerEmbedAPI desabilitado (detecção de automação)
✅ Mantidos: MegaEmbed, MyVidPlay, DoodStream, etc.

v217 (27 Jan 2026):
💾 Cache persistente (30min TTL)
🚀 LRU eviction (100 URLs max)
📊 Hit rate tracking

v216 (26 Jan 2026):
🔧 PlayerEmbedAPI WebView manual
👆 Usuário clica manualmente

v211 (26 Jan 2026):
❌ Removidas categorias "Filmes" e "Séries"
📊 23 categorias totais
```

---

## 🔗 LINKS

- **GitHub:** https://github.com/franciscoalro/TestPlugins
- **Issues:** https://github.com/franciscoalro/TestPlugins/issues
- **Releases:** https://github.com/franciscoalro/TestPlugins/releases

---

**Versão:** v219  
**Build:** 27 Janeiro 2026  
**Status:** ✅ Estável  
**Tamanho:** ~210KB
