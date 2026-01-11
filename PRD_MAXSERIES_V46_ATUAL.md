# PRD - MaxSeries CloudStream Provider v46
## Product Requirements Document - Estado Atual

**Data**: 11 Janeiro 2026  
**Versão**: v46.0  
**Status**: ✅ Funcional com limitações

---

## 📊 RESUMO EXECUTIVO

### ✅ O que está funcionando:
- **Build e Deploy**: 100% funcional
- **Integração CloudStream**: Instalação e carregamento OK
- **Fonte MyVidplay**: Reprodução funcionando
- **Interface**: Navegação e busca operacional

### ⚠️ Limitações identificadas:
- **Fontes limitadas**: Apenas MyVidplay reproduzindo
- **MegaEmbed**: Não está extraindo vídeos
- **PlayerEmbedAPI**: Não está funcionando
- **Outras fontes**: Não implementadas/funcionais

---

## 🎯 ANÁLISE FUNCIONAL DETALHADA

### 1. INFRAESTRUTURA ✅ (100% Funcional)

#### Build System
- ✅ Gradle configurado corretamente
- ✅ Android SDK integrado
- ✅ Compilação sem erros
- ✅ Geração de .cs3 automática

#### Deploy & Distribution
- ✅ GitHub Actions funcionando
- ✅ Releases automáticos
- ✅ Repository JSON atualizado
- ✅ CloudStream integration OK

### 2. CORE PROVIDER ✅ (90% Funcional)

#### Navegação e Busca
- ✅ **Homepage**: Carregamento de séries/filmes
- ✅ **Search**: Busca por título funcionando
- ✅ **Load**: Detalhes de série/filme OK
- ✅ **Episodes**: Lista de episódios correta

#### Metadata Extraction
- ✅ **Títulos**: Extração correta
- ✅ **Posters**: URLs de imagem OK
- ✅ **Descrições**: Texto extraído
- ✅ **Gêneros**: Categorização funcionando

### 3. VIDEO EXTRACTION ⚠️ (30% Funcional)

#### ✅ Fontes Funcionais
```
MyVidplay (DoodStream Clone)
├── Status: ✅ FUNCIONANDO
├── Método: HTTP direto + hash generation
├── Qualidade: HD disponível
├── Cobertura: ~40% do conteúdo
└── Confiabilidade: Alta
```

#### ❌ Fontes Não Funcionais

##### MegaEmbed
```
MegaEmbed
├── Status: ❌ NÃO FUNCIONANDO
├── Problema: Extração simplificada demais
├── Método atual: HTTP básico
├── Necessário: WebView + JavaScript execution
├── Cobertura esperada: ~50% do conteúdo
└── Prioridade: ALTA
```

##### PlayerEmbedAPI
```
PlayerEmbedAPI
├── Status: ❌ NÃO FUNCIONANDO  
├── Problema: Cadeia de redirecionamentos complexa
├── Método atual: HTTP básico
├── Necessário: WebView + iframe navigation
├── Cobertura esperada: ~30% do conteúdo
└── Prioridade: MÉDIA
```

##### Outras Fontes (Não Implementadas)
```
Fontes Adicionais Detectadas no Site:
├── Bysebuho (DoodStream clone) - Implementação: FÁCIL
├── G9R6 (DoodStream clone) - Implementação: FÁCIL  
├── Abyss.to - Implementação: MÉDIA
├── Short.icu redirects - Implementação: MÉDIA
└── Streamtape - Implementação: DIFÍCIL
```

---

## 🔍 ANÁLISE TÉCNICA DETALHADA

### Arquitetura Atual

```
MaxSeriesProvider
├── ✅ Core Navigation (100%)
├── ✅ DoodStream Extractor (100%)
├── ❌ MegaEmbed Extractor (30%)
├── ❌ PlayerEmbedAPI Extractor (20%)
└── ❌ WebView Fallback (50%)
```

### Problemas Identificados

#### 1. MegaEmbed Extraction
**Problema**: Versão simplificada não consegue bypass da criptografia
```kotlin
// ATUAL (não funciona)
val playlistUrl = MegaEmbedLinkFetcher.fetchPlaylistUrl(videoId)

// NECESSÁRIO (WebView + JS execution)
val resolver = MegaEmbedWebViewResolver(context)
val playlistUrl = resolver.resolveWithJavaScript(url)
```

#### 2. PlayerEmbedAPI Chain
**Problema**: Cadeia de redirecionamentos não seguida completamente
```
Fluxo Real:
playerembedapi.link → short.icu → abyss.to → storage.googleapis.com

Fluxo Atual (incompleto):
playerembedapi.link → [FALHA]
```

#### 3. Context Dependency
**Problema**: WebView precisa de Context Android
```kotlin
// PROBLEMA: Context não disponível em ExtractorApi
val resolver = MegaEmbedWebViewResolver(context) // context = null
```

---

## 📋 ROADMAP DE IMPLEMENTAÇÃO

### FASE 1: Fontes DoodStream Adicionais (FÁCIL - 2h)
**Objetivo**: Expandir cobertura com clones DoodStream
```
Implementar:
├── Bysebuho.com
├── G9R6.com  
└── Outros domínios DoodStream
```
**Impacto**: +20% cobertura de conteúdo

### FASE 2: MegaEmbed WebView (MÉDIO - 8h)
**Objetivo**: Implementar extração real do MegaEmbed
```
Tarefas:
├── Implementar WebView resolver
├── JavaScript execution engine
├── Network interception
└── Fallback para HTTP quando WebView falha
```
**Impacto**: +40% cobertura de conteúdo

### FASE 3: PlayerEmbedAPI Chain (MÉDIO - 6h)
**Objetivo**: Seguir cadeia completa de redirecionamentos
```
Tarefas:
├── Implementar redirect chain following
├── Short.icu handler
├── Abyss.to extraction
└── Google Cloud Storage direct links
```
**Impacto**: +25% cobertura de conteúdo

### FASE 4: Otimizações (BAIXO - 4h)
**Objetivo**: Melhorar performance e confiabilidade
```
Tarefas:
├── Cache de URLs extraídas
├── Retry logic para falhas
├── Quality detection
└── Error handling melhorado
```
**Impacto**: Melhor experiência do usuário

---

## 🎯 PRIORIDADES IMEDIATAS

### 🔥 CRÍTICO (Fazer Agora)
1. **Implementar fontes DoodStream adicionais** (Bysebuho, G9R6)
2. **Corrigir MegaEmbed com WebView real**

### ⚡ IMPORTANTE (Próxima Sprint)
3. **PlayerEmbedAPI redirect chain**
4. **WebView fallback universal**

### 📈 DESEJÁVEL (Futuro)
5. **Cache e otimizações**
6. **Novas fontes (Streamtape, etc)**

---

## 📊 MÉTRICAS DE SUCESSO

### Cobertura de Conteúdo
- **Atual**: ~40% (apenas MyVidplay)
- **Meta Fase 1**: ~60% (+DoodStream clones)
- **Meta Fase 2**: ~85% (+MegaEmbed)
- **Meta Final**: ~95% (+PlayerEmbedAPI)

### Confiabilidade
- **Atual**: 90% para MyVidplay, 0% outras fontes
- **Meta**: 85%+ para todas as fontes implementadas

### Performance
- **Atual**: ~3s para extração MyVidplay
- **Meta**: <5s para qualquer fonte

---

## 🚀 PRÓXIMOS PASSOS RECOMENDADOS

1. **Implementar Bysebuho e G9R6** (quick win)
2. **Analisar logs de falha do MegaEmbed** no CloudStream
3. **Implementar WebView resolver** para MegaEmbed
4. **Testar cada fonte individualmente** antes de deploy

**Conclusão**: O provider está funcional mas limitado. Com as implementações das Fases 1 e 2, teremos cobertura de ~85% do conteúdo disponível no MaxSeries.one.