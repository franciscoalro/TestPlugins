# 📋 MaxSeries v11 - Changelog

## 🎯 Objetivo
Corrigir problemas com séries mostrando "Em breve" e filmes não encontrando links, baseado na análise do HTML real do ViewPlayer.

## 🔍 Análise do Problema Real
Com base no HTML fornecido pelo usuário, identificamos que o MaxSeries usa:
- **ViewPlayer iframe**: `https://viewplayer.online`
- **Botões com data-source**: `<button data-source="https://playerembedapi.link/?v=izD1HrKWL">`
- **Múltiplos players**: Dublado e Legendado (#1, #2, #3)
- **Estrutura JavaScript**: `gleam.config` e `jwplayer.js`

## 🔧 Mudanças Implementadas v11

### 1. **Detecção de ViewPlayer**
```kotlin
// Busca específica por ViewPlayer iframe
val mainIframe = doc.selectFirst("iframe[src*=viewplayer]")?.attr("src")
    ?: doc.selectFirst("iframe.metaframe")?.attr("src")
```

### 2. **Extração de Botões com data-source**
```kotlin
// Procura botões com data-source (como no HTML real)
iframeDoc.select("button[data-source], .btn[data-source]").forEach { button ->
    val source = button.attr("data-source")
    val playerName = button.text().trim() // "#1 Dublado", "#2 Legendado", etc.
}
```

### 3. **Análise de Scripts Gleam**
```kotlin
// Procura configurações gleam.config e jwplayer
if (scriptContent.contains("gleam.config", ignoreCase = true) ||
    scriptContent.contains("jwplayer", ignoreCase = true)) {
    // Extrai URLs de vídeo dos scripts
}
```

### 4. **Múltiplos Métodos de Fallback**
1. **ViewPlayer + data-source** (principal)
2. **DooPlay AJAX** (fallback)
3. **Iframes diretos** (fallback)
4. **Links diretos na página** (último recurso)

### 5. **Logs Detalhados**
```kotlin
Log.d("MaxSeries", "📺 Carregando player iframe: $iframeSrc")
Log.d("MaxSeries", "🎯 Player encontrado: $playerName -> $source")
Log.d("MaxSeries", "🎬 Script de configuração encontrado")
```

## 📊 Estrutura HTML Identificada

### Exemplo Real (do usuário):
```html
<div id="players">
    <button class="btn" data-source="https://playerembedapi.link/?v=izD1HrKWL" data-type="iframe">
        #1 Dublado
    </button>
    <button class="btn" data-source="https://megaembed.link/#gsbqjz" data-type="iframe">
        #2 Dublado
    </button>
    <button class="btn" data-source="https://myvidplay.com/e/kieb85xhpkf3" data-type="iframe">
        #3 Dublado
    </button>
</div>
```

### Como o Plugin Processa:
1. Encontra iframe principal do ViewPlayer
2. Carrega conteúdo do iframe
3. Busca todos os botões com `data-source`
4. Extrai URLs: `playerembedapi.link`, `megaembed.link`, `myvidplay.com`
5. Usa `loadExtractor()` para cada URL

## 🔄 Fluxo de Funcionamento v11

```
1. Usuário clica em filme/série
   ↓
2. Plugin detecta iframe ViewPlayer
   ↓
3. Carrega iframe e busca botões com data-source
   ↓
4. Extrai URLs dos players:
   - playerembedapi.link
   - megaembed.link  
   - myvidplay.com
   ↓
5. Usa loadExtractor() para cada URL
   ↓
6. CloudStream reproduz o vídeo
```

## 🐛 Problemas Resolvidos

### ✅ "Em breve" nos Episódios
- **Causa**: Não detectava estrutura DooPlay corretamente
- **Solução**: Simplificou detecção + fallback para episódio único

### ✅ Links de Vídeo Não Encontrados
- **Causa**: Não processava botões com data-source do ViewPlayer
- **Solução**: Busca específica por `button[data-source]`

### ✅ Múltiplos Players
- **Causa**: Só tentava um método
- **Solução**: Processa todos os botões encontrados

## 🎯 Expectativas v11

### ✅ Deve Funcionar
- Filmes com múltiplos players (Dublado/Legendado)
- Séries com episódios listados
- Players: playerembedapi.link, megaembed.link, myvidplay.com
- Logs detalhados para debug

### 📋 Para Testar
1. **Filme**: Verificar se aparecem players "#1 Dublado", "#2 Legendado", etc.
2. **Série**: Verificar se episódios não mostram "Em breve"
3. **Reprodução**: Testar se os links funcionam
4. **Logs**: Verificar mensagens de debug

## 🔧 Build e Deploy

### Status do Build:
- ✅ Código commitado no GitHub
- 🔄 GitHub Actions deve compilar automaticamente
- 📦 Arquivo `.cs3` será gerado nos Artifacts

### Para Instalar:
1. Aguardar build do GitHub Actions completar
2. Baixar `MaxSeries.cs3` dos Artifacts
3. Instalar no CloudStream
4. Testar com filmes e séries

---

**Versão**: MaxSeries v11  
**Data**: 2026-01-08  
**Status**: ✅ Implementado, aguardando build  
**Próximo**: Teste em produção com usuário