# 🎯 Guia: Capturar Requisições XHR/Fetch da API

## 📋 Situação Atual

Você capturou logs de rede, mas **não aparecem requisições para `/api/`**.

Isso significa que:
- As requisições da API são feitas via JavaScript (XHR/Fetch)
- Acontecem DEPOIS do carregamento inicial da página
- Precisam ser capturadas especificamente

---

## 🚀 MÉTODO 1: DevTools - Filtro XHR (Mais Fácil)

### Passo a Passo

1. **Abrir DevTools**
   ```
   Pressione F12
   ```

2. **Ir para aba Network**
   ```
   Clique em "Network" (Rede)
   ```

3. **Configurar Filtros**
   ```
   ✅ Marque "Preserve log" (Preservar log)
   ✅ Clique em "XHR" ou "Fetch/XHR"
   ✅ Limpe o log (ícone 🚫)
   ```

4. **Acessar o Vídeo**
   ```
   Cole a URL: https://playerthree.online/episodio/255703
   Pressione Enter
   ```

5. **Aguardar o Player Carregar**
   ```
   Espere o player aparecer na tela
   Aguarde 5-10 segundos
   ```

6. **Procurar Requisições da API**
   ```
   Na lista de requisições XHR, procure por:
   • playerembedapi.link
   • /api/
   • /media
   • /video
   • /player
   ```

7. **Capturar os Dados**
   ```
   Clique na requisição
   Vá para aba "Response"
   Copie o JSON completo
   ```

---

## 🔍 MÉTODO 2: Console - Interceptação JavaScript

### Código para Colar no Console

Abra o Console (F12 → Console) e cole este código **ANTES** de carregar a página:

```javascript
// ============================================================
// INTERCEPTADOR DE REQUISIÇÕES - Cole no Console
// ============================================================

console.clear();
console.log('%c🔍 INTERCEPTADOR ATIVADO', 'color: green; font-size: 20px; font-weight: bold');
console.log('Aguardando requisições da API...\n');

// Interceptar fetch
const originalFetch = window.fetch;
window.fetch = function(...args) {
    const url = args[0];
    console.log('%c📡 FETCH:', 'color: blue; font-weight: bold', url);
    
    return originalFetch.apply(this, args).then(response => {
        // Clonar para não consumir o response original
        response.clone().text().then(text => {
            try {
                const data = JSON.parse(text);
                
                // Verificar se é a API que procuramos
                if (url.includes('api') || url.includes('player') || url.includes('media')) {
                    console.log('%c✅ POSSÍVEL API ENCONTRADA!', 'color: green; font-size: 16px; font-weight: bold');
                    console.log('URL:', url);
                    console.log('Dados:', data);
                    
                    // Verificar se tem os campos necessários
                    if (data.user_id && data.slug && data.md5_id && data.media) {
                        console.log('%c🎯 JACKPOT! DADOS COMPLETOS ENCONTRADOS!', 'color: red; font-size: 20px; font-weight: bold');
                        console.log('user_id:', data.user_id);
                        console.log('slug:', data.slug);
                        console.log('md5_id:', data.md5_id);
                        console.log('media:', data.media.substring(0, 50) + '...');
                        
                        // Salvar no localStorage
                        localStorage.setItem('api_data_captured', JSON.stringify(data));
                        console.log('💾 Dados salvos no localStorage!');
                        console.log('Para recuperar: JSON.parse(localStorage.getItem("api_data_captured"))');
                    }
                }
                
                console.log('Response:', data);
            } catch(e) {
                // Não é JSON, ignorar
            }
        }).catch(() => {});
        
        return response;
    });
};

// Interceptar XMLHttpRequest
const originalOpen = XMLHttpRequest.prototype.open;
const originalSend = XMLHttpRequest.prototype.send;

XMLHttpRequest.prototype.open = function(method, url) {
    this._url = url;
    this._method = method;
    console.log('%c📡 XHR:', 'color: purple; font-weight: bold', method, url);
    return originalOpen.apply(this, arguments);
};

XMLHttpRequest.prototype.send = function() {
    this.addEventListener('load', function() {
        try {
            const data = JSON.parse(this.responseText);
            const url = this._url;
            
            if (url.includes('api') || url.includes('player') || url.includes('media')) {
                console.log('%c✅ POSSÍVEL API ENCONTRADA!', 'color: green; font-size: 16px; font-weight: bold');
                console.log('URL:', url);
                console.log('Dados:', data);
                
                if (data.user_id && data.slug && data.md5_id && data.media) {
                    console.log('%c🎯 JACKPOT! DADOS COMPLETOS ENCONTRADOS!', 'color: red; font-size: 20px; font-weight: bold');
                    console.log('user_id:', data.user_id);
                    console.log('slug:', data.slug);
                    console.log('md5_id:', data.md5_id);
                    console.log('media:', data.media.substring(0, 50) + '...');
                    
                    localStorage.setItem('api_data_captured', JSON.stringify(data));
                    console.log('💾 Dados salvos no localStorage!');
                }
            }
            
            console.log('Response:', data);
        } catch(e) {}
    });
    return originalSend.apply(this, arguments);
};

console.log('%c✅ Interceptadores instalados!', 'color: green; font-size: 16px');
console.log('Agora carregue o vídeo e observe as requisições...\n');
```

### Como Usar

1. Abra o Console (F12 → Console)
2. Cole o código acima
3. Pressione Enter
4. Carregue a página do vídeo
5. Aguarde as mensagens no console
6. Quando aparecer "JACKPOT!", os dados foram capturados!

### Recuperar os Dados Salvos

No console, digite:

```javascript
// Recuperar dados
const data = JSON.parse(localStorage.getItem('api_data_captured'));
console.log(JSON.stringify(data, null, 2));

// Copiar para clipboard (se disponível)
copy(JSON.stringify(data, null, 2));
```

---

## 🎬 MÉTODO 3: Usar o Episódio Específico

Você está acessando: `https://playerthree.online/episodio/255703`

### Teste Direto

1. Abra o navegador
2. Abra DevTools (F12)
3. Vá para Network → XHR
4. Acesse: https://playerthree.online/episodio/255703
5. Aguarde o player carregar
6. Procure por requisições XHR

### URLs Possíveis da API

Baseado no episódio 255703, teste estas URLs:

```bash
# Possível endpoint 1
curl "https://playerembedapi.link/api/media?id=255703"

# Possível endpoint 2
curl "https://playerembedapi.link/api/video?id=255703"

# Possível endpoint 3
curl "https://playerembedapi.link/api/player?id=255703"

# Possível endpoint 4
curl "https://playerthree.online/api/episodio/255703"
```

---

## 📊 O Que Você Deve Ver

### Exemplo de Requisição XHR Correta

```
Name: media?v=kBJLtxCD3
Type: xhr
Status: 200
Size: 2.5 KB
```

### Exemplo de Response

```json
{
  "user_id": "482120",
  "slug": "kBJLtxCD3",
  "md5_id": "28930647",
  "media": "U2FsdGVkX1+abc123def456..."
}
```

---

## ✅ Checklist de Captura

- [ ] DevTools aberto ANTES de carregar a página
- [ ] Filtro XHR ativado
- [ ] "Preserve log" marcado
- [ ] Página carregada completamente
- [ ] Player apareceu na tela
- [ ] Aguardou 5-10 segundos
- [ ] Procurou por requisições com "api" no nome
- [ ] Verificou a aba Response de cada requisição
- [ ] Copiou o JSON completo

---

## 🚨 Troubleshooting

### Não vejo nenhuma requisição XHR

**Possíveis causas:**
1. DevTools não estava aberto antes de carregar
2. Filtro XHR não está ativado
3. API usa WebSocket em vez de XHR/Fetch
4. Dados estão embutidos na página HTML

**Soluções:**
1. Recarregue a página com DevTools aberto
2. Verifique a aba "WS" (WebSocket)
3. Use o interceptador JavaScript (Método 2)
4. Inspecione o código-fonte da página

### Vejo requisições mas não para /api/

**Possíveis causas:**
1. API usa endpoint diferente
2. Dados vêm de outro domínio
3. API usa GraphQL ou outro formato

**Soluções:**
1. Procure por requisições para outros domínios
2. Verifique requisições POST
3. Use o interceptador JavaScript que captura TUDO

### Requisições aparecem mas Response está vazio

**Possíveis causas:**
1. Response é binário (não JSON)
2. Response é muito grande
3. CORS bloqueou a visualização

**Soluções:**
1. Verifique o tamanho do response
2. Use "Copy as cURL" e execute no terminal
3. Use Burp Suite para interceptar

---

## 🎯 Próximo Passo Após Capturar

Quando você capturar os dados:

1. **Copie o JSON completo**
2. **Abra**: `test_manual_decryption.py`
3. **Edite a seção "EDITE AQUI"**:
   ```python
   user_id = "SEU_VALOR"
   slug = "SEU_VALOR"
   md5_id = "SEU_VALOR"
   encrypted_media = "SEU_VALOR_COMPLETO"
   ```
4. **Execute**:
   ```bash
   python test_manual_decryption.py
   ```

---

## 💡 Dica Final

Se você não conseguir capturar com DevTools, use o **Método 2 (Interceptador JavaScript)**.

Ele captura TODAS as requisições, independente de como são feitas, e salva automaticamente no localStorage.

**É o método mais confiável!**

---

**Boa sorte! 🚀**
