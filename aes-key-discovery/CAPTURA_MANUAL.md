# 🌐 Guia de Captura Manual de Dados da API

## 📋 Objetivo

Capturar os dados criptografados da API PlayerEmbed usando o DevTools do navegador.

---

## 🚀 Método 1: DevTools do Chrome/Edge (Mais Fácil)

### Passo 1: Abrir DevTools

1. Abra o Chrome ou Edge
2. Pressione `F12` ou `Ctrl+Shift+I`
3. Vá para a aba **Network** (Rede)

### Passo 2: Configurar Filtros

1. Na aba Network, clique em **XHR** ou **Fetch/XHR**
2. Isso filtra apenas requisições AJAX/API

### Passo 3: Acessar o Vídeo

1. Cole a URL no navegador:
   ```
   https://playerembedapi.link/?v=kBJLtxCD3
   ```

2. Pressione Enter

### Passo 4: Capturar a Requisição

1. Observe as requisições aparecendo na aba Network
2. Procure por requisições para:
   - `/api/media`
   - `/api/video`
   - `/api/player`
   - Qualquer endpoint com `api` no caminho

3. Clique na requisição

### Passo 5: Extrair os Dados

1. Clique na aba **Response** (Resposta)
2. Você verá um JSON com os dados
3. Procure pelos campos:
   - `user_id`
   - `slug`
   - `md5_id`
   - `media` (campo criptografado)

### Passo 6: Copiar os Dados

**Opção A: Copiar como JSON**
1. Clique com botão direito na resposta
2. Selecione "Copy" → "Copy response"
3. Cole em um arquivo de texto

**Opção B: Copiar manualmente**
```json
{
  "user_id": "482120",
  "slug": "kBJLtxCD3",
  "md5_id": "28930647",
  "media": "U2FsdGVkX1+abc123..."
}
```

### Passo 7: Testar a Decriptação

1. Abra o arquivo `test_manual_decryption.py`
2. Edite a seção "EDITE AQUI" com os dados copiados
3. Execute:
   ```bash
   python test_manual_decryption.py
   ```

---

## 🔧 Método 2: Console do Navegador (Avançado)

### Passo 1: Abrir Console

1. Pressione `F12`
2. Vá para a aba **Console**

### Passo 2: Interceptar Fetch/XHR

Cole este código no console:

```javascript
// Interceptar fetch
const originalFetch = window.fetch;
window.fetch = function(...args) {
    console.log('🌐 Fetch:', args[0]);
    return originalFetch.apply(this, args).then(response => {
        response.clone().json().then(data => {
            console.log('📄 Response:', data);
            
            // Se tiver os campos que procuramos
            if (data.user_id && data.slug && data.md5_id && data.media) {
                console.log('✅ DADOS ENCONTRADOS!');
                console.log('user_id:', data.user_id);
                console.log('slug:', data.slug);
                console.log('md5_id:', data.md5_id);
                console.log('media:', data.media.substring(0, 50) + '...');
                
                // Salvar no localStorage para fácil acesso
                localStorage.setItem('captured_data', JSON.stringify(data));
                console.log('💾 Dados salvos no localStorage');
            }
        }).catch(() => {});
        return response;
    });
};

// Interceptar XMLHttpRequest
const originalOpen = XMLHttpRequest.prototype.open;
XMLHttpRequest.prototype.open = function(method, url) {
    console.log('🌐 XHR:', method, url);
    this.addEventListener('load', function() {
        try {
            const data = JSON.parse(this.responseText);
            console.log('📄 Response:', data);
            
            if (data.user_id && data.slug && data.md5_id && data.media) {
                console.log('✅ DADOS ENCONTRADOS!');
                localStorage.setItem('captured_data', JSON.stringify(data));
            }
        } catch(e) {}
    });
    return originalOpen.apply(this, arguments);
};

console.log('✅ Interceptadores instalados! Agora carregue o vídeo.');
```

### Passo 3: Carregar o Vídeo

1. Cole a URL na barra de endereços
2. Pressione Enter
3. Observe o console

### Passo 4: Recuperar os Dados

No console, digite:

```javascript
// Recuperar dados salvos
const data = JSON.parse(localStorage.getItem('captured_data'));
console.log(JSON.stringify(data, null, 2));
```

Copie o JSON exibido.

---

## 🔍 Método 3: Burp Suite (Profissional)

### Passo 1: Configurar Burp Suite

1. Abra o Burp Suite
2. Vá para **Proxy** → **Options**
3. Configure o proxy em `127.0.0.1:8080`

### Passo 2: Configurar o Navegador

1. Configure o proxy do navegador:
   - Host: `127.0.0.1`
   - Porta: `8080`

2. Instale o certificado do Burp (para HTTPS)

### Passo 3: Interceptar

1. Vá para **Proxy** → **Intercept**
2. Clique em "Intercept is on"
3. Acesse: `https://playerembedapi.link/?v=kBJLtxCD3`

### Passo 4: Capturar a Resposta

1. Deixe as requisições passarem até encontrar a chamada da API
2. Quando ver `/api/media` ou similar, capture a resposta
3. Copie o JSON da resposta

---

## 📊 Exemplo de Dados Capturados

```json
{
  "user_id": "482120",
  "slug": "kBJLtxCD3",
  "md5_id": "28930647",
  "media": "U2FsdGVkX1+abc123def456ghi789jkl012mno345pqr678stu901vwx234yz..."
}
```

---

## ✅ Validação dos Dados

Após capturar os dados, valide se estão corretos:

### Checklist

- [ ] `user_id` é um número (string)
- [ ] `slug` tem ~9 caracteres alfanuméricos
- [ ] `md5_id` é um número (string)
- [ ] `media` começa com "U2FsdGVk" (base64 de "Salted__")
- [ ] `media` tem pelo menos 100 caracteres

### Teste Rápido

```bash
# Verificar se media está em base64 válido
echo "U2FsdGVkX1..." | base64 -d | head -c 8
# Deve exibir: Salted__
```

---

## 🚀 Próximos Passos

Após capturar os dados:

1. **Editar o script de teste**:
   ```bash
   nano test_manual_decryption.py
   # ou
   notepad test_manual_decryption.py
   ```

2. **Preencher os dados na seção "EDITE AQUI"**:
   ```python
   user_id = "482120"  # Seu valor
   slug = "kBJLtxCD3"  # Seu valor
   md5_id = "28930647"  # Seu valor
   encrypted_media = "U2FsdGVkX1..."  # Seu valor completo
   ```

3. **Executar o teste**:
   ```bash
   python test_manual_decryption.py
   ```

4. **Verificar o resultado**:
   - ✅ Se decriptar com sucesso → Fórmula confirmada!
   - ❌ Se falhar → Tentar outros métodos

---

## 🔧 Troubleshooting

### Problema: Não vejo requisições na aba Network

**Solução**:
1. Certifique-se de que o DevTools está aberto ANTES de carregar a página
2. Limpe o cache: `Ctrl+Shift+Delete`
3. Recarregue a página: `Ctrl+F5`

### Problema: Requisições estão bloqueadas por CORS

**Solução**:
1. Use uma extensão para desabilitar CORS temporariamente
2. Ou use Burp Suite que não tem esse problema

### Problema: Vídeo não carrega

**Solução**:
1. Tente outro vídeo
2. Verifique se o site está online
3. Use um vídeo que você sabe que funciona

### Problema: Campo "media" está vazio

**Solução**:
1. Aguarde mais tempo para a página carregar completamente
2. Verifique se há outras requisições da API
3. Procure por endpoints alternativos

---

## 💡 Dicas

1. **Use o filtro de busca** na aba Network para encontrar rapidamente:
   - Digite: `api`
   - Ou: `media`
   - Ou: `player`

2. **Preserve o log** para não perder requisições:
   - Marque a opção "Preserve log" na aba Network

3. **Desabilite o cache** durante a captura:
   - Marque "Disable cache" na aba Network

4. **Copie como cURL** para reproduzir a requisição:
   - Clique direito na requisição → Copy → Copy as cURL

---

## 📚 Recursos Adicionais

- [Chrome DevTools Network Reference](https://developer.chrome.com/docs/devtools/network/)
- [Burp Suite Documentation](https://portswigger.net/burp/documentation)
- [mitmproxy Documentation](https://docs.mitmproxy.org/)

---

## ⚠️ Notas Importantes

1. **Privacidade**: Não compartilhe dados capturados publicamente
2. **Ética**: Use apenas para fins educacionais e de pesquisa
3. **Legal**: Respeite os termos de serviço do site

---

**Boa sorte na captura! 🚀**
