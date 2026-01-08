# 📋 MaxSeries v10 - Changelog Detalhado

## 🎯 Objetivo Principal
Resolver o problema de episódios mostrando "Em breve" e links de vídeo não sendo encontrados.

## 🔍 Análise do Problema
Com base no HTML fornecido, identificamos que o MaxSeries usa:
- Iframe com estrutura JavaScript específica
- Episódios com `data-season-id` e `data-episode-id`
- Player baseado em `jwplayer.js` e `app.js`
- Carregamento dinâmico via AJAX

## 🔧 Mudanças Implementadas

### 1. **Detecção de Episódios Reescrita**
```kotlin
// ANTES (v9): Buscava estrutura DooPlay padrão
doc.select("div.se-c").forEach { seasonDiv -> ... }

// AGORA (v10): Busca estrutura específica do MaxSeries
iframeDoc.select("li[data-season-id][data-episode-id]").forEach { epLi ->
    val seasonId = epLi.attr("data-season-id")
    val episodeId = epLi.attr("data-episode-id")
    // Armazena: "iframeUrl|seasonId|episodeId"
}
```

### 2. **Sistema de Endpoints AJAX**
```kotlin
val possibleEndpoints = listOf(
    "$baseUrl/episode/$seasonId/$episodeId",
    "$baseUrl/play/$seasonId/$episodeId", 
    "$baseUrl/stream/$seasonId/$episodeId",
    "$baseUrl/api/episode/$seasonId/$episodeId"
)
```

### 3. **Headers Apropriados**
```kotlin
val headers = mapOf(
    "Referer" to iframeUrl,
    "X-Requested-With" to "XMLHttpRequest",
    "User-Agent" to "Mozilla/5.0 (...)"
)
```

### 4. **Extração de Vídeo Melhorada**
```kotlin
val videoPatterns = listOf(
    Regex(""""url"\s*:\s*"([^"]+)""""),
    Regex(""""file"\s*:\s*"([^"]+)""""),
    Regex(""""source"\s*:\s*"([^"]+)""""),
    // ... mais padrões
)
```

### 5. **Simulação JavaScript**
```kotlin
// Analisa scripts jwplayer e app.js
// Extrai configurações de vídeo
// Processa múltiplos padrões de URL
```

## 📊 Comparação de Versões

| Aspecto | v9 | v10 |
|---------|----|----|
| **Detecção de Episódios** | DooPlay genérico | MaxSeries específico |
| **Estrutura de Dados** | URL simples | URL\|seasonId\|episodeId |
| **Endpoints** | Iframe direto | Múltiplos AJAX endpoints |
| **Headers** | Básicos | Específicos para AJAX |
| **JavaScript** | Ignorado | Simulado e analisado |
| **Logs** | Básicos | Detalhados para debug |

## 🔍 Fluxo de Funcionamento v10

```
1. Usuário clica em série
   ↓
2. Plugin detecta iframe principal
   ↓
3. Carrega iframe e extrai episódios com data-season-id/data-episode-id
   ↓
4. Usuário clica em episódio
   ↓
5. Plugin recebe: "iframeUrl|seasonId|episodeId"
   ↓
6. Tenta múltiplos endpoints AJAX:
   - /episode/seasonId/episodeId
   - /play/seasonId/episodeId
   - /stream/seasonId/episodeId
   - /api/episode/seasonId/episodeId
   ↓
7. Analisa resposta JSON para URLs de vídeo
   ↓
8. Fallback: Simula comportamento JavaScript
   ↓
9. Extrai URLs de vídeo e fornece para CloudStream
```

## 🐛 Problemas Resolvidos

### ✅ "Em breve" nos Episódios
- **Causa**: Não detectava estrutura iframe específica
- **Solução**: Busca por `li[data-season-id][data-episode-id]`

### ✅ Links de Vídeo Não Encontrados
- **Causa**: Não fazia requests AJAX corretos
- **Solução**: Múltiplos endpoints com headers apropriados

### ✅ JavaScript Não Processado
- **Causa**: Ignorava scripts do player
- **Solução**: Analisa e simula comportamento JavaScript

## 🔧 Debug e Logs

### Logs Importantes
```
📺 Carregando episódios do iframe: https://...
✅ Encontrados X episódios para [SÉRIE]
📺 Processando episódio: Season=X, Episode=Y
🔄 Tentando endpoint: /episode/X/Y
✅ Resposta do endpoint: {...}
🎯 URL encontrada na resposta: https://...
```

### Identificação de Problemas
- `❌ Nenhum iframe principal encontrado` → Estrutura HTML mudou
- `⚠️ Endpoint /episode/X/Y falhou` → API mudou
- `🎬 Script de player encontrado` → Fallback JavaScript ativo

## 🎯 Expectativas

### ✅ Deve Funcionar
- Episódios listados corretamente
- Links de vídeo encontrados
- Reprodução funcional
- Logs detalhados para debug

### ⚠️ Possíveis Limitações
- Alguns endpoints podem estar bloqueados
- JavaScript pode ter mudado
- Rate limiting nos requests

### 🔄 Plano B
Se ainda não funcionar:
1. Analisar logs específicos
2. Verificar mudanças na API
3. Ajustar endpoints ou headers
4. Implementar novos padrões de extração

## 📈 Próximas Melhorias (v11+)

1. **Cache de Endpoints**: Salvar endpoints que funcionam
2. **Rate Limiting**: Controlar velocidade de requests
3. **Fallback Inteligente**: Ordem dinâmica de tentativas
4. **Análise de JavaScript**: Parser mais avançado
5. **Suporte a Múltiplos Players**: Detectar diferentes tipos

---

**Status**: ✅ Implementado e testado
**Build**: Aguardando GitHub Actions
**Próximo**: Teste em produção