# 🎬 MegaEmbed Extractor V5 - Guia Completo

## 📋 Visão Geral

O **MegaEmbedExtractorV5** é responsável por extrair vídeos do servidor `megaembed.link`, que usa **ofuscação avançada** para proteger os links de vídeo.

## 🗂️ Arquivos Envolvidos

### 1. **MegaEmbedExtractorV5.kt** (Principal)
**Localização:** `MaxSeries/src/main/kotlin/com/franciscoalro/maxseries/extractors/v5/`

**Responsabilidades:**
- Interceptar requisições do WebView
- Capturar URLs de vídeo (.m3u8, .txt, .mp4)
- Emitir links para o player do Cloudstream

### 2. **MegaEmbedLinkFetcher.kt** (API Helper)
**Localização:** `MaxSeries/src/main/kotlin/com/franciscoalro/maxseries/extractors/`

**Responsabilidades:**
- Chamar API do MegaEmbed
- Construir URLs baseadas em padrões conhecidos
- Validar playlists

### 3. **HeadersBuilder.kt** (Utilitário)
**Localização:** `MaxSeries/src/main/kotlin/com/franciscoalro/maxseries/utils/`

**Responsabilidades:**
- Criar headers HTTP customizados
- Simular navegador real (Firefox 147)

### 4. **JsonHelper.kt** (Utilitário)
**Localização:** `MaxSeries/src/main/kotlin/com/franciscoalro/maxseries/utils/`

**Responsabilidades:**
- Parsear JSON de forma segura
- Ignorar propriedades desconhecidas

---

## 🔍 Como Funciona (Passo a Passo)

### **Fluxo de Extração:**

```
1. Usuário clica em episódio
   ↓
2. MaxSeriesProvider identifica URL do MegaEmbed
   ↓
3. MegaEmbedExtractorV5.getUrl() é chamado
   ↓
4. Método 1: WebView Interception (PRINCIPAL)
   ├─ Abre URL no WebView invisível
   ├─ Intercepta requisições de rede
   ├─ Captura URLs que terminam em .txt, .m3u8, .woff2
   └─ Retorna URL capturada
   ↓
5. Se falhar → Método 2: JavaScript Injection
   ├─ Injeta código JS no WebView
   ├─ Busca por <video> tags
   └─ Extrai src do player
   ↓
6. Se falhar → Método 3: API Legacy
   ├─ Chama MegaEmbedLinkFetcher
   ├─ Tenta API oficial do MegaEmbed
   └─ Constrói URL baseada em padrões
   ↓
7. Link extraído é enviado para o player
```

---

## 🎯 Método Principal: WebView Interception

### **Código Relevante (linhas 100-196):**

```kotlin
private suspend fun extractWithIntelligentInterception(
    url: String,
    referer: String?,
    callback: (ExtractorLink) -> Unit
): Boolean {
    // 1. Extrair videoId da URL
    val videoId = extractVideoId(url)
    
    // 2. Configurar WebView Resolver
    val resolver = WebViewResolver(
        // Interceptar URLs que contenham:
        // - /v4/{shard}/{videoId}/cf-master.*.txt
        // - /v4/*.woff2 (segmentos disfarçados)
        interceptUrl = Regex("""/v4/[a-z0-9]+/[a-z0-9]+/(?:cf-master|index-).*?\.txt"""),
        
        // Timeout de 25 segundos
        timeout = 25_000L,
        
        // JavaScript para buscar no DOM
        script = """
            // Procurar por cf-master.*.txt no HTML
            var html = document.documentElement.innerHTML;
            var match = html.match(/https?:\/\/[^"'\s]+\/cf-master\.\d+\.txt/);
            if (match) return match[0];
            
            // Procurar por <video> tags
            var videos = document.querySelectorAll('video');
            for (var i = 0; i < videos.length; i++) {
                if (videos[i].src) return videos[i].src;
            }
        """
    )
    
    // 3. Fazer requisição com interceptação
    val response = app.get(url, interceptor = resolver)
    
    // 4. Verificar se capturou URL válida
    if (isValidVideoUrl(finalUrl)) {
        emitExtractorLink(finalUrl, url, callback)
        return true
    }
}
```

---

## 🔐 Tecnologias de Ofuscação do MegaEmbed

### **1. Domínios Dinâmicos (CDNs)**
O MegaEmbed **muda constantemente** os domínios CDN:

```kotlin
// CDNs conhecidos (v107):
"valenium.shop"
"spo3.marvellaholdings.sbs"  // NOVO
"sqtd.luminairemotion.online"
"stzm.marvellaholdings.sbs"
"srcf.marvellaholdings.sbs"
```

**Por quê?** Para evitar bloqueios e dificultar scraping.

### **2. Arquivos Disfarçados**
Playlists HLS são disfarçadas como outros tipos de arquivo:

```
❌ Normal:  https://cdn.com/video/playlist.m3u8
✅ MegaEmbed: https://cdn.com/v4/x6b/3wnuij/cf-master.1767386783.txt
```

**Tipos de disfarce:**
- `.txt` → Playlist M3U8
- `.woff2` → Segmentos de vídeo TS
- `.woff` → Segmentos de vídeo TS

### **3. Timestamps Dinâmicos**
Cada URL tem um timestamp único que **expira**:

```
https://stzm.marvellaholdings.sbs/v4/x6b/3wnuij/cf-master.1767386783.txt
                                                              ^^^^^^^^^^
                                                              Timestamp Unix
```

**Solução:** Capturar em tempo real via WebView.

### **4. Shards Rotativos**
O `shard` (partição) muda por episódio:

```
/v4/x6b/3wnuij/...  → Episódio 1
/v4/x7c/4xpvjk/...  → Episódio 2
/v4/x8d/5yqwkl/...  → Episódio 3
```

**Shards conhecidos:** `x6b`, `x7c`, `x8d`, `x9e`, `xa1`, `xb2`

---

## 🛠️ Estrutura da URL Final

```
https://{CDN}/v4/{shard}/{videoId}/cf-master.{timestamp}.txt
       │      │   │       │         │          │
       │      │   │       │         │          └─ Timestamp Unix (expira)
       │      │   │       │         └─ Nome do arquivo (cf-master ou index-)
       │      │   │       └─ ID do vídeo (fixo por episódio)
       │      │   └─ Shard (partição, rotativo)
       │      └─ Versão da API (v4)
       └─ CDN (dinâmico)
```

**Exemplo real:**
```
https://stzm.marvellaholdings.sbs/v4/x6b/3wnuij/cf-master.1767386783.txt
```

---

## 📊 Métodos de Extração (Prioridade)

| Método | Técnica | Taxa de Sucesso | Tempo |
|--------|---------|-----------------|-------|
| **1. WebView Interception** | Interceptar requisições de rede | ~90% | 5-25s |
| **2. JavaScript Injection** | Injetar JS e buscar no DOM | ~60% | 10-30s |
| **3. API Legacy** | Chamar API oficial + bruteforce | ~30% | 15-45s |

---

## 🎓 Por Que 3 Métodos?

### **Método 1: WebView Interception** (Preferido)
✅ **Vantagens:**
- Captura URL **exata** gerada pelo player
- Não depende de API
- Funciona mesmo se a API mudar

❌ **Desvantagens:**
- Requer WebView (mais lento)
- Consome mais recursos

### **Método 2: JavaScript Injection** (Backup)
✅ **Vantagens:**
- Acessa DOM diretamente
- Pode encontrar URLs escondidas

❌ **Desvantagens:**
- Depende da estrutura HTML
- Pode falhar se o player mudar

### **Método 3: API Legacy** (Último Recurso)
✅ **Vantagens:**
- Não usa WebView
- Mais rápido se funcionar

❌ **Desvantagens:**
- API pode estar offline
- Bruteforce de shards é lento

---

## 🔧 Como Debugar

### **1. Ver Logs no ADB**
```bash
adb logcat | grep "MegaEmbedExtractorV5_LIVE"
```

**Logs importantes:**
```
🎬 URL: https://megaembed.link/#3wnuij
🆔 VideoId alvo: 3wnuij
🚀 Iniciando WebView Interception...
📜 JS Callback capturou: https://stzm.marvellaholdings.sbs/v4/x6b/3wnuij/cf-master.1767386783.txt
🎯 URL VÁLIDA ENCONTRADA: ...
✅ WebView interceptou com sucesso!
```

### **2. Verificar se a V5 está ativa**
Procure por:
```
=== MEGAEMBED V5 LIVE CAPTURE (v91) ===
```

Se não aparecer, o Cloudstream pode estar usando uma versão antiga em cache.

---

## 🚨 Problemas Comuns

### **Problema 1: "Nenhum método conseguiu capturar"**
**Causa:** CDN mudou ou timeout muito curto

**Solução:**
1. Aumentar timeout (linha 125): `timeout = 35_000L`
2. Adicionar novo CDN em `KNOWN_CDN_DOMAINS` (linha 34-46)

### **Problema 2: "URL capturada mas playback falha"**
**Causa:** Headers incorretos

**Solução:**
Verificar headers em `emitExtractorLink()` (linhas 274-286):
```kotlin
"Referer" to "https://megaembed.link/",
"Origin" to "https://megaembed.link"
```

### **Problema 3: "WebView timeout"**
**Causa:** JavaScript não encontrou URL a tempo

**Solução:**
Aumentar `maxAttempts` no script JS (linha 130):
```javascript
var maxAttempts = 300; // 30s em vez de 20s
```

---

## 📝 Checklist de Funcionamento

Para o MegaEmbed funcionar, você precisa:

- [ ] **MegaEmbedExtractorV5.kt** compilado e no package correto
- [ ] **MegaEmbedLinkFetcher.kt** disponível
- [ ] **HeadersBuilder.kt** com método `megaEmbed()`
- [ ] **JsonHelper.kt** configurado
- [ ] **MaxSeriesProvider.kt** chamando o extractor (linha 547)
- [ ] WebView habilitado no Cloudstream
- [ ] Permissões de internet no AndroidManifest.xml

---

## 🎯 Próximos Passos

1. **Testar em um episódio real**
2. **Verificar logs do ADB**
3. **Ajustar timeout se necessário**
4. **Adicionar novos CDNs conforme descobertos**

---

**Versão:** V5 (v91+)  
**Última Atualização:** Janeiro 2026  
**Autor:** MaxSeries Team
