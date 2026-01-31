# 🔍 VERIFICAÇÃO DE LOGS - PlayerEmbedAPI v5.0

## ⚡ MÉTODO RÁPIDO (Recomendado)

### Passo 1: Conectar Dispositivo
```powershell
# Verificar se ADB está instalado
adb devices

# Deve mostrar algo como:
# List of devices attached
# xxxxxxxx    device
```

### Passo 2: Capturar Logs
```powershell
# No PowerShell, execute:
cd "C:\Users\KYTHOURS\Desktop\brcloudstream"
.\capture_logs.ps1

# Ou para tempo real:
.\capture_logs.ps1 -RealTime
```

### Passo 3: Testar no CloudStream
1. Abra o CloudStream
2. Entre no MaxSeries
3. Abra qualquer série/filme
4. Aguarde a extração de links
5. Pressione **Ctrl+C** no PowerShell para parar

### Passo 4: Analisar
```powershell
python analyze_logs.py cloudstream_logs_YYYYMMDD_HHMMSS.txt
```

---

## 📱 SEM PC? Use o Próprio CloudStream

Algumas versões do CloudStream têm log interno:

1. **Configurações** → **Desenvolvedor**
2. Ative **"Log de Debug"**
3. Reproduza o conteúdo
4. **Configurações** → **Logs** → **Exportar**
5. Me envie o arquivo

---

## 🎯 O QUE ESPERAR VER

### ✅ Sucesso Completo
```
🌐 PRIORIDADE 1 - PlayerEmbedAPI v5.0: https://...
ℹ️  [1/4] Tentando extração via API...
ℹ️  Pattern 1 funcionou!
🔓 Decrypting media: 1234 bytes
📺 Encontradas 3 fontes:
   [0] 1080p - https://storage.googleapis.com/...
   [1] 720p - https://storage.googleapis.com/...
   [2] 360p - https://storage.googleapis.com/...
✅✅✅ PlayerEmbedAPI v5.0: SUCESSO
```

### ⚠️ Com Fallback
```
🌐 PRIORIDADE 1 - PlayerEmbedAPI v5.0: https://...
⚠️  Pattern base64 não encontrado
🔄 Tentando ShortIcu...
✅✅✅ PlayerEmbedAPI v5.0: SUCESSO (ShortIcu)
```

### ❌ Falha
```
❌ Erro no request: timeout
❌ Todas as estratégias falharam
```

---

## 📊 INTERPRETAÇÃO RÁPIDA

| Resultado | Significado | Ação |
|-----------|-------------|------|
| **SUCESSO** na 1ª tentativa | ✅ Perfeito | Nada a fazer |
| **SUCESSO** após fallback | ⚠️ Funciona, mas... | Pode otimizar |
| **Falha** consistente | ❌ Problema | Reportar bug |

---

## 🆘 COMANDOS ÚTEIS

### Filtrar apenas erros:
```powershell
adb logcat -d | findstr "ERROR\|Falhou\|❌"
```

### Ver apenas PlayerEmbedAPI:
```powershell
adb logcat -d -s PlayerEmbedAPI-v5:D
```

### Limpar logs antigos:
```powershell
adb logcat -c
```

---

## 📤 ENVIAR PARA ANÁLISE

1. Capture os logs:
```powershell
.\capture_logs.ps1 -SaveTo "meus_logs.txt"
```

2. Analise:
```powershell
python analyze_logs.py meus_logs.txt
```

3. Me envie:
- Arquivo `meus_logs.txt`
- Arquivo `meus_logs_analysis.txt`
- Descrição do problema (se houver)

---

## ⏱️ TEMPO ESPERADO

| Operação | Tempo |
|----------|-------|
| Extração API (Estratégia 1) | 2-5 segundos |
| Extração ShortIcu | 3-8 segundos |
| Extração WebView | 10-20 segundos |
| **Se > 30 segundos** | ❌ Timeout |

---

## ✅ CHECKLIST DE FUNCIONAMENTO

- [ ] Logs mostram "PlayerEmbedAPI-v5"
- [ ] Versão 253 detectada
- [ ] Estratégia 1 (API) tentada primeiro
- [ ] Links retornados (360p/720p/1080p)
- [ ] Vídeo reproduz no player
- [ ] Cache HIT na segunda tentativa

**Se marcou tudo = 🎉 Está perfeito!**
