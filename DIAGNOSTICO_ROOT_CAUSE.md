# 🔍 Diagnóstico Root Cause - PlayerEmbedAPI ERROR 2004

## 📊 Análise dos Logs

### ✅ O Que Funciona

Analisando `playerembedapi_error_20260128_201239.txt`:

```
01-28 20:12:10.822 MaxSeriesProvider: 🌐🌐🌐 PLAYEREMBEDAPI DETECTADO! 🌐🌐🌐
01-28 20:12:10.827 MaxSeriesProvider: ⚡ Tentando PlayerEmbedAPIWebViewExtractor...
01-28 20:12:10.827 MaxSeriesProvider: 📍 PlayerthreeUrl: https://playerthree.online/embed/a-knight-of-the-seven-kingdoms/
01-28 20:12:10.828 MaxSeriesProvider: 🎬 IMDB ID extraído: null
01-28 20:12:10.828 MaxSeriesProvider: ❌ IMDB ID não encontrado para PlayerEmbedAPI
01-28 20:12:10.828 MaxSeriesProvider: 🔍 Processando source: https://megaembed.link/#5fw5iy
01-28 20:12:10.828 MaxSeriesProvider: ⚡ Tentando MegaEmbedExtractorV9...
```

**Conclusão**: 
- ✅ PlayerEmbedAPI foi **detectado corretamente**
- ✅ Código tentou extrair IMDB ID
- ❌ IMDB ID **não existe** (série usa slug, não IMDB)
- ✅ Código **pulou** PlayerEmbedAPI e usou MegaEmbed
- ✅ MegaEmbed **funcionou**

### 🎯 Root Cause Identificado

**PlayerEmbedAPI só funciona para FILMES, não para SÉRIES!**

#### Por Que?

1. **Filmes** usam ViewPlayer com IMDB ID:
   ```
   https://viewplayer.online/filme/tt39307872
   ```

2. **Séries** usam PlayThree com slug:
   ```
   https://playerthree.online/embed/a-knight-of-the-seven-kingdoms/
   ```

3. **PlayerEmbedAPI** precisa de IMDB ID para funcionar:
   ```kotlin
   val viewPlayerUrl = "https://viewplayer.online/filme/$imdbId"
   ```

4. **Séries não têm IMDB ID** na URL do PlayThree (apenas slug)

### 🔍 Onde Está o Erro 2004?

O erro 2004 que o usuário reportou **NÃO está nos logs capturados**.

Os logs mostram:
- ✅ Teste com **série** (The Knight of the Seven Kingdoms)
- ✅ PlayerEmbedAPI foi **corretamente pulado** (sem IMDB ID)
- ✅ MegaEmbed **funcionou**

**Hipótese**: O erro 2004 acontece quando o usuário tenta um **FILME** (não série).

## 🎬 Teste Necessário

### Para Reproduzir o Erro 2004

1. Abrir um **FILME** (não série) no MaxSeries
2. Clicar em PlayerEmbedAPI
3. Tentar reproduzir
4. Capturar logs

### Exemplo de Filme para Testar

Baseado nos logs anteriores, o usuário testou estes filmes:
```
https://viewplayer.online/filme/tt27425164
https://viewplayer.online/filme/tt6604188
https://viewplayer.online/filme/tt32020404
```

## 🐛 Possíveis Problemas com Filmes

### 1. WebView Não Captura URLs

**Sintoma**: Timeout após 30s, nenhuma URL capturada

**Causa**: 
- Automação não clica nos botões corretos
- Popups bloqueiam o player
- Site detecta WebView

**Solução**: Melhorar automação JavaScript

### 2. URLs Capturadas Expiram

**Sintoma**: URL capturada mas dá erro 2004 ao reproduzir

**Causa**: 
- URLs têm timestamp que expira rapidamente
- Delay entre captura e reprodução

**Solução**: Reduzir tempo de extração

### 3. Headers Incorretos

**Sintoma**: URL funciona no browser mas não no player

**Causa**: 
- Faltam headers (Referer, Origin, User-Agent)
- CORS bloqueando

**Solução**: Adicionar headers ao ExtractorLink

### 4. URL Intermediária

**Sintoma**: URL capturada não é a do vídeo final

**Causa**: 
- Capturou redirect intermediário
- Não aguardou URL final do Google Storage

**Solução**: Aguardar mais tempo ou seguir redirects

## 📋 Checklist de Diagnóstico

### Para Séries (PlayThree)
- [x] PlayerEmbedAPI detectado
- [x] IMDB ID não encontrado (esperado)
- [x] PlayerEmbedAPI pulado corretamente
- [x] MegaEmbed usado como fallback
- [x] **FUNCIONA CORRETAMENTE**

### Para Filmes (ViewPlayer)
- [ ] PlayerEmbedAPI detectado
- [ ] IMDB ID extraído com sucesso
- [ ] WebView iniciado
- [ ] ViewPlayer carregado
- [ ] Botão PlayerEmbedAPI clicado
- [ ] Overlay clicado
- [ ] URLs capturadas
- [ ] ExtractorLink criado
- [ ] **PRECISA TESTAR**

## 🎯 Próximos Passos

### 1. Confirmar Tipo de Conteúdo

**Pergunta para o usuário**: 
> O erro 2004 acontece em **FILME** ou **SÉRIE**?

### 2. Se for SÉRIE

**Resposta**: 
> PlayerEmbedAPI não funciona para séries (por design). Use MegaEmbed, MyVidPlay ou DoodStream.

**Ação**: 
> Nenhuma. Código já funciona corretamente.

### 3. Se for FILME

**Ação**: 
> Capturar logs de um FILME específico:

```powershell
# Abrir um FILME (não série)
# Clicar em PlayerEmbedAPI
# Aguardar erro 2004
# Executar:
.\capture-playerembedapi-error.ps1
```

## 🔧 Melhorias Possíveis

### 1. Mensagem Mais Clara

Quando IMDB ID não é encontrado, logar:

```kotlin
Log.w(TAG, "⚠️ PlayerEmbedAPI só funciona para FILMES (ViewPlayer)")
Log.w(TAG, "⚠️ Séries (PlayThree) não têm IMDB ID - usando outros extractors")
```

### 2. Não Mostrar PlayerEmbedAPI para Séries

Filtrar sources antes de processar:

```kotlin
// Se não tem IMDB ID, remover PlayerEmbedAPI da lista
if (extractImdbIdFromUrl(playerthreeUrl) == null) {
    sources = sources.filter { !it.contains("playerembedapi", ignoreCase = true) }
}
```

### 3. Adicionar Suporte a Séries

Tentar extrair IMDB ID do HTML da página do MaxSeries:

```kotlin
// Na página do MaxSeries, procurar por IMDB ID
val imdbId = document.select("[data-imdb], [href*=imdb.com]")
    .firstOrNull()?.attr("data-imdb") ?: extractFromUrl()
```

## 📊 Resumo

| Aspecto | Status | Observação |
|---------|--------|------------|
| **Detecção** | ✅ Funciona | PlayerEmbedAPI é detectado corretamente |
| **Séries** | ✅ Funciona | Corretamente pulado (sem IMDB ID) |
| **Filmes** | ❓ Desconhecido | Precisa testar com filme específico |
| **MegaEmbed** | ✅ Funciona | Fallback funciona perfeitamente |
| **Logs** | ✅ Completos | Logs mostram fluxo correto |

## 🎬 Conclusão

**O código v220 está funcionando CORRETAMENTE para séries.**

O erro 2004 reportado pelo usuário provavelmente acontece com **FILMES**, não séries.

**Próxima ação**: Pedir ao usuário para testar um **FILME** específico e capturar logs quando o erro 2004 aparecer.

---

**Criado**: 28 Jan 2026  
**Versão**: v220  
**Status**: Aguardando teste com FILME
