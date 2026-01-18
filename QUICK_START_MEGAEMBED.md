# 🚀 Quick Start: Capturar Chave do MegaEmbed

## ⚡ 5 Passos Rápidos

### 1️⃣ Abrir o Player
```
https://megaembed.link/#3wnuij
```
Cole no Chrome e pressione Enter

### 2️⃣ Abrir DevTools
Pressione **F12**

### 3️⃣ Ir para Console
Clique na aba **Console**

### 4️⃣ Colar o Script

**⚠️ IMPORTANTE**: O Chrome vai mostrar um aviso de segurança:
```
Warning: Don't paste code into the DevTools Console...
Please type 'allow pasting' below and hit Enter to allow pasting.
```

**Isso é normal!** Siga estes passos:

1. Digite: `allow pasting` (sem aspas)
2. Pressione Enter
3. Agora você pode colar o script:
   - Abra: `capture-megaembed-key-devtools.js`
   - Copie TUDO (Ctrl+A, Ctrl+C)
   - Cole no Console (Ctrl+V)
   - Pressione Enter

Você verá:
```
✅ Interceptors instalados!
📝 Agora recarregue a página (F5)
```

### 5️⃣ Recarregar e Aguardar
1. Pressione **F5**
2. Aguarde o vídeo carregar
3. Veja os dados aparecerem no Console!

## 📊 Resultado Esperado

```
🔑 crypto.subtle.importKey() CHAMADO:
   📦 Key Data (hex): a1b2c3d4e5f6789012345678abcdef01
   📦 Key Length: 16 bytes

🔓 crypto.subtle.decrypt() CHAMADO:
   🔢 IV (hex): 0123456789abcdef0123456789abcdef
   
   🎬 URL DO VÍDEO ENCONTRADA:
      https://srcf.marvellaholdings.sbs/v4/x6b/3wnuij/cf-master.txt
```

## 💾 Copiar os Dados

No Console, digite:
```javascript
localStorage.getItem("megaembed_key_hex")      // Chave
localStorage.getItem("megaembed_iv_hex")       // IV
localStorage.getItem("megaembed_video_url")    // URL do vídeo
```

## ✅ Testar

Cole a URL do vídeo no navegador:
```
https://srcf.marvellaholdings.sbs/v4/x6b/3wnuij/cf-master.txt
```

O vídeo deve reproduzir! 🎉

## 🔧 Problemas?

**Nada aparece?**
- Recarregue a página (F5) novamente
- Aguarde mais tempo (10-15 segundos)

**Erro no Console?**
- Verifique se colou o script completo
- Use Chrome (não Firefox)

**URL não funciona?**
- A URL expira em 5-10 minutos
- Capture novamente

## 📚 Guia Completo

Para mais detalhes, veja:
- `GUIA_CAPTURAR_CHAVE_MEGAEMBED.md` - Guia passo a passo detalhado
- `capture-megaembed-key-devtools.js` - O script completo
- `MEGAEMBED_REVERSE_ENGINEERING_FINAL.md` - Explicação técnica

## 🎯 Próximos Passos

Depois de capturar:
1. ✅ Confirme que conseguiu a chave e URL
2. 📖 Leia `MEGAEMBED_PROXIMOS_PASSOS.md`
3. 🔨 Decida se vai implementar (não recomendado)

---

**Tempo total**: ~2 minutos ⏱️
**Dificuldade**: Fácil 🟢
**Requer**: Chrome + Script 🌐
