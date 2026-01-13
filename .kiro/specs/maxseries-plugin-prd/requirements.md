# PRD - MaxSeries Plugin para CloudStream

## Introdução

Este documento descreve a arquitetura completa do plugin MaxSeries para CloudStream, incluindo todos os arquivos, componentes, fluxos de extração e fontes de vídeo disponíveis.

## Glossário

- **CloudStream**: Aplicativo Android de streaming que suporta plugins customizados
- **Provider**: Classe principal que implementa a interface com o site de origem
- **Extractor**: Classe que extrai URLs de vídeo de players embed
- **MegaEmbed**: Player embed que usa HLS ofuscado (.woff2)
- **PlayerEmbedAPI**: Player embed que retorna MP4 direto do Google Cloud Storage
- **Playerthree**: Intermediário que lista episódios e redireciona para players
- **HLS**: HTTP Live Streaming - protocolo de streaming adaptativo
- **WebView**: Componente Android para renderizar páginas web

## Visão Geral do Plugin

**Nome**: MaxSeries  
**Versão Atual**: 70  
**Autor**: franciscoalro  
**Site de Origem**: https://www.maxseries.one  
**Idioma**: pt-BR  
**Tipos de Conteúdo**: TvSeries, Movie

---

## Arquitetura de Arquivos

### Estrutura de Diretórios

```
MaxSeries/
├── build.gradle.kts                    # Configuração de build
└── src/main/kotlin/com/franciscoalro/maxseries/
    ├── MaxSeriesPlugin.kt              # Ponto de entrada do plugin
    ├── MaxSeriesProvider.kt            # Provider principal
    └── extractors/
        ├── MegaEmbedSimpleExtractor.kt # Extractor MegaEmbed (ATIVO)
        ├── PlayerEmbedAPIExtractor.kt  # Extractor PlayerEmbedAPI (ATIVO)
        ├── MegaEmbedExtractor.kt       # Extractor MegaEmbed v2 (legado)
        ├── MegaEmbedLinkFetcher.kt     # Utilitário de fetch (legado)
        └── MegaEmbedWebViewResolver.kt # Resolver WebView (legado)
```

---

## Componentes Principais

### Requirement 1: MaxSeriesPlugin.kt

**User Story:** Como desenvolvedor, quero um ponto de entrada que registre o provider e extractors, para que o CloudStream carregue o plugin corretamente.

#### Acceptance Criteria

1. THE MaxSeriesPlugin SHALL extend BasePlugin
2. THE MaxSeriesPlugin SHALL register MaxSeriesProvider as main API
3. THE MaxSeriesPlugin SHALL register MegaEmbedSimpleExtractor
4. THE MaxSeriesPlugin SHALL register PlayerEmbedAPIExtractor
5. THE MaxSeriesPlugin SHALL use @CloudstreamPlugin annotation

#### Código Atual

```kotlin
@CloudstreamPlugin
class MaxSeriesPlugin: BasePlugin() {
    override fun load() {
        registerMainAPI(MaxSeriesProvider())
        registerExtractorAPI(MegaEmbedSimpleExtractor())
        registerExtractorAPI(PlayerEmbedAPIExtractor())
    }
}
```

---

### Requirement 2: MaxSeriesProvider.kt

**User Story:** Como usuário, quero navegar por filmes e séries do MaxSeries, para que eu possa assistir conteúdo em português.

#### Acceptance Criteria

1. THE MaxSeriesProvider SHALL implement MainAPI interface
2. THE MaxSeriesProvider SHALL provide main page with "Filmes" and "Séries" categories
3. THE MaxSeriesProvider SHALL support search functionality
4. THE MaxSeriesProvider SHALL load movie and TV series details
5. THE MaxSeriesProvider SHALL extract video links from playerthree.online
6. THE MaxSeriesProvider SHALL prioritize PlayerEmbedAPI over MegaEmbed

#### Fluxo de Extração Descoberto (Jan 2026)

```
1. maxseries.one/series/... 
   └─ iframe src="playerthree.online/embed/synden/"

2. playerthree.online/embed/{slug}/
   └─ Lista de episódios com data-episode-id
   └─ AJAX: /episodio/{episodeId}

3. /episodio/{id} retorna HTML com botões:
   └─ data-source="https://playerembedapi.link/?v=xxx"
   └─ data-source="https://megaembed.link/#xxx"

4. Extractors processam cada source
```

#### Métodos Principais

| Método | Descrição |
|--------|-----------|
| `getMainPage()` | Retorna lista de filmes/séries da página inicial |
| `search()` | Busca conteúdo por query |
| `load()` | Carrega detalhes de filme/série e lista de episódios |
| `loadLinks()` | Extrai URLs de vídeo para reprodução |
| `extractPlayerthreeUrl()` | Extrai URL do iframe playerthree |
| `parseEpisodesFromPlayerthree()` | Busca episódios via AJAX |
| `extractFromPlayerthreeEpisode()` | Extrai sources de um episódio |
| `extractPlayerSources()` | Extrai URLs dos botões data-source |

---

### Requirement 3: MegaEmbedSimpleExtractor.kt (ATIVO)

**User Story:** Como usuário, quero reproduzir vídeos do MegaEmbed, para que eu possa assistir conteúdo hospedado neste player.

#### Acceptance Criteria

1. THE MegaEmbedSimpleExtractor SHALL extend ExtractorApi
2. THE MegaEmbedSimpleExtractor SHALL handle megaembed.link URLs
3. THE MegaEmbedSimpleExtractor SHALL use newExtractorLink() with type=VIDEO
4. THE MegaEmbedSimpleExtractor SHALL include HAR headers for browser emulation
5. THE MegaEmbedSimpleExtractor SHALL force internal WebView player

#### Configuração

| Propriedade | Valor |
|-------------|-------|
| name | "MegaEmbed Simple (PreRelease)" |
| mainUrl | "https://megaembed.link" |
| requiresReferer | true |
| type | ExtractorLinkType.VIDEO |

#### Headers HAR

```kotlin
mapOf(
    "User-Agent" to "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0",
    "Accept" to "*/*",
    "Accept-Language" to "pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3",
    "Accept-Encoding" to "gzip, deflate, br, zstd",
    "X-Requested-With" to "XMLHttpRequest",
    "Sec-Fetch-Dest" to "empty",
    "Sec-Fetch-Mode" to "cors",
    "Sec-Fetch-Site" to "same-origin"
)
```

#### Limitações Conhecidas

- **Erro 3003**: ExoPlayer não consegue parsear segmentos .woff2 ofuscados
- **Solução**: Requer CloudStream pre-release (jan/2026+) com parser atualizado
- **Alternativa**: Usar PlayerEmbedAPI que retorna MP4 compatível

---

### Requirement 4: PlayerEmbedAPIExtractor.kt (ATIVO)

**User Story:** Como usuário, quero reproduzir vídeos do PlayerEmbedAPI, para que eu tenha uma fonte de vídeo MP4 compatível.

#### Acceptance Criteria

1. THE PlayerEmbedAPIExtractor SHALL extend ExtractorApi
2. THE PlayerEmbedAPIExtractor SHALL handle playerembedapi.link URLs
3. THE PlayerEmbedAPIExtractor SHALL parse JSON response with sources array
4. THE PlayerEmbedAPIExtractor SHALL support both MP4 and M3U8 formats
5. THE PlayerEmbedAPIExtractor SHALL extract quality labels from response

#### Configuração

| Propriedade | Valor |
|-------------|-------|
| name | "PlayerEmbedAPI (MP4)" |
| mainUrl | "https://playerembedapi.link" |
| requiresReferer | true |

#### Formato de Resposta JSON

```json
{
  "sources": [
    {
      "file": "https://storage.googleapis.com/..../video.mp4",
      "label": "720p"
    },
    {
      "file": "https://storage.googleapis.com/..../video.m3u8",
      "label": "Auto"
    }
  ]
}
```

#### Vantagens

- Retorna MP4 direto do Google Cloud Storage
- Não requer WebView ou JavaScript
- Compatível com todas as versões do CloudStream
- Evita erro 3003 do ExoPlayer

---

## Fontes de Vídeo Disponíveis

### Fonte 1: PlayerEmbedAPI (RECOMENDADA)

| Propriedade | Valor |
|-------------|-------|
| URL Base | https://playerembedapi.link |
| Formato | MP4 / M3U8 |
| CDN | Google Cloud Storage |
| Compatibilidade | 100% |
| Prioridade | Alta |

### Fonte 2: MegaEmbed

| Propriedade | Valor |
|-------------|-------|
| URL Base | https://megaembed.link |
| Formato | HLS ofuscado (.woff2) |
| CDN | marvellaholdings.sbs (rotativo) |
| Compatibilidade | Requer pre-release |
| Prioridade | Baixa |

### Fonte 3: Playerthree (Intermediário)

| Propriedade | Valor |
|-------------|-------|
| URL Base | https://playerthree.online |
| Função | Lista episódios e redireciona |
| Endpoint AJAX | /episodio/{id} |
| Retorna | URLs do PlayerEmbedAPI e MegaEmbed |

---

## Fluxo de Dados Completo

```
┌─────────────────────────────────────────────────────────────────┐
│                        USUÁRIO                                   │
│                    Seleciona série/filme                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    MaxSeriesProvider.load()                      │
│                                                                  │
│  1. GET maxseries.one/series/{slug}                             │
│  2. Extrai iframe playerthree.online                            │
│  3. GET playerthree.online/embed/{slug}                         │
│  4. Parseia lista de episódios (data-episode-id)                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  MaxSeriesProvider.loadLinks()                   │
│                                                                  │
│  1. AJAX GET playerthree.online/episodio/{id}                   │
│  2. Extrai data-source dos botões                               │
│  3. Ordena: PlayerEmbedAPI primeiro, MegaEmbed depois           │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
┌─────────────────────────┐     ┌─────────────────────────┐
│  PlayerEmbedAPIExtractor │     │  MegaEmbedSimpleExtractor│
│                          │     │                          │
│  GET playerembedapi.link │     │  Retorna URL embed       │
│  Parse JSON sources      │     │  type=VIDEO (WebView)    │
│  Retorna MP4/M3U8        │     │  Headers HAR             │
└─────────────────────────┘     └─────────────────────────┘
              │                               │
              ▼                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                        ExoPlayer                                 │
│                                                                  │
│  PlayerEmbedAPI: ✅ Reproduz MP4 direto                         │
│  MegaEmbed: ⚠️ Erro 3003 em versões antigas                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## Arquivos Legados (Não Utilizados)

### MegaEmbedExtractor.kt

- Implementação complexa com WebView e JavaScript
- Substituído por MegaEmbedSimpleExtractor
- Mantido para referência

### MegaEmbedLinkFetcher.kt

- Utilitário para fetch de playlist via API
- Não funciona devido a tokens JWT dinâmicos
- Mantido para referência

### MegaEmbedWebViewResolver.kt

- Resolver WebView para interceptação de rede
- Não funciona em extractors (requer Activity)
- Mantido para referência

---

## Configuração de Build

### build.gradle.kts

```kotlin
version = 70

cloudstream {
    description = "MaxSeries v70 - MegaEmbed PreRelease com headers HAR e type=VIDEO."
    authors = listOf("franciscoalro")
    status = 1
    tvTypes = listOf("TvSeries", "Movie")
    language = "pt-BR"
    iconUrl = "https://www.maxseries.one/wp-content/themes/dooplay/assets/img/favicon.png"
}
```

---

## Problemas Conhecidos e Soluções

### Problema 1: Erro 3003 (PARSING_CONTAINER_UNSUPPORTED)

**Causa**: ExoPlayer não consegue parsear segmentos .woff2 do MegaEmbed  
**Solução**: Atualizar CloudStream para pre-release (jan/2026+)  
**Alternativa**: Usar PlayerEmbedAPI (priorizado automaticamente)

### Problema 2: Hash (#videoId) não enviado ao servidor

**Causa**: Fragment (#) é client-side e não é enviado em requisições HTTP  
**Solução**: Tratar hash manualmente no extractor

### Problema 3: Tokens JWT dinâmicos do MegaEmbed

**Causa**: CDN requer token JWT gerado por JavaScript  
**Solução**: Usar type=VIDEO para forçar WebView interna

---

## Histórico de Versões

| Versão | Data | Mudanças |
|--------|------|----------|
| v70 | Jan 2026 | Headers HAR completos, type=VIDEO |
| v69 | Jan 2026 | newExtractorLink() |
| v68 | Jan 2026 | WebView interna |
| v67 | Jan 2026 | Extractors simplificados |
| v66 | Jan 2026 | Prioriza PlayerEmbedAPI |

---

## Requisitos do Sistema

- CloudStream 4.x ou superior
- Android 5.0+ (API 21+)
- Para MegaEmbed: CloudStream pre-release (jan/2026+)
- Conexão com internet

---

## Notas de Implementação

1. **Priorização de Sources**: PlayerEmbedAPI é sempre chamado primeiro por ser mais compatível
2. **Headers HAR**: Copiados de captura real do navegador para evitar bloqueios
3. **type=VIDEO**: Força o CloudStream a usar WebView interna em vez de ExoPlayer direto
4. **Fallbacks**: Sistema de fallback em cascata (PlayerEmbedAPI → MegaEmbed → loadExtractor genérico)
