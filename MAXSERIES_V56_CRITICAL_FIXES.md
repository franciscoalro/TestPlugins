# MaxSeries v56 - Critical AnimesOnlineCC Fixes

## 🎯 OBJETIVO
Resolver o problema de **conteúdo não aparecer no CloudStream app** aplicando correções críticas baseadas no provider AnimesOnlineCC que está funcionando.

## 🔧 CORREÇÕES CRÍTICAS APLICADAS

### 1. **Tratamento de Erro Robusto**
- ✅ Adicionado `try/catch` em todas as funções principais
- ✅ Logs detalhados para debug (`Log.e`, `Log.d`)
- ✅ Retorno seguro (`null` ou lista vazia) em caso de erro
- ✅ Verificação de título obrigatório no `load()`

### 2. **Busca de Imagem Robusta**
```kotlin
// ANTES (v55)
val posterUrl = this.selectFirst("img")?.attr("src")

// DEPOIS (v56)
val img = this.selectFirst("img")
val posterUrl = fixUrlNull(
    img?.attr("src")
        ?: img?.attr("data-src")
        ?: img?.attr("data-lazy-src")
        ?: img?.attr("data-original")
)
```

### 3. **URLs Consistentes**
- ✅ Uso de `fixUrl()` e `fixUrlNull()` em todos os lugares
- ✅ Remoção de concatenação manual de URLs
- ✅ Tratamento robusto de URLs relativas e absolutas

### 4. **Logs Detalhados**
```kotlin
// ANTES (v55)
println("🎬 Processando fonte: $sourceName")

// DEPOIS (v56)
Log.d("MaxSeries", "🎬 Processando fonte: $sourceName -> $sourceUrl")
```

### 5. **Seletores Robustos**
```kotlin
// Busca de título mais robusta
val title = document.selectFirst("h1.entry-title, h1")?.text()?.trim()

// Busca de poster mais robusta
val img = document.selectFirst(".poster img, div.poster img, .sheader .poster img")

// Busca de gêneros mais robusta
val tags = document.select(".genres a, .sgeneros a").map { it.text() }
```

### 6. **Suporte Híbrido de Episódios**
- ✅ Suporte ao formato MaxSeries original (`.seasons-lst .season`)
- ✅ Suporte ao formato AnimesOnlineCC (`ul.episodios li`)
- ✅ Detecção automática do formato usado

## 📊 TESTE DE FUNCIONALIDADE

### Resultados do Teste Automatizado:
```
🌐 Site: https://www.maxseries.one ✅ (Status: 200)
🔍 Seletor 'div.items article.item': ✅ (36 itens encontrados)
🎬 Página de filmes: ✅ (1 filme encontrado)
📺 Página de séries: ✅ (42 séries encontradas)
🔍 Pesquisa: ✅ (funcional)
```

### Estrutura dos Itens Encontrados:
```
📝 Título: "Garota Sequestrada" ✅
🔗 Link: "https://www.maxseries.one/series/..." ✅
🖼️ Imagem: "https://image.tmdb.org/t/p/w500/..." ✅
```

## 🆚 COMPARAÇÃO COM ANIMESONLINECC

| Aspecto | AnimesOnlineCC | MaxSeries v55 | MaxSeries v56 |
|---------|----------------|---------------|---------------|
| **Error Handling** | ✅ Try/catch completo | ❌ Sem tratamento | ✅ Try/catch completo |
| **Logs** | ✅ Log.d() detalhado | ❌ println() básico | ✅ Log.d() detalhado |
| **Busca de Imagem** | ✅ Múltiplos atributos | ❌ Só `src` | ✅ Múltiplos atributos |
| **URLs** | ✅ fixUrl() consistente | ❌ Concatenação manual | ✅ fixUrl() consistente |
| **Seletores** | ✅ Robustos | ❌ Básicos | ✅ Robustos |

## 🚀 RELEASE INFORMATION

- **Versão**: v56
- **Arquivo**: MaxSeries.cs3 (128,164 bytes)
- **GitHub**: https://github.com/franciscoalro/TestPlugins/releases/tag/v56.0
- **plugins.json**: Atualizado para v56

## 📱 COMO TESTAR

1. **Instalar no CloudStream**:
   - Adicionar repositório: `https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/plugins.json`
   - Instalar MaxSeries v56

2. **Verificar Funcionalidade**:
   - ✅ Conteúdo deve aparecer na página principal
   - ✅ Pesquisa deve funcionar
   - ✅ Carregamento de detalhes deve funcionar
   - ✅ Links de vídeo devem ser encontrados

3. **Debug (se necessário)**:
   - Conectar dispositivo via ADB
   - Verificar logs do Android: `adb logcat | grep MaxSeries`
   - Procurar por logs detalhados com emojis

## 🎯 EXPECTATIVA

Com base no teste automatizado e nas correções aplicadas, **MaxSeries v56 deve resolver o problema de conteúdo não aparecer no CloudStream app**.

As correções são baseadas no provider AnimesOnlineCC que está funcionando corretamente, garantindo compatibilidade e robustez.

## 📞 PRÓXIMOS PASSOS

Se v56 ainda não funcionar:
1. Verificar logs do Android para erros específicos
2. Comparar comportamento real com AnimesOnlineCC
3. Investigar possíveis problemas de rede ou CloudStream
4. Considerar usar ADB para debug em tempo real