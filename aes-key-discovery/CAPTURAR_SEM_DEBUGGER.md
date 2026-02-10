# 🎯 CAPTURAR ALGORITMO - Versão Anti-Debug

**O site detectou o DevTools e bloqueou!**  
Vamos usar uma técnica diferente.

---

## 🚀 MÉTODO 1: Desabilitar Debugger (MAIS FÁCIL)

### Passo 1: Abrir Chrome com DevTools Desabilitado

Feche TODOS os Chrome abertos e execute:

**Windows (CMD)**:
```cmd
"C:\Program Files\Google\Chrome\Application\chrome.exe" --disable-blink-features=AutomationControlled --disable-web-security --user-data-dir="C:\temp\chrome_debug"
```

**Windows (PowerShell)**:
```powershell
& "C:\Program Files\Google\Chrome\Application\chrome.exe" --disable-blink-features=AutomationControlled --disable-web-security --user-data-dir="C:\temp\chrome_debug"
```

### Passo 2: Abrir DevTools ANTES da Página

1. Pressione **F12** (DevTools abre em página em branco)
2. Vá para **Console**
3. Cole o código abaixo
4. **SÓ DEPOIS** acesse a URL

### Passo 3: Código Anti-Debug

```javascript
// ============================================================
// CÓDIGO ANTI-DEBUG - Cole ANTES de carregar a página
// ============================================================

// Desabilitar debugger
(function() {
    const noop = () => {};
    window.debugger = noop;
    
    // Sobrescrever Function constructor para ignorar debugger
    const OriginalFunction = Function;
    window.Function = new Proxy(OriginalFunction, {
        construct(target, args) {
            const code = args[args.length - 1];
            if (typeof code === 'string' && code.includes('debugger')) {
                args[args.length - 1] = code.replace(/debugger/g, '');
            }
            return new target(...args);
        }
    });
})();

console.clear();
console.log('%c🎯 ANTI-DEBUG ATIVADO', 'color: green; font-size: 20px; font-weight: bold');
console.log('');

// Armazenar dados capturados
window.algorithmData = {
    key: null,
    algorithm: null,
    decrypted: null,
    rawData: null
};

// Interceptar window.SoTrym
setTimeout(() => {
    const originalSoTrym = window.SoTrym;
    
    window.SoTrym = function(data) {
        console.log('%c🎯 DADOS CAPTURADOS!', 'color: yellow; font-size: 18px; font-weight: bold');
        
        window.algorithmData.rawData = data;
        
        console.log('user_id:', data.user_id);
        console.log('slug:', data.slug);
        console.log('md5_id:', data.md5_id);
        
        const key = `${data.user_id}:${data.slug}:${data.md5_id}`;
        window.algorithmData.key = key;
        
        console.log('%c🔑 CHAVE:', 'color: blue; font-weight: bold', key);
        
        return originalSoTrym ? originalSoTrym.apply(this, arguments) : null;
    };
}, 100);

// Interceptar crypto.subtle.decrypt
setTimeout(() => {
    if (!crypto || !crypto.subtle) return;
    
    const originalDecrypt = crypto.subtle.decrypt;
    
    crypto.subtle.decrypt = function(algorithm, key, data) {
        console.log('%c🔓 ALGORITMO CAPTURADO!', 'color: red; font-size: 18px; font-weight: bold');
        
        window.algorithmData.algorithm = {
            name: algorithm.name,
            ...algorithm
        };
        
        console.log('Algoritmo:', JSON.stringify(algorithm, null, 2));
        console.log('Data length:', data.byteLength);
        
        return originalDecrypt.apply(this, arguments).then(result => {
            console.log('%c✅ DECRIPTADO!', 'color: green; font-size: 18px; font-weight: bold');
            
            try {
                const text = new TextDecoder().decode(result);
                const json = JSON.parse(text);
                
                console.log('Dados:', json);
                window.algorithmData.decrypted = json;
                
                localStorage.setItem('playerembed_algorithm', JSON.stringify({
                    key: window.algorithmData.key,
                    algorithm: window.algorithmData.algorithm,
                    decrypted: json
                }, null, 2));
                
                console.log('%c💾 SALVO!', 'color: green; font-weight: bold');
                console.log('Recuperar: JSON.parse(localStorage.getItem("playerembed_algorithm"))');
                
            } catch(e) {
                console.log('Erro:', e);
            }
            
            return result;
        });
    };
}, 100);

console.log('%c✅ INTERCEPTADORES PRONTOS!', 'color: green; font-size: 16px; font-weight: bold');
console.log('Agora carregue: https://playerembedapi.link/?v=kBJLtxCD3');
```

### Passo 4: Carregar a Página

Na barra de endereços:
```
https://playerembedapi.link/?v=kBJLtxCD3
```

---

## 🚀 MÉTODO 2: Usar Extensão (ALTERNATIVA)

Se o Método 1 não funcionar, use uma extensão do Chrome:

### Instalar "Disable JavaScript Debugger"

1. Abra: `chrome://extensions/`
2. Ative "Modo do desenvolvedor"
3. Procure por "Anti-Debugger" ou use este código:

**Criar extensão manualmente**:

1. Crie uma pasta: `C:\temp\anti-debug-extension`
2. Crie arquivo `manifest.json`:

```json
{
  "manifest_version": 3,
  "name": "Anti-Debugger",
  "version": "1.0",
  "content_scripts": [{
    "matches": ["*://playerembedapi.link/*"],
    "js": ["content.js"],
    "run_at": "document_start"
  }]
}
```

3. Crie arquivo `content.js`:

```javascript
(function() {
    const noop = () => {};
    window.debugger = noop;
    
    const OriginalFunction = Function;
    window.Function = new Proxy(OriginalFunction, {
        construct(target, args) {
            const code = args[args.length - 1];
            if (typeof code === 'string' && code.includes('debugger')) {
                args[args.length - 1] = code.replace(/debugger/g, '');
            }
            return new target(...args);
        }
    });
})();
```

4. Carregue a extensão:
   - Abra `chrome://extensions/`
   - Clique "Carregar sem compactação"
   - Selecione a pasta `C:\temp\anti-debug-extension`

5. Agora use o código de captura normalmente

---

## 🚀 MÉTODO 3: Firefox (SEM PROTEÇÃO)

O Firefox geralmente não tem esse problema:

1. Abra o **Firefox**
2. Pressione **F12**
3. Vá para **Console**
4. Cole o código de captura (versão original)
5. Acesse a URL

---

## 🚀 MÉTODO 4: Captura via Proxy (AVANÇADO)

Use mitmproxy para interceptar:

```bash
# Instalar
pip install mitmproxy

# Executar
mitmweb

# Configurar proxy no navegador: localhost:8080
# Acessar a página
# Ver requisições em http://127.0.0.1:8081
```

---

## 📊 QUAL MÉTODO USAR?

**Mais fácil**: Método 1 (Chrome com flags)  
**Mais confiável**: Método 3 (Firefox)  
**Mais avançado**: Método 4 (Proxy)

---

## ❓ AINDA NÃO FUNCIONOU?

Se nenhum método funcionar, podemos:

1. **Analisar o código JavaScript manualmente** (já temos o lite.bundle.js)
2. **Usar Frida** para hook em runtime
3. **Fazer engenharia reversa** do algoritmo

Mas tente os métodos acima primeiro! Um deles vai funcionar. 🚀

---

**Recomendação**: Tente o **Método 1** primeiro (Chrome com flags). É o mais rápido!

