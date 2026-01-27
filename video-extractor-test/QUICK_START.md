# 🚀 Quick Start Guide

## Instalação Rápida

```bash
cd video-extractor-test
npm install
```

## Testar Extractor

### MyVidPlay (Mais Rápido)

```bash
npm run dev "https://myvidplay.com/e/SEU_VIDEO_ID"
```

**Exemplo de saída:**
```
[MyVidPlay] ℹ️  Extracting from: https://myvidplay.com/e/abc123
[MyVidPlay] ✅ Found M3U8: https://cdn.example.com/video/master.m3u8
[MyVidPlay] ✅ Extracted 1 link(s)
[Main] ✅ Extraction successful!
[Main] ℹ️  Links found: 1
[Main] ℹ️  Extraction time: 1234ms
```

### DoodStream

```bash
npm run dev "https://doodstream.com/e/SEU_VIDEO_ID"
```

### MegaEmbed (Requer Clicks Manuais)

```bash
npm run dev "https://megaembed.link/#SEU_VIDEO_ID"
```

**Atenção:** Browser abrirá e você precisa clicar 3 vezes para remover overlays.

## Listar Extractors Disponíveis

```bash
npm run dev list
```

## Rodar Todos os Testes

```bash
npm test
```

## Adicionar URLs de Teste

Edite `src/test-all.ts`:

```typescript
const TEST_URLS: Record<string, { url: string; referer?: string }[]> = {
  'MyVidPlay': [
    { url: 'https://myvidplay.com/e/REAL_VIDEO_ID' },
    { url: 'https://myvidplay.com/e/ANOTHER_ID' }
  ]
};
```

## Workflow Completo

### 1. Testar URL Real

```bash
# Pegar URL real do MaxSeries
npm run dev "https://myvidplay.com/e/abc123" "https://maxseries.pics"
```

### 2. Verificar Resultado

```
✅ Extraction successful!
Links found: 1
URL: https://cdn.example.com/hls/master.m3u8
Quality: Unknown
M3U8: true
```

### 3. Portar para Kotlin

Se funcionou no TypeScript, copie a lógica para Kotlin:

**TypeScript:**
```typescript
const m3u8Pattern = /https?:\/\/[^"'\s]+\.m3u8/g;
const matches = html.match(m3u8Pattern);
```

**Kotlin:**
```kotlin
val m3u8Pattern = Regex("""https?://[^"'\s]+\.m3u8""")
val matches = m3u8Pattern.findAll(html)
```

### 4. Testar no MaxSeries

```bash
cd ..
.\gradlew.bat clean make --no-daemon
```

## Dicas

### Debug HTML

```typescript
// Adicione no extractor
import * as fs from 'fs';
fs.writeFileSync('debug.html', html);
```

### Ver Requisições de Rede

Para MegaEmbed, o browser abre em modo visível. Use DevTools (F12) para ver Network.

### Timeout

Se demorar muito, ajuste timeout em `src/utils/http.ts`:

```typescript
timeout: 30000, // 30 segundos
```

## Problemas Comuns

### Erro: "No extractor found"

URL não corresponde a nenhum domínio registrado. Verifique `domains` no extractor.

### Erro: "No video sources found"

O site pode ter mudado o HTML. Inspecione a página e atualize os padrões regex.

### Erro: "Timeout"

Site está lento ou bloqueou o request. Tente:
- Aumentar timeout
- Adicionar delay entre requests
- Verificar headers (User-Agent, Referer)

## Próximos Passos

1. ✅ Testar extractors existentes
2. ✅ Adicionar URLs reais de teste
3. ✅ Criar novos extractors (StreamTape, Mixdrop, Filemoon)
4. ✅ Portar lógica funcionando para Kotlin
5. ✅ Atualizar MaxSeries provider
