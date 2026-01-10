# 🔍 Burp Suite para Web Scraping - Guia Completo

## 📋 O que é Burp Suite?

Burp Suite é um **proxy HTTP interceptador** que captura TODAS as requisições entre seu navegador e os servidores. É a ferramenta **MAIS PODEROSA** para:

- ✅ Capturar APIs escondidas
- ✅ Ver requisições AJAX/Fetch
- ✅ Interceptar WebSockets
- ✅ Modificar requisições em tempo real
- ✅ Repetir requisições (Repeater)
- ✅ Analisar tokens e cookies

---

## 🚀 Instalação

### Download
```
https://portswigger.net/burp/communitydownload
```

**Versão Community (Grátis)** é suficiente para scraping!

### Instalação Windows
1. Baixe o instalador `.exe`
2. Execute e siga o wizard
3. Escolha "Temporary project"
4. Use configurações padrão

---

## ⚙️ Configuração Básica

### 1. Configurar Proxy no Navegador

**Opção A: Extensão FoxyProxy (Recomendado)**

1. Instale FoxyProxy no Chrome/Firefox
2. Adicione novo proxy:
   - **Tipo:** HTTP
   - **Host:** `127.0.0.1`
   - **Porta:** `8080`
3. Ative o proxy

**Opção B: Configuração Manual**

**Chrome:**
```
Settings → System → Open proxy settings
→ LAN Settings → Proxy Server
   Address: 127.0.0.1
   Port: 8080
```

**Firefox:**
```
Settings → Network Settings → Manual proxy
   HTTP Proxy: 127.0.0.1
   Port: 8080
   ☑ Also use this proxy for HTTPS
```

### 2. Instalar Certificado SSL

Para interceptar HTTPS:

1. No Burp Suite: **Proxy → Options → Import/Export CA Certificate**
2. Export em formato DER
3. No navegador:
   - Chrome: `Settings → Privacy → Manage certificates → Import`
   - Firefox: `Settings → Privacy → View Certificates → Import`
4. Marque: "Trust for identifying websites"

---

## 🎯 Capturando Requisições do MaxSeries

### Passo 1: Iniciar Burp Suite

```
1. Abra Burp Suite
2. Temporary Project → Next
3. Use Burp defaults → Start Burp
4. Vá para aba "Proxy" → "Intercept"
5. Certifique-se que está "Intercept is on"
```

### Passo 2: Configurar Filtros

**Proxy → Options → Intercept Client Requests:**

Adicione filtros para capturar apenas o que importa:

```
✅ And URL matches: .*megaembed.*
✅ And URL matches: .*playerthree.*
✅ And URL matches: .*\.m3u8
✅ And URL matches: .*api.*
```

### Passo 3: Navegar no MaxSeries

1. Ative o proxy no navegador (FoxyProxy)
2. Vá para: `https://www.maxseries.one`
3. Escolha uma série/episódio
4. Clique no play

### Passo 4: Ver Requisições Capturadas

**Proxy → HTTP History:**

Aqui você verá TODAS as requisições! 🎉

Procure por:
- `megaembed.link/api/v1/info`
- `megaembed.link/api/v1/video`
- URLs com `.m3u8`

---

## 🔧 Ferramentas Essenciais do Burp

### 1. **Repeater** (Repetir Requisições)

**Uso:**
1. Clique direito em uma requisição → "Send to Repeater"
2. Vá para aba "Repeater"
3. Modifique headers/parâmetros
4. Clique "Send"
5. Veja a resposta

**Exemplo - Testar API do MegaEmbed:**

```http
GET /api/v1/video?id=3wnuij&w=1920&h=1080&r=playerthree.online HTTP/1.1
Host: megaembed.link
User-Agent: Mozilla/5.0
Referer: https://playerthree.online/
Accept: application/json
```

Clique "Send" → Veja resposta!

### 2. **Decoder** (Decodificar Dados)

Se a resposta estiver codificada:

1. Copie o texto
2. Vá para aba "Decoder"
3. Cole no campo
4. Tente decodificar:
   - Base64
   - URL
   - HTML
   - Hex

### 3. **Comparer** (Comparar Respostas)

Compare duas requisições para ver diferenças:

1. Selecione 2 requisições
2. Clique direito → "Send to Comparer"
3. Vá para aba "Comparer"
4. Clique "Compare"

---

## 📊 Exemplo Prático: MaxSeries

### Fluxo Capturado

```
1. GET https://www.maxseries.one/series/assistir-terra-de-pecados-online
   ↓
2. GET https://playerthree.online/embed/synden/
   ↓
3. GET https://playerthree.online/episodio/255703
   ↓
4. Redirect para https://megaembed.link/?id=3wnuij
   ↓
5. GET https://megaembed.link/api/v1/info?id=3wnuij
   ↓
6. GET https://megaembed.link/api/v1/video?id=3wnuij&w=1920&h=1080&r=playerthree.online
   ↓
7. 🎯 RESPOSTA CONTÉM O LINK DO VÍDEO!
```

### Analisando a Resposta

**Se a resposta for JSON:**
```json
{
  "sources": [
    {
      "file": "https://cdn.example.com/video.m3u8",
      "type": "hls"
    }
  ]
}
```

**Se for binário/encriptado:**
- Use Decoder para tentar Base64
- Procure por padrões de URL no hex
- Analise headers para pistas

---

## 🎓 Técnicas Avançadas

### 1. Match and Replace (Modificar Automaticamente)

**Proxy → Options → Match and Replace:**

Exemplo - Adicionar header em todas requisições:

```
Type: Request header
Match: ^Host.*
Replace: Host: megaembed.link
Referer: https://playerthree.online/
```

### 2. Scope (Filtrar Domínios)

**Target → Scope:**

Adicione apenas domínios relevantes:
```
✅ megaembed.link
✅ playerthree.online
✅ maxseries.one
```

Depois em **Proxy → Options:**
```
☑ Show only in-scope items
```

### 3. Exportar Requisições

**Proxy → HTTP History:**

1. Selecione requisições
2. Clique direito → "Save items"
3. Formato: XML ou JSON

---

## 🔍 Encontrando Links M3U8

### Método 1: Busca no HTTP History

**Proxy → HTTP History → Filter:**

```
Filter by MIME type: ☑ Script
Filter by MIME type: ☑ JSON
Filter by search term: m3u8
```

### Método 2: Regex Search

**Proxy → HTTP History → Search:**

```
Regex: https?://[^\s"']+\.m3u8[^\s"']*
```

### Método 3: Response Analysis

Para cada requisição suspeita:

1. Clique na requisição
2. Vá para aba "Response"
3. Procure por:
   - `"file":`
   - `"src":`
   - `"url":`
   - `.m3u8`
   - `playlist`

---

## 💡 Dicas Pro

### 1. Usar com Playwright

Combine Burp Suite + Playwright:

```javascript
// Configure Playwright para usar Burp como proxy
const browser = await chromium.launch({
  proxy: {
    server: 'http://127.0.0.1:8080'
  }
});
```

Agora você captura TUDO no Burp enquanto Playwright navega!

### 2. Salvar Sessão

**Project → Save copy:**

Salve todo o histórico de requisições para análise posterior.

### 3. Extensões Úteis

**Extender → BApp Store:**

- **Logger++** - Logging avançado
- **Autorize** - Testar autorizações
- **JSON Beautifier** - Formatar JSON
- **Turbo Intruder** - Requisições em massa

---

## 🎯 Caso de Uso: Extrair Link do MegaEmbed

### Passo a Passo Completo

1. **Iniciar Burp Suite**
   ```
   Proxy → Intercept → Intercept is on
   ```

2. **Configurar Navegador**
   - Ativar proxy 127.0.0.1:8080
   - Instalar certificado SSL

3. **Navegar**
   ```
   https://www.maxseries.one → Episódio → Play
   ```

4. **No Burp, procurar:**
   ```
   HTTP History → Filter: megaembed
   ```

5. **Encontrar requisição:**
   ```
   GET /api/v1/video?id=XXXXX
   ```

6. **Analisar resposta:**
   - Aba "Response"
   - Procurar por "file", "src", "m3u8"

7. **Usar Repeater:**
   - Send to Repeater
   - Modificar parâmetros
   - Testar diferentes IDs

8. **Copiar link M3U8:**
   ```
   https://cdn.example.com/video.m3u8?token=...
   ```

9. **Testar no VLC:**
   ```bash
   vlc "LINK_COPIADO"
   ```

---

## 📝 Comparação: Burp Suite vs DevTools

| Recurso | Burp Suite | DevTools (F12) |
|---------|------------|----------------|
| Interceptar requisições | ✅ Sim | ❌ Não |
| Modificar requisições | ✅ Sim | ⚠️ Limitado |
| Repetir requisições | ✅ Fácil | ⚠️ Manual |
| Ver WebSockets | ✅ Sim | ✅ Sim |
| Decodificar dados | ✅ Sim | ❌ Não |
| Comparar respostas | ✅ Sim | ❌ Não |
| Salvar histórico | ✅ Sim | ⚠️ Limitado |
| Automação | ✅ Extensões | ❌ Não |

**Conclusão:** Burp Suite é **MUITO MAIS PODEROSO** para scraping!

---

## 🚨 Troubleshooting

### Problema: "Proxy refused connection"

**Solução:**
```
1. Verifique se Burp está rodando
2. Proxy → Options → Proxy Listeners
3. Certifique-se que 127.0.0.1:8080 está "Running"
```

### Problema: "SSL Certificate Error"

**Solução:**
```
1. Reinstale o certificado do Burp
2. Certifique-se de marcar "Trust for websites"
3. Reinicie o navegador
```

### Problema: "Nenhuma requisição aparece"

**Solução:**
```
1. Proxy → Intercept → Intercept is off (desative temporariamente)
2. Proxy → Options → Intercept Client Requests → Remove filtros
3. Verifique se proxy está ativo no navegador
```

---

## 🎬 Workflow Recomendado para MaxSeries

```
1. Abrir Burp Suite
   ↓
2. Configurar proxy no navegador (127.0.0.1:8080)
   ↓
3. Adicionar filtro: .*megaembed.* e .*\.m3u8
   ↓
4. Navegar no MaxSeries e clicar no play
   ↓
5. No Burp: Proxy → HTTP History
   ↓
6. Procurar: /api/v1/video
   ↓
7. Analisar Response
   ↓
8. Copiar link M3U8
   ↓
9. Testar no VLC
   ↓
10. Usar Repeater para automatizar
```

---

## 📚 Recursos Adicionais

- **Documentação Oficial:** https://portswigger.net/burp/documentation
- **Web Security Academy:** https://portswigger.net/web-security
- **YouTube:** "Burp Suite Tutorial for Beginners"

---

## ✅ Checklist Final

Antes de começar a capturar:

- [ ] Burp Suite instalado e rodando
- [ ] Proxy configurado no navegador (127.0.0.1:8080)
- [ ] Certificado SSL instalado
- [ ] Filtros configurados (opcional)
- [ ] Aba "HTTP History" aberta
- [ ] Navegador pronto para navegar

**Agora você está pronto para capturar QUALQUER requisição! 🚀**

---

**Criado para o projeto EstampaPro/MaxSeries**  
**Data:** 2026-01-10
