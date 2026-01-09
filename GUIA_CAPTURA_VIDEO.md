# 🎬 Guia: Captura de URLs de Vídeo com Selenium Indetectável

Este guia explica como usar o script `undetected-video-capture.py` para capturar URLs de vídeo de sites protegidos como MaxSeries.

## 📋 Por que isso é necessário?

O Cloudstream é um app Android que **não executa JavaScript completo**. Sites como MegaEmbed, PlayerEmbedAPI e outros usam JavaScript para:
- Decriptar tokens de vídeo
- Gerar URLs dinâmicas
- Proteger contra bots

O script usa **Selenium com Chrome indetectável** para:
1. Abrir o site como um usuário real
2. Aguardar o JavaScript executar
3. Interceptar as requisições de rede
4. Capturar as URLs finais do vídeo (`.m3u8`, `.mp4`)

---

## 🔧 Instalação

### Opção 1: Python (Recomendado)

#### Passo 1: Instalar Python
1. Baixe o Python em: https://www.python.org/downloads/
2. Durante a instalação, marque **"Add Python to PATH"**
3. Reinicie o terminal/PowerShell

#### Passo 2: Instalar dependências
```powershell
pip install undetected-chromedriver selenium webdriver-manager
```

#### Passo 3: Executar o script
```powershell
# Capturar de um episódio específico
python undetected-video-capture.py "https://www.maxseries.one/series/assistir-a-casa-do-dragao-online/"

# Capturar de um player direto
python undetected-video-capture.py "https://playerthree.online/embed/XYZ/"
```

---

### Opção 2: Node.js (Alternativa)

Se preferir Node.js, use o script `puppeteer-video-capture.js`:

#### Passo 1: Instalar Node.js
Baixe em: https://nodejs.org/

#### Passo 2: Instalar dependências
```powershell
npm install puppeteer puppeteer-extra puppeteer-extra-plugin-stealth
```

#### Passo 3: Executar
```powershell
node puppeteer-video-capture.js "https://www.maxseries.one/series/assistir-a-casa-do-dragao-online/"
```

---

## 📖 Como funciona

1. **Abre o Chrome** (versão indetectável que bypassa anti-bot)
2. **Navega para a URL** do episódio ou player
3. **Detecta iframes** de players (playerthree, megaembed, etc)
4. **Aguarda JavaScript** executar a decriptação
5. **Intercepta requisições** de rede em tempo real
6. **Filtra URLs de vídeo** (.m3u8, .mp4)
7. **Salva resultados** em JSON

---

## 📁 Arquivos de saída

- `video_capture_YYYYMMDD_HHMMSS.json` - Resultados com todas as URLs encontradas
- Contém:
  - URL do vídeo
  - Tipo (m3u8, mp4)
  - Host de origem
  - Headers necessários
  - Qualidade (se detectada)

---

## 🔗 Usando as URLs no Cloudstream

Depois de capturar as URLs, você pode:

### Para m3u8 (HLS):
```kotlin
M3u8Helper.generateM3u8(
    "NomeDaFonte",
    "URL_M3U8_CAPTURADA",
    "URL_REFERER"
).forEach(callback)
```

### Para mp4:
```kotlin
callback(
    newExtractorLink("NomeDaFonte", "NomeDaFonte", "URL_MP4_CAPTURADA") {
        this.referer = "URL_REFERER"
        this.quality = Qualities.Unknown.value
    }
)
```

---

## ⚠️ Troubleshooting

### "Chrome não inicia"
- Certifique-se que o Chrome está instalado
- O script usa o Chrome instalado no sistema

### "Nenhum vídeo encontrado"
- Aumente o tempo de espera no script
- Alguns sites precisam de mais tempo para carregar
- Tente com um episódio diferente

### "Detector de bot"
- O undetected-chromedriver deve bypassar a maioria
- Se persistir, tente com `headless=False` para ver o que acontece

---

## 🎯 Próximos Passos

1. Executar o script para capturar URLs
2. Analisar o padrão das URLs capturadas
3. Implementar o extractor correspondente no plugin Kotlin
4. Se o padrão for consistente, criar lógica automática

---

## 📞 Suporte

Se tiver dúvidas, verifique:
- Console do script para erros
- Arquivo JSON de saída
- Se o site ainda está online e funcionando
