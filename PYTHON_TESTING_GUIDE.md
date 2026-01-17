# 🐍 Guia de Testes em Python - MegaEmbed

## 🎯 Por Que Testar em Python Primeiro?

### ❌ Problema com Kotlin (CloudStream):
- **Ciclo Lento:** Escrever código → Build → Instalar no Android → Testar → Repetir
- **Debugging Difícil:** Logs só aparecem no Logcat do Android
- **Sem REPL:** Não dá pra testar linha por linha interativamente
- **Build Demora:** Gradle pode levar minutos para compilar

### ✅ Vantagens do Python:
- **Execução Instantânea:** Roda direto, sem compilar
- **REPL/Jupyter:** Testa linha por linha, vê resultados na hora
- **Debugging Fácil:** Print, breakpoints, inspeção de variáveis
- **Iteração Rápida:** Muda código → Roda → Vê resultado em segundos

---

## 🚀 Fluxo de Trabalho Recomendado

```
1. 🐍 PYTHON (Prototipagem)
   ├─ Usar Burp Suite para analisar site
   ├─ Escrever script Python para extrair links
   ├─ Testar diferentes URLs, headers, regex
   ├─ Validar que funciona 100%
   └─ Documentar lógica e padrões
   
2. 🔄 CONVERSÃO
   ├─ Converter lógica Python → Kotlin
   ├─ Adaptar bibliotecas (requests → OkHttp, etc.)
   └─ Manter mesma estrutura
   
3. 🤖 KOTLIN (Build Final)
   ├─ Build do plugin
   ├─ Testar no CloudStream
   └─ Ajustes finais (se necessário)
```

---

## 📦 Instalação

### 1. Instalar Python (se não tiver)
```bash
# Windows: Baixar de python.org
# Ou usar winget:
winget install Python.Python.3.11
```

### 2. Instalar Dependências
```bash
cd d:\TestPlugins-master
pip install -r requirements.txt
```

---

## 🧪 Uso do Script de Testes

### **Opção 1: Teste Rápido (URLs padrão)**
```bash
python test_megaembed.py
```

### **Opção 2: Testar URL Específica**
```bash
python test_megaembed.py --url "https://megaembed.link/#3wnuij"
```

### **Opção 3: Testar com VideoId Direto**
```bash
python test_megaembed.py --video-id 3wnuij
```

### **Opção 4: Limitar Tentativas de Construção**
```bash
python test_megaembed.py --url "https://megaembed.link/#3wnuij" --max-attempts 5
```

---

## 📊 Saída Esperada

```
============================================================
🚀 TESTE COMPLETO - MegaEmbed Link Fetcher
============================================================
URL de Entrada: https://megaembed.link/#3wnuij
============================================================

============================================================
🔍 PASSO 1: Extraindo VideoId
============================================================
URL: https://megaembed.link/#3wnuij
✅ Padrão 'Hash (#)' funcionou!
✅ VideoId extraído: 3wnuij

============================================================
🌐 PASSO 2: Testando API do MegaEmbed
============================================================
VideoId: 3wnuij

📡 Método 1: API v1
URL: https://megaembed.link/api/v1/video?id=3wnuij
Fazendo requisição...
Status Code: 200
✅ Requisição bem-sucedida!

📄 JSON Response:
{
  "token": "abc123...",
  "url": "https://stzm.marvellaholdings.sbs/v4/x6b/3wnuij/cf-master.1767386783.txt"
}

🔍 Procurando campos de vídeo...
  ✓ Campo 'url': https://stzm.marvellaholdings.sbs/...

✅ LINK DE VÍDEO ENCONTRADO!
Campo: url
URL: https://stzm.marvellaholdings.sbs/v4/x6b/3wnuij/cf-master.1767386783.txt

============================================================
✅ SUCESSO VIA API!
URL Final: https://stzm.marvellaholdings.sbs/v4/x6b/3wnuij/cf-master.1767386783.txt
============================================================

============================================================
✅ VALIDAÇÃO FINAL
============================================================
URL: https://stzm.marvellaholdings.sbs/v4/x6b/3wnuij/cf-master.1767386783.txt
Status Code: 200
É M3U8: True
Tem RESOLUTION: True

✅ M3U8 VÁLIDO!

Conteúdo (primeiras 500 chars):
#EXTM3U
#EXT-X-VERSION:3
#EXT-X-STREAM-INF:BANDWIDTH=800000,RESOLUTION=640x360
https://...
```

---

## 🔧 Estrutura do Script

### **Classe MegaEmbedTester**
```python
class MegaEmbedTester:
    # Métodos principais:
    
    extract_video_id(url)        # Extrai videoId da URL
    test_api_call(video_id)      # Testa API do MegaEmbed
    test_constructed_url(...)    # Testa construção de URL
    validate_m3u8(url)           # Valida M3U8
```

### **Fluxo de Execução**
```
1. extract_video_id()
   ↓
2. test_api_call()
   ├─ API v1
   ├─ Player API (se tem token)
   └─ APIs alternativas
   ↓
3. test_constructed_url() (se API falhar)
   ├─ Testa CDNs conhecidos
   └─ Testa shards conhecidos
   ↓
4. validate_m3u8()
   └─ Verifica se é M3U8 válido
```

---

## 🎓 Comparação: Python vs Kotlin

| Aspecto | Python | Kotlin |
|---------|--------|--------|
| **Velocidade de teste** | ⚡ Instantâneo | 🐌 Minutos (build) |
| **Debugging** | ✅ Fácil (print, breakpoints) | ❌ Difícil (Logcat) |
| **Iteração** | ✅ Rápida | ❌ Lenta |
| **Prototipagem** | ✅ Perfeito | ❌ Ruim |
| **Produto final** | ❌ Não roda no CloudStream | ✅ Plugin nativo |

---

## 🔄 Conversão Python → Kotlin

### **Python:**
```python
response = requests.get(url, headers=headers)
data = response.json()
video_url = data["url"]
```

### **Kotlin:**
```kotlin
val response = app.get(url, headers = headers)
val data = parseJson<JsonNode>(response.text)
val videoUrl = data.get("url").asText()
```

---

## 📝 Próximos Passos

1. **Testar em Python** até funcionar 100%
2. **Documentar** a lógica e padrões descobertos
3. **Converter** para Kotlin usando o código Python como referência
4. **Build** do plugin Kotlin
5. **Testar** no CloudStream

---

## 🎯 Para Seu TCC

Este fluxo Python → Kotlin demonstra:
- ✅ Prototipagem rápida
- ✅ Validação antes de implementação final
- ✅ Debugging eficiente
- ✅ Documentação do processo

**Perfeito para incluir no TCC como metodologia de desenvolvimento!**

---

**Arquivo:** [`test_megaembed.py`](file:///d:/TestPlugins-master/test_megaembed.py)  
**Dependências:** [`requirements.txt`](file:///d:/TestPlugins-master/requirements.txt)
