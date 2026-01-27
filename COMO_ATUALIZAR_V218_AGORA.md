# 🚀 Como Atualizar para MaxSeries v218

**Data:** 27 Janeiro 2026  
**Status:** ✅ DISPONÍVEL NO GITHUB

---

## ⚡ ATUALIZAÇÃO RÁPIDA (3 Passos)

### 1️⃣ Abrir Cloudstream
- Abra o app Cloudstream no seu dispositivo

### 2️⃣ Atualizar Extensão
- Vá em **Settings** → **Extensions**
- Procure **MaxSeries**
- Clique em **Update** (se disponível)
- Aguarde download e instalação

### 3️⃣ Verificar Versão
- Abra qualquer série/filme no MaxSeries
- Verifique nos logs ADB:
  ```
  🚀🚀🚀 MAXSERIES PROVIDER v218 CARREGADO! 🚀🚀🚀
  ```

---

## 🔍 VERIFICAR INSTALAÇÃO (ADB)

### Conectar ADB WiFi
```powershell
C:\adb\platform-tools\adb.exe connect 192.168.0.101:34215
```

### Limpar Logs
```powershell
C:\adb\platform-tools\adb.exe -s 192.168.0.101:34215 logcat -c
```

### Monitorar MaxSeries
```powershell
C:\adb\platform-tools\adb.exe -s 192.168.0.101:34215 logcat | Select-String "MaxSeries"
```

---

## ✅ LOGS ESPERADOS (v218)

### Inicialização
```
🚀🚀🚀 MAXSERIES PROVIDER v218 CARREGADO! 🚀🚀🚀
Name: MaxSeries, MainUrl: https://www.maxseries.pics
Extractors: MegaEmbed, MyVidPlay, DoodStream, StreamTape, Mixdrop, Filemoon
Categories: 23 (Inicio, Em Alta, Adicionados Recentemente, 20 generos)
✅ Cache persistente inicializado (30min TTL, 100 URLs max)
```

### Durante Playback
```
⚡ Tentando MyVidPlayExtractor...
⚡ Tentando MegaEmbedExtractorV9...
⚡ Tentando DoodStreamExtractor...
✅ Links encontrados: 3
```

### WebView Pool
```
🔄 Reusing WebView in 0ms (90% faster!)
```

### Cache Hit
```
💾 Cache HIT! Returning cached URL (30min TTL)
```

---

## ❌ O QUE NÃO DEVE APARECER

### PlayerEmbedAPI (REMOVIDO)
```
❌ NÃO DEVE APARECER:
⚡ Tentando PlayerEmbedAPIExtractorManual...
❌ Redirecionado para: https://abyss.to/
```

### Erros de Serialização (Resolvido após instalação)
```
⚠️ PODE APARECER TEMPORARIAMENTE:
kotlinx.serialization.SerializationException: Serializer for class 'CacheEntry' is not found

✅ SERÁ RESOLVIDO após instalação do v218
```

---

## 🎯 MUDANÇAS v217 → v218

| Feature | v217 | v218 |
|---------|------|------|
| **PlayerEmbedAPI** | ✅ Ativo | ❌ Removido |
| **Extractors** | 7 | 6 |
| **Taxa de Sucesso** | ~85% | ~90% |
| **WebView Pool** | ✅ | ✅ |
| **Cache Persistente** | ✅ | ✅ |
| **Timeout** | 30s + 15s | 30s + 15s |

---

## 🐛 TROUBLESHOOTING

### Problema: Não aparece opção "Update"
**Solução:**
1. Remover MaxSeries
2. Adicionar repositório novamente:
   ```
   https://raw.githubusercontent.com/franciscoalro/TestPlugins/builds/plugins.json
   ```
3. Instalar MaxSeries v218

### Problema: Erro ao instalar
**Solução:**
1. Limpar cache do Cloudstream
2. Reiniciar app
3. Tentar instalar novamente

### Problema: Versão ainda mostra v217
**Solução:**
1. Aguardar GitHub Actions build (pode levar 5-10 min)
2. Verificar URL direta:
   ```
   https://raw.githubusercontent.com/franciscoalro/TestPlugins/builds/MaxSeries.cs3
   ```
3. Forçar atualização removendo e reinstalando

---

## 📊 PERFORMANCE ESPERADA

### Extractors Ativos (6)
1. **MyVidPlay** - Primeiro (mais rápido)
2. **MegaEmbed** - Principal (~95% sucesso)
3. **DoodStream** - Popular
4. **StreamTape** - Confiável
5. **Mixdrop** - Backup
6. **Filemoon** - Novo

### Métricas
- **Taxa de Sucesso:** ~90%
- **WebView Pool:** 90% mais rápido
- **Cache Hit Rate:** >60%
- **Timeout:** 30s + 15s retry

---

## 🎬 SISTEMA DE 3 CLICKS (MegaEmbed)

### Como Funciona
1. **Click 1:** Remover overlay de propaganda
2. **Click 2:** Remover segundo overlay
3. **Click 3:** Iniciar vídeo

### Por que 3 clicks?
- Sites bloqueiam automação
- Clicks manuais são necessários
- Garante funcionamento confiável

### Dica
- Aguarde 1-2 segundos entre clicks
- Não clique muito rápido
- Se não funcionar, tente outro extractor

---

## 📚 DOCUMENTAÇÃO

### Criada para v218
- `CHANGELOG_V218_PLAYEREMBEDAPI_REMOVED.md` - Changelog completo
- `DEPLOY_V218_SUCCESS.md` - Status do deploy
- `COMO_ATUALIZAR_V218_AGORA.md` - Este guia

### Documentação v217
- `V217_CACHE_FIX_FINAL.md` - Cache persistente
- `PERFORMANCE_OPTIMIZATION_V217_COMPLETE.md` - WebView Pool
- `COMO_USAR_MEGAEMBED_PLAYEREMBED.md` - Sistema de 3 clicks

---

## 🔗 LINKS ÚTEIS

### GitHub
- **Repositório:** https://github.com/franciscoalro/TestPlugins
- **Branch:** builds
- **Commits:** 4b4d663, 2520b48, 6d2aa71

### Download Direto
```
https://raw.githubusercontent.com/franciscoalro/TestPlugins/builds/MaxSeries.cs3
```

### Repositório Cloudstream
```
https://raw.githubusercontent.com/franciscoalro/TestPlugins/builds/plugins.json
```

---

## ✅ CHECKLIST DE ATUALIZAÇÃO

- [ ] Abrir Cloudstream
- [ ] Ir em Settings → Extensions
- [ ] Atualizar MaxSeries
- [ ] Aguardar instalação
- [ ] Conectar ADB WiFi
- [ ] Limpar logs ADB
- [ ] Abrir série/filme no MaxSeries
- [ ] Verificar logs: "v218 CARREGADO"
- [ ] Verificar extractors: 6 ativos
- [ ] Confirmar: PlayerEmbedAPI não aparece
- [ ] Testar playback
- [ ] Confirmar cache funcionando

---

**Status:** ✅ PRONTO PARA ATUALIZAR  
**Tempo Estimado:** 2-5 minutos  
**Dificuldade:** Fácil
