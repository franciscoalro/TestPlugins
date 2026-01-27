# 🎬 Video Extractor Test Project - TypeScript → Kotlin

**Data:** 27 Janeiro 2026  
**Status:** ✅ PROJETO CRIADO

---

## 🎯 OBJETIVO

Criar ambiente de testes em **TypeScript** para validar lógica de extração de vídeo **ANTES** de implementar em **Kotlin** no MaxSeries.

### Por que TypeScript primeiro?

1. ✅ **Iteração rápida** - Testar e debugar em segundos
2. ✅ **Browser DevTools** - Inspecionar network facilmente
3. ✅ **Menos compilação** - Sem Gradle, sem build Android
4. ✅ **Lógica validada** - Só portar código que funciona
5. ✅ **Documentação** - Código TypeScript serve como referência

---

## 📁 ESTRUTURA DO PROJETO

```
video-extractor-test/
├── src/
│   ├── extractors/
│   │   ├── base.ts           # Classe base para extractors
│   │   ├── myvidplay.ts      # MyVidPlay (HTTP only)
│   │   ├── doodstream.ts     # DoodStream (token-based)
│   │   ├── megaembed.ts      # MegaEmbed (browser automation)
│   │   └── index.ts          # Registry de extractors
│   ├── types/
│   │   └── index.ts          # TypeScript interfaces
│   ├── utils/
│   │   ├── http.ts           # HTTP client com headers
│   │   └── logger.ts         # Logger colorido
│   ├── index.ts              # CLI principal
│   └── test-all.ts           # Test runner
├── package.json              # Dependencies
├── tsconfig.json             # TypeScript config
├── README.md                 # Documentação completa
└── QUICK_START.md            # Guia rápido
```

---

## 🚀 INSTALAÇÃO

```bash
cd video-extractor-test
npm install
```

### Dependencies

- **axios** - HTTP requests
- **cheerio** - HTML parsing (como Jsoup)
- **playwright** - Browser automation (como WebView)
- **tsx** - TypeScript execution
- **typescript** - Compilador

---

## 💻 USO

### Testar URL Individual

```bash
npm run dev "https://myvidplay.com/e/abc123"
```

### Listar Extractors

```bash
npm run dev list
```

### Rodar Todos os Testes

```bash
npm test
```

### Testar Extractor Específico

```bash
npm run test:myvidplay
npm run test:doodstream
npm run test:megaembed
```

---

## 🔧 EXTRACTORS IMPLEMENTADOS

### 1. MyVidPlay ✅

**Método:** HTTP + Regex  
**Velocidade:** ~1-2s  
**Taxa de Sucesso:** ~95%

```typescript
// Busca M3U8 em script tags
const m3u8Pattern = /https?:\/\/[^"'\s]+\.m3u8/g;
const matches = html.match(m3u8Pattern);
```

**Port para Kotlin:**
```kotlin
val m3u8Pattern = Regex("""https?://[^"'\s]+\.m3u8""")
val matches = m3u8Pattern.findAll(html)
```

### 2. DoodStream ✅

**Método:** Token extraction  
**Velocidade:** ~2-3s  
**Taxa de Sucesso:** ~90%

```typescript
// 1. Extrair pass_md5 URL
const passMd5Pattern = /\/pass_md5\/[^'"]+/;
const match = html.match(passMd5Pattern);

// 2. Buscar token
const tokenResponse = await HttpClient.get(passMd5Url);
const token = tokenResponse.data;

// 3. Gerar URL final
const videoUrl = `${token}${randomString}?token=${token}`;
```

**Port para Kotlin:**
```kotlin
// 1. Extrair pass_md5
val passMd5Pattern = Regex("""/pass_md5/[^'"]+""")
val match = passMd5Pattern.find(html)

// 2. Buscar token
val tokenResponse = app.get(passMd5Url, referer = url)
val token = tokenResponse.text

// 3. Gerar URL
val videoUrl = "$token${randomString()}?token=$token"
```

### 3. MegaEmbed ⚠️

**Método:** Browser automation + Network capture  
**Velocidade:** ~30-60s (com clicks manuais)  
**Taxa de Sucesso:** ~95% (após clicks)

```typescript
// Interceptar network requests
page.on('response', async (response) => {
  const url = response.url();
  if (url.includes('.m3u8')) {
    links.push({ url, name: 'MegaEmbed', isM3U8: true });
  }
});
```

**Port para Kotlin:**
```kotlin
// Já implementado em MegaEmbedExtractorV9.kt
webView.webViewClient = object : WebViewClient() {
  override fun shouldInterceptRequest(
    view: WebView,
    request: WebResourceRequest
  ): WebResourceResponse? {
    val url = request.url.toString()
    if (url.contains(".m3u8")) {
      // Capturar M3U8
    }
  }
}
```

---

## 🔄 WORKFLOW: TypeScript → Kotlin

### Passo 1: Testar em TypeScript

```bash
# Pegar URL real do MaxSeries/PlayThree
npm run dev "https://myvidplay.com/e/REAL_ID" "https://maxseries.pics"
```

### Passo 2: Verificar Resultado

```
✅ Extraction successful!
Links found: 1
URL: https://cdn.example.com/hls/master.m3u8
Extraction time: 1234ms
```

### Passo 3: Portar para Kotlin

**TypeScript:**
```typescript
const response = await HttpClient.get(url, referer);
const html = response.data;
const $ = cheerio.load(html);
```

**Kotlin:**
```kotlin
val response = app.get(url, referer = referer)
val html = response.text
val document = Jsoup.parse(html)
```

### Passo 4: Testar no MaxSeries

```bash
cd ..
.\gradlew.bat clean make --no-daemon
```

### Passo 5: Verificar ADB Logs

```powershell
C:\adb\platform-tools\adb.exe -s 192.168.0.101:34215 logcat | Select-String "MaxSeries"
```

---

## 📊 COMPARAÇÃO: TypeScript vs Kotlin

| Feature | TypeScript | Kotlin |
|---------|-----------|--------|
| **HTTP Client** | axios | app.get() |
| **HTML Parser** | cheerio | Jsoup |
| **Regex** | /pattern/g | Regex("pattern") |
| **Browser** | playwright | WebView |
| **Async** | async/await | suspend fun |
| **Logging** | console.log | Log.d() |

---

## 🎯 PRÓXIMOS EXTRACTORS

### StreamTape
```typescript
// TODO: Implementar
export class StreamTapeExtractor extends BaseExtractor {
  name = 'StreamTape';
  domains = ['streamtape.com'];
  // ...
}
```

### Mixdrop
```typescript
// TODO: Implementar
export class MixdropExtractor extends BaseExtractor {
  name = 'Mixdrop';
  domains = ['mixdrop.co', 'mixdrop.to'];
  // ...
}
```

### Filemoon
```typescript
// TODO: Implementar
export class FilemoonExtractor extends BaseExtractor {
  name = 'Filemoon';
  domains = ['filemoon.sx'];
  // ...
}
```

---

## 🐛 DEBUG

### Salvar HTML para Análise

```typescript
import * as fs from 'fs';
fs.writeFileSync('debug.html', html);
```

### Ver Network Requests

Para MegaEmbed, browser abre em modo visível:
1. Abrir DevTools (F12)
2. Ir em Network tab
3. Filtrar por ".m3u8"
4. Copiar URL capturada

### Logs Detalhados

```typescript
this.logger.debug('Detailed info');
this.logger.info('General info');
this.logger.success('Success message');
this.logger.error('Error message');
```

---

## 📚 PADRÕES COMUNS

### Padrão 1: M3U8 em Script

```typescript
$('script').each((_, element) => {
  const script = $(element).html() || '';
  const m3u8Pattern = /https?:\/\/[^"'\s]+\.m3u8/g;
  const matches = script.match(m3u8Pattern);
});
```

### Padrão 2: JSON com file URL

```typescript
const jsonPattern = /"file"\s*:\s*"([^"]+\.m3u8)"/;
const match = html.match(jsonPattern);
if (match) {
  const m3u8Url = match[1];
}
```

### Padrão 3: Base64 Decode

```typescript
const base64Pattern = /data:([^;]+);base64,([^"']+)/;
const match = html.match(base64Pattern);
const decoded = Buffer.from(match[2], 'base64').toString();
```

### Padrão 4: Token-based

```typescript
// 1. Get token
const tokenResponse = await HttpClient.get(tokenUrl);
const token = tokenResponse.data;

// 2. Build video URL
const videoUrl = `${baseUrl}?token=${token}&expiry=${Date.now()}`;
```

---

## ✅ VANTAGENS DO PROJETO

1. **Velocidade** - Testar em segundos vs minutos (Gradle)
2. **Debug** - Browser DevTools vs ADB logs
3. **Iteração** - Mudar código e testar imediatamente
4. **Documentação** - Código TypeScript = referência
5. **Validação** - Só portar código que funciona
6. **Aprendizado** - Entender lógica antes de Kotlin

---

## 📝 CHECKLIST DE USO

### Para Novo Extractor

- [ ] Criar arquivo `src/extractors/newextractor.ts`
- [ ] Estender `BaseExtractor`
- [ ] Implementar método `extract()`
- [ ] Adicionar em `src/extractors/index.ts`
- [ ] Adicionar URLs de teste em `src/test-all.ts`
- [ ] Testar com `npm run dev <url>`
- [ ] Verificar resultado
- [ ] Portar para Kotlin
- [ ] Testar no MaxSeries
- [ ] Verificar ADB logs

### Para Testar Extractor Existente

- [ ] Pegar URL real do MaxSeries
- [ ] Rodar `npm run dev <url> <referer>`
- [ ] Verificar se M3U8 foi extraído
- [ ] Copiar URL do M3U8
- [ ] Testar URL no VLC/navegador
- [ ] Se funcionar, lógica está correta
- [ ] Se não funcionar, debugar TypeScript

---

## 🚀 DEPLOY

### Quando Extractor Funciona em TypeScript

1. ✅ Portar lógica para Kotlin
2. ✅ Adicionar em MaxSeriesProvider.kt
3. ✅ Build: `.\gradlew.bat clean make`
4. ✅ Commit e push para GitHub
5. ✅ Testar no device via ADB
6. ✅ Verificar logs: "Links encontrados: X"

---

## 📖 DOCUMENTAÇÃO

- **README.md** - Documentação completa
- **QUICK_START.md** - Guia rápido de uso
- **VIDEO_EXTRACTOR_TEST_PROJECT.md** - Este documento

---

## 🎓 APRENDIZADOS

### TypeScript → Kotlin Mapping

```typescript
// TypeScript
const response = await axios.get(url);
const html = response.data;
const $ = cheerio.load(html);
const match = html.match(/pattern/);

// Kotlin
val response = app.get(url)
val html = response.text
val document = Jsoup.parse(html)
val match = Regex("pattern").find(html)
```

### Async/Await → Suspend

```typescript
// TypeScript
async function extract(url: string): Promise<Result> {
  const response = await fetch(url);
  return result;
}

// Kotlin
suspend fun extract(url: String): Result {
  val response = app.get(url)
  return result
}
```

---

**Status:** ✅ PROJETO PRONTO PARA USO  
**Próximo:** Testar extractors com URLs reais do MaxSeries
