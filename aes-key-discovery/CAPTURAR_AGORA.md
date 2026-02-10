# 🎯 CAPTURAR ALGORITMO AGORA - Guia Passo a Passo

**Tempo estimado**: 5 minutos  
**Dificuldade**: Fácil  
**O que você vai obter**: Algoritmo completo de decriptação + dados do vídeo

---

## 📋 PASSO A PASSO

### 1️⃣ Abrir o Chrome

- Abra o navegador Chrome ou Edge
- Não precisa fechar outras abas

### 2️⃣ Abrir DevTools

- Pressione **F12** (ou Ctrl+Shift+I)
- Clique na aba **Console** (no topo do DevTools)

### 3️⃣ Colar o Código de Interceptação

Cole este código completo no console e pressione **Enter**:

```javascript
// ============================================================
// CÓDIGO DE CAPTURA - Cole tudo de uma vez
// ============================================================

console.clear();
console.log('%c🎯 INICIANDO CAPTURA DO ALGORITMO', 'color: green; font-size: 20px; font-weight: bold');
console.log('');

// Armazenar dados capturados
window.algorithmData = {
    key: null,
    algorithm: null,
    decrypted: null,
    rawData: null
};

// Interceptar window.SoTrym
(function() {
    const originalSoTrym = window.SoTrym;
    
    window.SoTrym = function(data) {
        console.log('%c━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'color: cyan');
        console.log('%c🎯 DADOS RECEBIDOS', 'color: yellow; font-size: 16px; font-weight: bold');
        console.log('%c━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'color: cyan');
        
        window.algorithmData.rawData = data;
        
        console.log('user_id:', data.user_id);
        console.log('slug:', data.slug);
        console.log('md5_id:', data.md5_id);
        
        // Gerar chave
        const key = `${data.user_id}:${data.slug}:${data.md5_id}`;
        window.algorithmData.key = key;
        
        console.log('');
        console.log('%c🔑 CHAVE GERADA:', 'color: blue; font-size: 14px; font-weight: bold');
        console.log('%c' + key, 'color: lime; font-size: 16px; font-weight: bold');
        console.log('');
        
        // Chamar função original
        const result = originalSoTrym ? originalSoTrym.apply(this, arguments) : null;
        return result;
    };
})();

// Interceptar crypto.subtle.importKey
(function() {
    if (!crypto || !crypto.subtle) return;
    
    const originalImportKey = crypto.subtle.importKey;
    
    crypto.subtle.importKey = function(format, keyData, algorithm, extractable, keyUsages) {
        console.log('%c━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'color: cyan');
        console.log('%c🔑 IMPORTANDO CHAVE', 'color: orange; font-size: 16px; font-weight: bold');
        console.log('%c━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'color: cyan');
        
        console.log('Format:', format);
        console.log('Algorithm:', algorithm);
        console.log('Extractable:', extractable);
        console.log('Key usages:', keyUsages);
        
        // Tentar extrair a chave
        try {
            if (keyData.byteLength) {
                const keyArray = new Uint8Array(keyData);
                const keyHex = Array.from(keyArray).map(b => b.toString(16).padStart(2, '0')).join('');
                console.log('Key (hex):', keyHex.substring(0, 64) + '...');
                console.log('Key length:', keyArray.length, 'bytes');
            }
        } catch(e) {}
        
        console.log('');
        
        return originalImportKey.apply(this, arguments);
    };
})();

// Interceptar crypto.subtle.decrypt
(function() {
    if (!crypto || !crypto.subtle) return;
    
    const originalDecrypt = crypto.subtle.decrypt;
    
    crypto.subtle.decrypt = function(algorithm, key, data) {
        console.log('%c━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'color: cyan');
        console.log('%c🔓 ALGORITMO DE DECRIPTAÇÃO CAPTURADO!', 'color: red; font-size: 18px; font-weight: bold');
        console.log('%c━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'color: cyan');
        
        // Salvar algoritmo
        window.algorithmData.algorithm = {
            name: algorithm.name,
            ...algorithm
        };
        
        console.log('%cAlgoritmo:', 'font-weight: bold');
        console.log(JSON.stringify(algorithm, null, 2));
        console.log('');
        console.log('Data length:', data.byteLength, 'bytes');
        console.log('');
        
        return originalDecrypt.apply(this, arguments).then(result => {
            console.log('%c━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'color: cyan');
            console.log('%c✅ DECRIPTAÇÃO BEM-SUCEDIDA!', 'color: green; font-size: 18px; font-weight: bold');
            console.log('%c━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'color: cyan');
            
            console.log('Result length:', result.byteLength, 'bytes');
            console.log('');
            
            try {
                const text = new TextDecoder().decode(result);
                
                console.log('%c📄 DADOS DECRIPTADOS:', 'color: blue; font-size: 14px; font-weight: bold');
                console.log('');
                
                // Tentar parsear como JSON
                try {
                    const json = JSON.parse(text);
                    console.log(JSON.stringify(json, null, 2));
                    
                    window.algorithmData.decrypted = json;
                    
                    // Salvar no localStorage
                    localStorage.setItem('playerembed_algorithm', JSON.stringify({
                        key: window.algorithmData.key,
                        algorithm: window.algorithmData.algorithm,
                        decrypted: json,
                        timestamp: new Date().toISOString()
                    }, null, 2));
                    
                    console.log('');
                    console.log('%c━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'color: cyan');
                    console.log('%c💾 DADOS SALVOS NO LOCALSTORAGE!', 'color: green; font-size: 16px; font-weight: bold');
                    console.log('%c━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'color: cyan');
                    console.log('');
                    console.log('Para recuperar:');
                    console.log('%cJSON.parse(localStorage.getItem("playerembed_algorithm"))', 'color: yellow; background: black; padding: 5px;');
                    console.log('');
                    
                } catch(e) {
                    console.log(text.substring(0, 500));
                    window.algorithmData.decrypted = text;
                }
            } catch(e) {
                console.log('Erro ao decodificar:', e);
            }
            
            return result;
        }).catch(error => {
            console.error('%c❌ ERRO NA DECRIPTAÇÃO:', 'color: red; font-weight: bold', error);
            throw error;
        });
    };
})();

console.log('%c✅ INTERCEPTADORES INSTALADOS!', 'color: green; font-size: 16px; font-weight: bold');
console.log('');
console.log('%cAgora carregue a página do vídeo...', 'color: yellow; font-size: 14px;');
console.log('%cURL: https://playerembedapi.link/?v=kBJLtxCD3', 'color: cyan;');
console.log('');
```

### 4️⃣ Carregar a Página do Vídeo

Na barra de endereços do navegador, cole:

```
https://playerembedapi.link/?v=kBJLtxCD3
```

Pressione **Enter** e aguarde 5-10 segundos.

### 5️⃣ Ver os Resultados

Você verá mensagens coloridas no console mostrando:

- ✅ **CHAVE GERADA**: `482120:kBJLtxCD3:28930647`
- ✅ **ALGORITMO CAPTURADO**: Nome e parâmetros do algoritmo
- ✅ **DADOS DECRIPTADOS**: JSON com URLs do vídeo

### 6️⃣ Copiar os Dados

No console, digite:

```javascript
copy(JSON.parse(localStorage.getItem('playerembed_algorithm')))
```

Pressione **Enter**. Os dados foram copiados para a área de transferência!

### 7️⃣ Salvar os Dados

Cole os dados em um arquivo de texto ou me envie aqui para análise.

---

## 📊 O QUE VOCÊ VAI VER

### Exemplo de Saída:

```
🎯 DADOS RECEBIDOS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
user_id: 482120
slug: kBJLtxCD3
md5_id: 28930647

🔑 CHAVE GERADA:
482120:kBJLtxCD3:28930647

🔓 ALGORITMO DE DECRIPTAÇÃO CAPTURADO!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Algoritmo:
{
  "name": "AES-CTR",
  "counter": {...},
  "length": 128
}

✅ DECRIPTAÇÃO BEM-SUCEDIDA!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📄 DADOS DECRIPTADOS:
{
  "title": "Land of Sin S01E01",
  "sources": [
    {
      "file": "https://...",
      "label": "1080p"
    }
  ]
}

💾 DADOS SALVOS NO LOCALSTORAGE!
```

---

## ❓ PROBLEMAS COMUNS

### Nada apareceu no console

**Solução**: 
1. Recarregue a página (F5)
2. Aguarde mais 10 segundos
3. Verifique se está na aba Console do DevTools

### Erro "SoTrym is not defined"

**Solução**: 
1. Cole o código ANTES de carregar a página
2. Ou recarregue a página depois de colar o código

### Página não carrega

**Solução**:
1. Verifique sua conexão com a internet
2. Tente outro vídeo: `https://playerembedapi.link/?v=QvXFt2de3`

---

## 🎯 PRÓXIMO PASSO

Depois de capturar os dados:

1. **Me envie o resultado** (cole aqui no chat)
2. Ou salve em: `aes-key-discovery/output/algorithm_captured.json`
3. Vou analisar e criar o código de decriptação para o plugin

---

## 💡 DICA

Se preferir, posso criar um script automatizado que faz tudo isso para você. Mas o método manual é mais rápido e confiável para a primeira vez.

---

**Pronto para começar? Cole o código no console e carregue a página!** 🚀

