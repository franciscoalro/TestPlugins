# PlayerEmbedAPI v5.0 - Teste Python

Script de teste em Python para validar as estratégias de extração do PlayerEmbedAPI antes de implementar em Kotlin.

## 📋 Instalação

```bash
cd "C:\Users\KYTHOURS\Desktop\brcloudstream"

# Instalar dependências
pip install -r test_requirements.txt

# Ou instalar manualmente
pip install requests pycryptodome beautifulsoup4 lxml
```

## 🚀 Uso

```bash
python test_playerembedapi_v5.py "<URL_DO_PLAYEREMBEDAPI>"
```

### Exemplo:

```bash
python test_playerembedapi_v5.py "https://playerembedapi.link/?v=abc123"
```

## 🎯 Estratégias Testadas

O script testa 4 estratégias em ordem:

### 1. API (base64 + AES-CTR)
- Extrai dados criptografados do HTML
- Decodifica base64
- Decripta usando AES-CTR
- Extrai URLs do JSON decriptado

### 2. ShortIcu
- Extrai iframe short.icu do HTML
- Acessa a URL do short.icu
- Extrai vídeo direto do Google Cloud Storage

### 3. Regex direto no HTML
- Procura por URLs de vídeo no HTML original
- Padrões: Google Storage, SSSRR CDN, JWPlayer

### 4. WebView (simulado)
- Simula navegador com headers completos
- Último recurso quando outras falham

## 📊 Interpretação dos Resultados

### ✅ Sucesso
```
[12:34:56] ✅ URL encontrada em sources: https://storage.googleapis.com/...
```

### ⚠️ Aviso
```
[12:34:56] ⚠️  Não encontrou base64 'datas'
```

### ❌ Erro
```
[12:34:56] ❌ Erro na decriptação: ...
```

## 🔍 Debugging

Para ver mais detalhes, edite o script e altere:

```python
# Adicione logs adicionais
self.log(f"HTML completo: {html[:500]}...")
```

## 🔄 Comparação com Kotlin

| Feature | Python | Kotlin |
|---------|--------|--------|
| AES-CTR | pycryptodome | javax.crypto |
| Requests | requests | okhttp |
| Regex | re | kotlin.text.Regex |
| JSON | json | kotlinx.serialization |
| WebView | Simulado | WebView real |

## 📝 Notas

- O script **não** baixa o vídeo, apenas extrai a URL
- A estratégia 1 (API) requer `pycryptodome`
- A estratégia 4 (WebView) é simulada - no Android usa WebView real
- URLs de teste podem expirar rapidamente

## 🛡️ Segurança

- Não loga chaves criptográficas completas
- Valida URLs antes de retornar
- Verifica domínios permitidos
