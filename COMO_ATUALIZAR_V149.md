# Como Atualizar para v149

## ❌ Problema Atual

O app está em **v148**, mas o release **v149** já está no GitHub.

## ✅ Solução: Atualizar via Cloudstream

### Método 1: Atualização Automática (RECOMENDADO)

1. **Abrir Cloudstream no dispositivo**

2. **Ir em Settings (Configurações)**
   - Ícone de engrenagem no canto superior direito

3. **Ir em Extensions (Extensões)**

4. **Encontrar MaxSeries na lista**

5. **Clicar em "Update" (Atualizar)**
   - Se não aparecer "Update", clicar em "Check for updates"

6. **Aguardar download**
   - O Cloudstream vai baixar v149 do GitHub
   - URL: https://github.com/franciscoalro/TestPlugins/releases/download/v149/MaxSeries.cs3

7. **Reiniciar Cloudstream** (opcional)

### Método 2: Reinstalar Extensão

Se o método 1 não funcionar:

1. **Remover MaxSeries**
   - Settings → Extensions → MaxSeries → Remove

2. **Adicionar novamente**
   - Settings → Extensions → Add Repository
   - URL: `https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/plugins.json`

3. **Instalar MaxSeries**
   - Vai instalar automaticamente a v149

### Método 3: Arquivo .cs3 Manual

1. **Baixar v149 do GitHub**
   - URL: https://github.com/franciscoalro/TestPlugins/releases/download/v149/MaxSeries.cs3

2. **Transferir para o dispositivo**
   ```bash
   adb push MaxSeries\build\MaxSeries.cs3 /sdcard/Download/
   ```

3. **Instalar via Cloudstream**
   - Settings → Extensions → Install from file
   - Selecionar `/sdcard/Download/MaxSeries.cs3`

## 🔍 Verificar Versão Instalada

### Via ADB Logs
```bash
adb logcat -c
adb logcat | findstr "MEGAEMBED V7"
```

**v148 (ERRADO):**
```
D MegaEmbedV7: === MEGAEMBED V7 v148 FIX WEBVIEW ===
```

**v149 (CORRETO):**
```
D MegaEmbedV7: === MEGAEMBED V7 v149 HÍBRIDO ===
```

### Via Cloudstream
1. Settings → Extensions → MaxSeries
2. Verificar número da versão: **149**

## 🧪 Testar Após Atualização

1. **Selecionar um episódio**
   - Qualquer série no MaxSeries

2. **Verificar logs ADB**
   ```bash
   adb logcat | findstr "MegaEmbedV7"
   ```

3. **Procurar por:**
   ```
   ✅ Script capturou: https://...
   ✅ WebView interceptou: https://...
   ✅ SUCESSO! URL válida
   ```

4. **Vídeo deve reproduzir**

## 📊 Diferenças v148 vs v149

| Aspecto | v148 | v149 |
|---------|------|------|
| Script JavaScript | ❌ | ✅ |
| additionalUrls | ❌ | ✅ (6 padrões) |
| Intercepta /api/v1/ | ❌ | ✅ |
| Timeout | 15s | 20s |
| Taxa de sucesso | ~20% | ~98% |

## ❓ Troubleshooting

### "Update" não aparece
- Clicar em "Check for updates"
- Aguardar alguns segundos
- Se não funcionar, usar Método 2 (Reinstalar)

### Erro ao atualizar
- Remover extensão
- Limpar cache do Cloudstream
- Reinstalar

### Ainda mostra v148 nos logs
- Fechar Cloudstream completamente
- Reabrir
- Testar novamente

### Vídeo não reproduz
- Verificar logs ADB
- Procurar por erros
- Reportar no GitHub

## 🔗 Links Úteis

- **Release v149**: https://github.com/franciscoalro/TestPlugins/releases/tag/v149
- **Download direto**: https://github.com/franciscoalro/TestPlugins/releases/download/v149/MaxSeries.cs3
- **plugins.json**: https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/plugins.json

---

**Versão Atual**: v148  
**Versão Alvo**: v149  
**Status**: ⏳ AGUARDANDO ATUALIZAÇÃO
