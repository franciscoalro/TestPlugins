# 🎬 Video Extractor Test Suite

TypeScript testing environment for video extractors before Kotlin implementation in Cloudstream.

## 🎯 Purpose

Test and validate video extraction logic in TypeScript before implementing in Kotlin for MaxSeries provider. This allows:

- ✅ Faster iteration and debugging
- ✅ Easy testing with real URLs
- ✅ Network inspection with browser tools
- ✅ Proven logic before Kotlin port

## 📦 Installation

```bash
cd video-extractor-test
npm install
```

## 🚀 Usage

### Test Single URL

```bash
# MyVidPlay
npm run dev https://myvidplay.com/e/abc123

# DoodStream
npm run dev https://doodstream.com/e/xyz789

# With referer
npm run dev https://myvidplay.com/e/abc123 https://maxseries.pics
```

### List Available Extractors

```bash
npm run dev list
```

### Run All Tests

```bash
npm test
```

### Test Specific Extractor

```bash
npm run test:myvidplay
npm run test:doodstream
npm run test:megaembed
```

## 📁 Project Structure

```
video-extractor-test/
├── src/
│   ├── extractors/
│   │   ├── base.ts           # Base extractor class
│   │   ├── myvidplay.ts      # MyVidPlay extractor
│   │   ├── doodstream.ts     # DoodStream extractor
│   │   ├── megaembed.ts      # MegaEmbed extractor
│   │   └── index.ts          # Extractor registry
│   ├── types/
│   │   └── index.ts          # TypeScript types
│   ├── utils/
│   │   ├── http.ts           # HTTP client
│   │   └── logger.ts         # Logger utility
│   ├── index.ts              # Main entry point
│   └── test-all.ts           # Test runner
├── package.json
├── tsconfig.json
└── README.md
```

## 🔧 Implemented Extractors

### 1. MyVidPlay ✅
- **Status:** Working
- **Method:** Direct HTML extraction
- **Speed:** Fast (~1-2s)
- **Requires:** HTTP only

### 2. DoodStream ✅
- **Status:** Working
- **Method:** pass_md5 token extraction
- **Speed:** Medium (~2-3s)
- **Requires:** HTTP only

### 3. MegaEmbed ⚠️
- **Status:** Requires manual interaction
- **Method:** Browser automation + network capture
- **Speed:** Slow (~30-60s with clicks)
- **Requires:** Playwright browser

## 📊 Test Results

Results are saved to `test-results.json`:

```json
[
  {
    "extractor": "MyVidPlay",
    "url": "https://myvidplay.com/e/abc123",
    "success": true,
    "linksFound": 1,
    "subtitlesFound": 0,
    "extractionTime": 1234,
    "links": [...]
  }
]
```

## 🔄 Workflow: TypeScript → Kotlin

### 1. Test in TypeScript
```bash
npm run dev https://myvidplay.com/e/abc123
```

### 2. Verify Extraction Logic
- Check console output
- Verify M3U8 URLs
- Test with multiple sources

### 3. Port to Kotlin
- Copy extraction logic
- Adapt to Kotlin syntax
- Use Cloudstream APIs
- Test in MaxSeries

### 4. Example Port

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

## 🎯 Adding New Extractor

### 1. Create Extractor File

```typescript
// src/extractors/newextractor.ts
import { BaseExtractor } from './base';
import { ExtractorResult } from '../types';

export class NewExtractor extends BaseExtractor {
  name = 'NewExtractor';
  domains = ['newsite.com'];

  async extract(url: string, referer?: string): Promise<ExtractorResult> {
    const startTime = Date.now();
    
    try {
      // Your extraction logic here
      const links = [];
      
      return this.createResult(url, links, [], startTime);
    } catch (error: any) {
      return this.createErrorResult(url, error.message, startTime);
    }
  }
}
```

### 2. Register in index.ts

```typescript
import { NewExtractor } from './newextractor';

export const ALL_EXTRACTORS: IExtractor[] = [
  new MyVidPlayExtractor(),
  new DoodStreamExtractor(),
  new NewExtractor() // Add here
];
```

### 3. Add Test URLs

```typescript
// src/test-all.ts
const TEST_URLS: Record<string, { url: string; referer?: string }[]> = {
  'NewExtractor': [
    { url: 'https://newsite.com/e/test1' }
  ]
};
```

### 4. Test

```bash
npm run dev https://newsite.com/e/test1
```

## 🐛 Debugging

### Enable Verbose Logging

```typescript
// In extractor file
this.logger.debug('Detailed debug info');
```

### Inspect Network

For browser-based extractors (MegaEmbed):
- Browser opens in non-headless mode
- Use DevTools Network tab
- Monitor XHR/Fetch requests

### Save HTML for Analysis

```typescript
import * as fs from 'fs';
fs.writeFileSync('debug.html', html);
```

## 📚 Common Patterns

### Pattern 1: M3U8 in Script Tags

```typescript
$('script').each((_, element) => {
  const script = $(element).html() || '';
  const m3u8Pattern = /https?:\/\/[^"'\s]+\.m3u8/g;
  const matches = script.match(m3u8Pattern);
});
```

### Pattern 2: JSON with file URL

```typescript
const jsonPattern = /"file"\s*:\s*"([^"]+\.m3u8)"/;
const match = html.match(jsonPattern);
```

### Pattern 3: Base64 Encoded Data

```typescript
const base64Pattern = /data:([^;]+);base64,([^"']+)/;
const match = html.match(base64Pattern);
const decoded = Buffer.from(match[2], 'base64').toString();
```

### Pattern 4: Token-based URLs

```typescript
const tokenResponse = await HttpClient.get(tokenUrl, referer);
const token = tokenResponse.data;
const videoUrl = `${baseUrl}?token=${token}`;
```

## ⚡ Performance Tips

1. **Use HTTP first** - Avoid browser automation if possible
2. **Cache tokens** - Reuse authentication tokens
3. **Parallel requests** - Use Promise.all() for multiple sources
4. **Timeout handling** - Set reasonable timeouts (30s)
5. **Retry logic** - Implement exponential backoff

## 🔐 Security Notes

- Never commit real video URLs to git
- Use environment variables for sensitive data
- Respect rate limits
- Add delays between requests if needed

## 📝 TODO

- [ ] Add StreamTape extractor
- [ ] Add Mixdrop extractor
- [ ] Add Filemoon extractor
- [ ] Implement retry logic
- [ ] Add quality detection
- [ ] Add subtitle extraction
- [ ] Create Kotlin code generator
- [ ] Add performance benchmarks

## 🤝 Contributing

1. Test extractor in TypeScript
2. Verify with real URLs
3. Document extraction method
4. Port to Kotlin
5. Update MaxSeries provider

## 📄 License

MIT
