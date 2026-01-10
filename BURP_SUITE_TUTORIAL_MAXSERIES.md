# 🎓 Tutorial Prático: Burp Suite no MaxSeries

**Objetivo:** Capturar link de vídeo M3U8 do MaxSeries usando Burp Suite

---

## 📋 Pré-requisitos

- [ ] Burp Suite Community instalado
- [ ] Navegador (Chrome ou Firefox)
- [ ] 15 minutos de tempo

---

## 🚀 Passo a Passo Completo

### **PASSO 1: Baixar e Instalar Burp Suite**

#### 1.1 Download
```
https://portswigger.net/burp/communitydownload
```

- Escolha: **Burp Suite Community Edition** (GRÁTIS)
- Baixe para Windows

#### 1.2 Instalação
1. Execute o instalador `.exe`
2. Clique "Next" → "Next" → "Install"
3. Aguarde instalação (2-3 minutos)
4. Clique "Finish"

---

### **PASSO 2: Iniciar Burp Suite**

#### 2.1 Primeira Execução
1. Abra Burp Suite
2. Selecione: **"Temporary project"**
3. Clique **"Next"**
4. Selecione: **"Use Burp defaults"**
5. Clique **"Start Burp"**

Aguarde carregar (10-20 segundos)

#### 2.2 Interface Principal

Você verá 4 abas principais:
- **Dashboard** - Visão geral
- **Target** - Sites alvo
- **Proxy** - ⭐ **USAREMOS ESTA**
- **Intruder** - Ataques automatizados

---

### **PASSO 3: Configurar Proxy no Navegador**

#### Opção A: Firefox (RECOMENDADO - Mais Fácil)

**3.1 Abrir Configurações**
```
Menu (☰) → Settings → Network Settings → Settings
```

**3.2 Configurar Proxy Manual**
```
⚫ Manual proxy configuration

HTTP Proxy: 127.0.0.1
Port: 8080

☑ Also use this proxy for HTTPS

⚪ No proxy for: [deixe vazio]

☑ Enable DNS over HTTPS [DESMARQUE]
```

**3.3 Salvar**
```
Clique "OK"
```

#### Opção B: Chrome com FoxyProxy

**3.1 Instalar Extensão**
```
Chrome Web Store → Buscar "FoxyProxy"
→ Adicionar ao Chrome
```

**3.2 Configurar Proxy**
```
Clique no ícone FoxyProxy
→ Options
→ Add New Proxy
→ Title: Burp Suite
→ Proxy Type: HTTP
→ Proxy IP: 127.0.0.1
→ Port: 8080
→ Save
```

**3.3 Ativar**
```
Clique no ícone FoxyProxy
→ Selecione "Burp Suite"
```

---

### **PASSO 4: Instalar Certificado SSL**

**IMPORTANTE:** Sem isso, sites HTTPS não funcionarão!

#### 4.1 Gerar Certificado no Burp

1. No Burp Suite, vá para: **Proxy → Options**
2. Role até: **"Proxy Listeners"**
3. Verifique que `127.0.0.1:8080` está **"Running"**
4. Clique em: **"Import / export CA certificate"**
5. Selecione: **"Export → Certificate in DER format"**
6. Clique **"Next"**
7. Salve como: `burp-certificate.cer` (Desktop)
8. Clique **"Close"**

#### 4.2 Instalar no Firefox

1. Firefox: `Menu → Settings → Privacy & Security`
2. Role até: **"Certificates"**
3. Clique: **"View Certificates"**
4. Aba: **"Authorities"**
5. Clique: **"Import..."**
6. Selecione: `burp-certificate.cer` (do Desktop)
7. Marque: **☑ Trust this CA to identify websites**
8. Clique: **"OK"**

#### 4.3 Instalar no Chrome

1. Chrome: `Settings → Privacy and security → Security`
2. Role até: **"Manage certificates"**
3. Aba: **"Trusted Root Certification Authorities"**
4. Clique: **"Import..."**
5. Clique: **"Next"**
6. Selecione: `burp-certificate.cer`
7. Clique: **"Next" → "Next" → "Finish"**
8. Clique: **"OK"**

---

### **PASSO 5: Testar Configuração**

#### 5.1 Verificar Proxy

1. No Burp: **Proxy → Intercept**
2. Certifique-se: **"Intercept is off"** (clique no botão se estiver "on")
3. Vá para aba: **"HTTP history"**

#### 5.2 Testar Navegação

1. No navegador, acesse: `http://example.com`
2. No Burp, veja se apareceu requisição em **"HTTP history"**

**✅ Se apareceu:** Configuração OK!  
**❌ Se não apareceu:** Revise passos 3 e 4

---

### **PASSO 6: Configurar Filtros (Opcional mas Recomendado)**

#### 6.1 Filtrar por Domínio

No Burp: **Proxy → HTTP history → Filter**

Marque:
```
☑ Show only in-scope items
```

Depois: **Target → Scope → Add**
```
Protocol: https
Host: megaembed.link
File: [deixe vazio]
```

Clique **"OK"**

Repita para:
- `playerthree.online`
- `maxseries.one`

---

### **PASSO 7: Capturar Requisições do MaxSeries**

#### 7.1 Preparar Burp

1. **Proxy → HTTP history**
2. Clique direito → **"Clear history"** (limpar histórico antigo)
3. Deixe a aba aberta

#### 7.2 Navegar no MaxSeries

**No navegador:**

1. Vá para: `https://www.maxseries.one`
2. Escolha uma série (ex: Terra de Pecados)
3. Clique em um episódio
4. **AGUARDE** o player carregar (10-15 segundos)
5. Clique no botão **PLAY** ▶️

#### 7.3 Observar Requisições

No Burp, você verá várias requisições aparecendo em tempo real!

---

### **PASSO 8: Encontrar a API do MegaEmbed**

#### 8.1 Filtrar Requisições

No **HTTP history**, procure por:

```
Host: megaembed.link
```

Você verá algo como:

```
GET /api/v1/info?id=XXXXX
GET /api/v1/video?id=XXXXX&w=1920&h=1080&r=playerthree.online
```

#### 8.2 Identificar a Requisição Importante

Clique na requisição: `/api/v1/video?id=...`

**Verifique:**
- **Status:** 200 (verde)
- **Length:** ~5000-6000 bytes

---

### **PASSO 9: Analisar a Resposta**

#### 9.1 Ver Resposta

1. Clique na requisição `/api/v1/video`
2. Painel inferior → Aba **"Response"**
3. Sub-aba: **"Raw"**

Você verá dados binários/encriptados.

#### 9.2 Tentar Decodificar

**Opção 1: Procurar por URLs**

1. Sub-aba: **"Hex"**
2. Procure por padrões: `http` ou `.m3u8`
3. Use Ctrl+F para buscar

**Opção 2: Usar Decoder**

1. Selecione todo o conteúdo da resposta
2. Clique direito → **"Send to Decoder"**
3. Vá para aba **"Decoder"**
4. Tente decodificar:
   - **Decode as:** Base64
   - **Decode as:** URL
   - **Decode as:** HTML

#### 9.3 Procurar Link M3U8

Procure por strings que contenham:
- `https://`
- `.m3u8`
- `playlist`
- `master`

---

### **PASSO 10: Usar o Repeater**

#### 10.1 Enviar para Repeater

1. Clique direito na requisição `/api/v1/video`
2. **"Send to Repeater"**
3. Vá para aba **"Repeater"**

#### 10.2 Modificar e Testar

Você pode:
- Mudar parâmetros (ex: `w=1280&h=720`)
- Adicionar headers
- Testar diferentes IDs

Clique **"Send"** para ver a resposta!

---

### **PASSO 11: Salvar Dados**

#### 11.1 Salvar Requisição

1. Clique direito na requisição
2. **"Save item"**
3. Salve como: `megaembed-video-request.xml`

#### 11.2 Copiar Resposta

1. Aba **"Response" → "Raw"**
2. Selecione tudo (Ctrl+A)
3. Copie (Ctrl+C)
4. Cole em arquivo de texto

---

## 🎯 Exemplo Real - Terra de Pecados

### Requisição Capturada

```http
GET /api/v1/video?id=3wnuij&w=1920&h=1080&r=playerthree.online HTTP/1.1
Host: megaembed.link
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)
Accept: application/json, text/plain, */*
Referer: https://playerthree.online/
Origin: https://megaembed.link
```

### Resposta

```
Status: 200 OK
Content-Type: application/octet-stream
Content-Length: 5939

[Dados binários/encriptados]
```

### Próximo Passo

A resposta está **encriptada**. Você precisa:

1. **Analisar o JavaScript** do player
2. **Encontrar a função** de decriptação
3. **Reverter a encriptação** manualmente
4. **Ou usar DevTools** para capturar o link quando o vídeo carregar

---

## 💡 Dicas Pro

### Dica 1: Usar com DevTools Simultaneamente

1. Burp Suite captura APIs
2. DevTools (F12) captura M3U8 final

**Workflow:**
```
Burp Suite → Entender fluxo
DevTools → Capturar link final
```

### Dica 2: Salvar Sessão

```
Burp → Project → Save copy
```

Salve todo o histórico para análise posterior!

### Dica 3: Filtro Avançado

**HTTP history → Filter:**

```
☑ Filter by search term: m3u8
☑ Filter by MIME type: JSON
☑ Show only in-scope items
```

---

## ❌ Troubleshooting

### Problema: "Proxy connection refused"

**Solução:**
```
1. Verifique se Burp está rodando
2. Proxy → Options → Proxy Listeners
3. Certifique-se que 127.0.0.1:8080 está "Running"
4. Reinicie o navegador
```

### Problema: "SSL Certificate Error"

**Solução:**
```
1. Reinstale o certificado (Passo 4)
2. Certifique-se de marcar "Trust for websites"
3. Reinicie o navegador
4. Limpe cache do navegador
```

### Problema: "Nenhuma requisição aparece"

**Solução:**
```
1. Proxy → Intercept → Certifique-se que está "OFF"
2. Verifique proxy no navegador (127.0.0.1:8080)
3. Teste com http://example.com
4. Verifique firewall/antivírus
```

---

## ✅ Checklist Final

Antes de começar:

- [ ] Burp Suite instalado e rodando
- [ ] Proxy configurado (127.0.0.1:8080)
- [ ] Certificado SSL instalado
- [ ] Teste com example.com funcionou
- [ ] HTTP history visível
- [ ] Navegador pronto

**Agora você está pronto para capturar! 🚀**

---

## 📚 Recursos Adicionais

- **Vídeo Tutorial:** https://www.youtube.com/results?search_query=burp+suite+tutorial
- **Documentação:** https://portswigger.net/burp/documentation
- **Comunidade:** https://forum.portswigger.net/

---

## 🎬 Resumo do Fluxo Completo

```
1. Instalar Burp Suite
   ↓
2. Configurar proxy (127.0.0.1:8080)
   ↓
3. Instalar certificado SSL
   ↓
4. Testar com example.com
   ↓
5. Navegar no MaxSeries
   ↓
6. Clicar no PLAY
   ↓
7. No Burp: HTTP history
   ↓
8. Procurar: megaembed.link/api/v1/video
   ↓
9. Analisar resposta
   ↓
10. Usar Decoder/Repeater
   ↓
11. Extrair link M3U8
   ↓
12. Testar no VLC
```

---

**Tempo estimado:** 15-20 minutos  
**Dificuldade:** ⭐⭐⭐ Intermediário  
**Resultado:** Link M3U8 para VLC

**Boa sorte! 🍀**
