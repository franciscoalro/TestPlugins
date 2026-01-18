# 🔑 Guia: Como Capturar a Chave do MegaEmbed

## 📋 Passo a Passo Completo

### Passo 1: Abrir o Player MegaEmbed

1. Abra o **Google Chrome** ou **Microsoft Edge**
2. Vá para: https://megaembed.link/#3wnuij
   - Ou use qualquer outro video ID do MegaEmbed
   - Exemplo: https://megaembed.link/#xez5rx

### Passo 2: Abrir o DevTools

**Opção A - Atalho de Teclado**:
- Pressione **F12**
- Ou pressione **Ctrl + Shift + I** (Windows/Linux)
- Ou pressione **Cmd + Option + I** (Mac)

**Opção B - Menu**:
1. Clique nos 3 pontinhos no canto superior direito
2. Mais ferramentas → Ferramentas do desenvolvedor

### Passo 3: Ir para a Aba Console

1. No DevTools, clique na aba **Console**
2. Você verá uma linha de comando com `>`

### Passo 4: Colar o Script

**⚠️ AVISO DE SEGURANÇA DO CHROME**

Quando você tentar colar, o Chrome vai mostrar:
```
Warning: Don't paste code into the DevTools Console that you don't understand 
or haven't reviewed yourself. This could allow attackers to steal your identity 
or take control of your computer. Please type 'allow pasting' below and hit 
Enter to allow pasting.
```

**Isso é NORMAL e SEGURO neste caso** porque:
1. ✅ Você criou o script (está no seu computador)
2. ✅ Você pode revisar o código antes de usar
3. ✅ O script só intercepta dados, não envia nada para fora
4. ✅ É só para análise local

**Como proceder**:

1. **Digite** no Console: `allow pasting` (sem aspas)
2. **Pressione Enter**
3. Agora você pode colar normalmente:
   - Abra o arquivo `capture-megaembed-key-devtools.js`
   - **Copie TODO o conteúdo** (Ctrl+A, Ctrl+C)
   - **Cole no Console** (Ctrl+V)
   - **Pressione Enter**

Você verá:
```
🔓 MEGAEMBED KEY CAPTURER - INICIADO
================================================================================
✅ Interceptors instalados!
📝 Agora recarregue a página (F5) e aguarde o vídeo carregar
```

### Passo 5: Recarregar a Página

1. Pressione **F5** para recarregar a página
2. Aguarde o player carregar (pode demorar 5-10 segundos)
3. O vídeo vai começar a carregar

### Passo 6: Ver os Dados Capturados

Quando o vídeo carregar, você verá no Console:

```
🌐 FETCH /api/v1/player DETECTADO:
   URL: https://megaembed.link/api/v1/player?t=3772aacf...
   🎫 Token: 3772aacff2bd31142eec3d5b0f291f4e...
   🎫 Token Length: 480 chars

🔑 crypto.subtle.importKey() CHAMADO:
   Format: raw
   Algorithm: {name: "AES-CBC"}
   📦 Key Data (hex): a1b2c3d4e5f6789012345678abcdef01
   📦 Key Length: 16 bytes
   ✅ Chave salva em localStorage.megaembed_key_hex

🔓 crypto.subtle.decrypt() CHAMADO:
   Algorithm: {name: "AES-CBC", iv: ArrayBuffer}
   🔢 IV (hex): 0123456789abcdef0123456789abcdef
   🔢 IV Length: 16 bytes
   ✅ IV salvo em localStorage.megaembed_iv_hex
   
   ✅ Decrypted Data Length: 150 bytes
   ✅ Decrypted Data (text): {"url":"https://srcf.marvellaholdings.sbs/..."}
   🎯 É JSON! Chaves: ['url']
   🎯 JSON completo: {
     "url": "https://srcf.marvellaholdings.sbs/v4/x6b/3wnuij/cf-master.1767386783.txt"
   }
   
   🎬 URL DO VÍDEO ENCONTRADA:
      https://srcf.marvellaholdings.sbs/v4/x6b/3wnuij/cf-master.1767386783.txt
```

### Passo 7: Copiar os Dados

**Opção A - Do Console**:
Copie diretamente do console:
- **Chave**: O valor em `📦 Key Data (hex):`
- **IV**: O valor em `🔢 IV (hex):`
- **URL do Vídeo**: O valor em `🎬 URL DO VÍDEO ENCONTRADA:`

**Opção B - Do localStorage**:
No Console, digite:
```javascript
// Ver a chave
localStorage.getItem("megaembed_key_hex")

// Ver o IV
localStorage.getItem("megaembed_iv_hex")

// Ver o token
localStorage.getItem("megaembed_token")

// Ver a URL do vídeo
localStorage.getItem("megaembed_video_url")

// Ver o JSON completo
localStorage.getItem("megaembed_decrypted_json")
```

### Passo 8: Testar a URL do Vídeo

1. Copie a URL do vídeo (termina com `.txt`)
2. Cole no navegador ou no VLC
3. O vídeo deve reproduzir!

Exemplo:
```
https://srcf.marvellaholdings.sbs/v4/x6b/3wnuij/cf-master.1767386783.txt
```

## 🎯 Exemplo Completo

### Dados Capturados:
```
Chave (hex):  a1b2c3d4e5f6789012345678abcdef01
IV (hex):     0123456789abcdef0123456789abcdef
Token:        3772aacff2bd31142eec3d5b0f291f4e...
URL do Vídeo: https://srcf.marvellaholdings.sbs/v4/x6b/3wnuij/cf-master.1767386783.txt
```

### Usar no Python:
```python
import binascii
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

# Dados capturados
key_hex = "a1b2c3d4e5f6789012345678abcdef01"
iv_hex = "0123456789abcdef0123456789abcdef"
encrypted_hex = "933a30ecdabc15152bfbe068bc27d534..."  # Do Burp Suite

# Converter para bytes
key = binascii.unhexlify(key_hex)
iv = binascii.unhexlify(iv_hex)
encrypted_data = binascii.unhexlify(encrypted_hex)

# Descriptografar
cipher = AES.new(key, AES.MODE_CBC, iv)
decrypted = cipher.decrypt(encrypted_data)
unpadded = unpad(decrypted, AES.block_size)

# Ver resultado
print(unpadded.decode('utf-8'))
# Output: {"url": "https://srcf.marvellaholdings.sbs/..."}
```

## 🔧 Troubleshooting

### Problema 1: Chrome pede "allow pasting"
**Solução**:
1. Isso é um aviso de segurança normal do Chrome
2. Digite: `allow pasting` (sem aspas)
3. Pressione Enter
4. Agora cole o script normalmente

### Problema 2: Nada aparece no Console
**Solução**:
1. Verifique se colou o script ANTES de recarregar
2. Recarregue a página novamente (F5)
3. Aguarde o vídeo carregar completamente

### Problema 2: Erro "crypto is not defined"
**Solução**:
1. Use HTTPS (não HTTP)
2. Use Chrome ou Edge (não Firefox antigo)
3. Desative extensões que bloqueiam JavaScript

### Problema 3: Vídeo não carrega
**Solução**:
1. Tente outro video ID
2. Verifique se o site está online
3. Desative AdBlock temporariamente

### Problema 4: URL do vídeo não funciona
**Solução**:
1. A URL expira após alguns minutos
2. Capture novamente com um vídeo novo
3. Use a URL imediatamente após capturar

## 🔒 Segurança do Script

### Por Que o Chrome Mostra o Aviso?

O Chrome mostra esse aviso para **proteger você** de scripts maliciosos. É uma boa prática de segurança!

### Por Que Este Script é Seguro?

1. ✅ **Código Aberto**: Você pode ler todo o código em `capture-megaembed-key-devtools.js`
2. ✅ **Local**: O script roda apenas no seu browser, não envia dados para nenhum servidor
3. ✅ **Interceptação**: Só intercepta chamadas de crypto para mostrar no console
4. ✅ **Sem Modificação**: Não modifica o comportamento do site
5. ✅ **Sem Rede**: Não faz requisições HTTP para servidores externos

### O Que o Script Faz?

```javascript
// 1. Intercepta crypto.subtle.importKey para ver a chave
const originalImportKey = crypto.subtle.importKey;
crypto.subtle.importKey = function(...args) {
  console.log('🔑 CHAVE:', args[1]);  // Mostra a chave
  return originalImportKey.apply(this, args);  // Chama a função original
};

// 2. Intercepta crypto.subtle.decrypt para ver o IV
const originalDecrypt = crypto.subtle.decrypt;
crypto.subtle.decrypt = function(...args) {
  console.log('🔢 IV:', args[0].iv);  // Mostra o IV
  return originalDecrypt.apply(this, args);  // Chama a função original
};

// 3. Salva no localStorage para fácil acesso
localStorage.setItem('megaembed_key_hex', keyHex);
```

### Como Verificar o Script?

Antes de usar, você pode:
1. Abrir `capture-megaembed-key-devtools.js` em um editor de texto
2. Ler o código linha por linha
3. Verificar que não há:
   - `fetch()` para servidores externos
   - `XMLHttpRequest` para enviar dados
   - `eval()` ou código ofuscado
   - Modificações permanentes no browser

### Alternativa Mais Segura

Se ainda tiver dúvidas, você pode:
1. Usar apenas as primeiras linhas do script (interceptação básica)
2. Não salvar no localStorage (comentar essas linhas)
3. Usar o DevTools Network tab para ver as requisições manualmente

## 📝 Notas Importantes

### ⚠️ Limitações:
1. **Chave muda**: Cada sessão gera uma chave diferente
2. **URL expira**: A URL do vídeo expira após ~5-10 minutos
3. **Manual**: Precisa fazer isso para cada vídeo
4. **Não automatizável**: Não dá para fazer isso em um script

### ✅ Vantagens:
1. **100% funcional**: Sempre captura a chave correta
2. **Simples**: Só precisa do Chrome e do script
3. **Rápido**: Leva menos de 1 minuto
4. **Educativo**: Mostra exatamente como funciona

### 💡 Uso Prático:
- **Para testar**: Confirmar que conseguimos descriptografar
- **Para debug**: Entender o fluxo do MegaEmbed
- **Para análise**: Ver como a API funciona
- **NÃO para produção**: Use WebView no CloudStream

## 🎓 O Que Você Vai Aprender

Ao fazer isso, você vai entender:
1. Como o MegaEmbed gera chaves aleatórias
2. Como interceptar chamadas de crypto no browser
3. Como funciona AES-CBC na prática
4. Por que é impossível fazer reverse engineering completo

## 📚 Próximos Passos

Depois de capturar a chave:

### Se quiser testar a descriptografia:
1. Use o script `decrypt-megaembed-response.py`
2. Substitua a chave e IV pelos valores capturados
3. Execute: `python decrypt-megaembed-response.py`

### Se quiser implementar no CloudStream:
1. Leia `MEGAEMBED_PROXIMOS_PASSOS.md`
2. Veja a Opção 2 (WebView)
3. Implemente o extractor com WebView

### Se quiser entender mais:
1. Leia `MEGAEMBED_REVERSE_ENGINEERING_FINAL.md`
2. Veja `MEGAEMBED_BURP_ANALYSIS.md`
3. Estude o código em `megaembed_index.js`

## 🔗 Arquivos Relacionados

- **Script**: `capture-megaembed-key-devtools.js`
- **Guia de Implementação**: `MEGAEMBED_PROXIMOS_PASSOS.md`
- **Análise Completa**: `MEGAEMBED_REVERSE_ENGINEERING_FINAL.md`
- **Dados do Burp Suite**: `sniffer_results.json`

## ❓ Dúvidas Frequentes

**P: Posso automatizar isso?**
R: Não. A chave é gerada no browser, precisa de interação manual. Use WebView para automatizar.

**P: A chave funciona para outros vídeos?**
R: Não. Cada vídeo/sessão gera uma chave diferente.

**P: Quanto tempo a URL do vídeo funciona?**
R: Aproximadamente 5-10 minutos. Depois expira.

**P: Posso usar isso em produção?**
R: Não. É só para testes. Use WebView no CloudStream.

**P: Funciona no Firefox?**
R: Sim, mas o script pode precisar de ajustes. Chrome é recomendado.

**P: Preciso do Burp Suite?**
R: Não. O script captura tudo no browser. Burp Suite foi só para análise inicial.

## ✅ Checklist

Antes de começar:
- [ ] Chrome ou Edge instalado
- [ ] Arquivo `capture-megaembed-key-devtools.js` aberto
- [ ] Internet funcionando
- [ ] AdBlock desativado (opcional)

Durante a captura:
- [ ] DevTools aberto (F12)
- [ ] Aba Console selecionada
- [ ] Script colado e executado
- [ ] Página recarregada (F5)
- [ ] Vídeo carregando

Após capturar:
- [ ] Chave copiada
- [ ] IV copiado
- [ ] URL do vídeo copiada
- [ ] URL testada no browser/VLC

## 🎉 Pronto!

Agora você sabe como capturar a chave do MegaEmbed!

Se tiver dúvidas, consulte:
- `MEGAEMBED_REVERSE_ENGINEERING_FINAL.md` - Explicação técnica
- `MEGAEMBED_PROXIMOS_PASSOS.md` - Próximos passos
- `MEGAEMBED_BURP_ANALYSIS.md` - Análise do Burp Suite
