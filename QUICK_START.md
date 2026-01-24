# 🎯 Quick Start: Extração de Vídeo MaxSeries

## 📦 O Que Foi Criado

### 1. Scripts Browser (TypeScript/JavaScript)
- ✅ `browser-video-extractor.ts` - Versão TypeScript
- ✅ `browser-video-extractor.js` - Versão JavaScript (pronta para usar)
- ✅ `GUIA_BROWSER_SCRIPT.md` - Documentação completa

**Como usar:**
```
1. Abra https://maxseries.one/episodio/[ID]
2. Pressione F12 (DevTools)
3. Cole o conteúdo de browser-video-extractor.js
4. Aguarde a análise automática
```

---

### 2. Scripts Puppeteer (Node.js)
- ✅ `test-puppeteer-extractor.js` - Teste automatizado
- ✅ `package.json` - Dependências
- ✅ `PUPPETEER_TO_KOTLIN.md` - Guia de migração

**Como usar:**
```bash
# Já instalado! ✅
npm install

# Executar teste
node test-puppeteer-extractor.js https://maxseries.one/episodio/258444
```

---

### 3. Scripts Python (Selenium)
- ✅ `extract_video_easy.py` - Extração básica HTTP
- ✅ `extract_video_advanced.py` - Extração com Selenium
- ✅ `README_EXTRACAO.md` - Guia de uso

**Como usar:**
```bash
# Básico (rápido)
python extract_video_easy.py https://maxseries.one/episodio/258444

# Avançado (completo)
pip install selenium webdriver-manager
python extract_video_advanced.py https://maxseries.one/episodio/258444
```

---

## 🚀 Próximos Passos

### Passo 1: Testar Puppeteer ⏭️
```bash
node test-puppeteer-extractor.js https://maxseries.one/episodio/258444
```

**O que vai acontecer:**
- ✅ Abrirá navegador Chrome (visível)
- ✅ Navegará para o episódio
- ✅ Interceptará requisições de rede
- ✅ Analisará iframes
- ✅ Salvará resultados em `puppeteer-results.json`

---

### Passo 2: Analisar Resultados
```bash
# Ver resultados
code puppeteer-results.json

# Ou no notepad
notepad puppeteer-results.json
```

**O que procurar:**
- 🎬 URLs M3U8 capturadas
- 📦 Segmentos TS
- 🎭 Arquivos disfarçados (.woff2, .txt)
- 🔗 Padrões de URL

---

### Passo 3: Implementar em Kotlin
Baseado nos resultados do Puppeteer, você vai:

1. **Identificar padrões de URL**
   ```
   Exemplo: https://cdn.megaembed.cc/v4/{code}/{id}/master.m3u8
   ```

2. **Criar/Atualizar extractor Kotlin**
   ```kotlin
   // Já existe: MegaEmbedWebViewResolver.kt
   // Você pode melhorar baseado nos padrões encontrados
   ```

3. **Testar no dispositivo**
   ```bash
   .\gradlew MaxSeries:make
   adb install -r MaxSeries\build\MaxSeries.cs3
   ```

---

## 📊 Comparação de Abordagens

| Método | Velocidade | Facilidade | Precisão | Uso |
|--------|-----------|------------|----------|-----|
| **Browser Script** | ⚡ Instantâneo | ✅ Cola e roda | 🎯 Alta | Debug rápido |
| **Puppeteer** | ⚠️ 10-20s | ✅ Automatizado | 🎯 Muito alta | Testes completos |
| **Python Selenium** | ⚠️ 15-30s | ⚠️ Requer setup | 🎯 Alta | Alternativa |
| **Kotlin WebView** | ⚡ Rápido | ⚠️ Requer build | 🎯 Alta | Produção |

---

## 💡 Dicas

### Para Debug Rápido
```javascript
// Use o browser script (F12 → Console)
// Mais rápido para testar ideias
```

### Para Testes Completos
```bash
# Use Puppeteer
node test-puppeteer-extractor.js [URL]
```

### Para Produção
```kotlin
// Implemente em Kotlin (CloudStream)
// Baseado nos padrões descobertos
```

---

## 🔧 Comandos Úteis

### Puppeteer
```bash
# Teste básico
npm run test:episode

# Teste customizado
node test-puppeteer-extractor.js https://maxseries.one/episodio/[ID]
```

### Python
```bash
# Básico
python extract_video_easy.py [URL]

# Avançado
python extract_video_advanced.py [URL]
```

### Kotlin (CloudStream)
```bash
# Build
.\gradlew MaxSeries:make

# Instalar
adb install -r MaxSeries\build\MaxSeries.cs3

# Logs
adb logcat | Select-String "MaxSeries"
```

---

## 📁 Estrutura de Arquivos

```
brcloudstream/
├── 🌐 Browser Scripts
│   ├── browser-video-extractor.ts
│   ├── browser-video-extractor.js ⭐
│   └── GUIA_BROWSER_SCRIPT.md
│
├── 🤖 Puppeteer
│   ├── test-puppeteer-extractor.js ⭐
│   ├── package.json
│   └── PUPPETEER_TO_KOTLIN.md
│
├── 🐍 Python
│   ├── extract_video_easy.py
│   ├── extract_video_advanced.py
│   └── README_EXTRACAO.md
│
└── 📱 Kotlin (CloudStream)
    └── MaxSeries/
        └── src/main/kotlin/
            └── extractors/
                └── MegaEmbedWebViewResolver.kt ⭐
```

---

## ❓ FAQ

### "Qual script devo usar primeiro?"
**R:** Comece com o **Puppeteer** (`test-puppeteer-extractor.js`). Ele é automatizado e completo.

### "O navegador não abre no Puppeteer"
**R:** Mude `headless: false` para `headless: true` no arquivo `test-puppeteer-extractor.js` (linha 18).

### "Nenhuma URL foi capturada"
**R:** Possíveis causas:
- Vídeo requer clique manual no Play
- Player usa criptografia avançada
- Aguarde mais tempo (aumente o timeout na linha 95)

### "Como implementar em Kotlin?"
**R:** Veja o guia completo em `PUPPETEER_TO_KOTLIN.md`. Há um template de código pronto.

---

## ✅ Checklist

- [x] Puppeteer instalado
- [ ] Teste executado
- [ ] Resultados analisados
- [ ] Padrões identificados
- [ ] Kotlin implementado
- [ ] Plugin testado no dispositivo

---

**🎯 Próximo Comando:**
```bash
node test-puppeteer-extractor.js https://maxseries.one/episodio/258444
```

---

**Versão:** 1.0  
**Última Atualização:** 23/01/2026  
**Status:** ✅ Pronto para uso
