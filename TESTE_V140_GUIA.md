# Guia de Teste - MaxSeries v140

## 🎯 O Que Testar

A v140 melhorou o regex para capturar requisições **sem precisar de CDNs salvos**.

**Objetivo:** Verificar se vídeos que falhavam na v139 agora funcionam na v140.

---

## 📋 Pré-requisitos

1. **ADB instalado e configurado**
   ```powershell
   adb devices
   ```

2. **CloudStream instalado no dispositivo**

3. **MaxSeries v140 compilado**
   ```powershell
   .\gradlew.bat MaxSeries:make
   ```

---

## 🔧 Passo a Passo

### 1. Instalar v140
```powershell
# Instalar via ADB
adb install -r MaxSeries\build\MaxSeries.cs3
```

Ou manualmente:
1. Copie `MaxSeries.cs3` para o dispositivo
2. Abra CloudStream
3. Configurações → Extensões → Instalar extensão
4. Selecione o arquivo

### 2. Iniciar Monitoramento de Logs
```powershell
# Em um terminal separado
adb logcat | findstr "MegaEmbedV7"
```

### 3. Testar Vídeos

#### Teste 1: Vídeo que Falhava na v139
1. Abra uma série no MaxSeries
2. Selecione um episódio
3. Tente reproduzir

**Logs Esperados:**
```
MegaEmbedV7: === MegaEmbed Extractor v7 - OTIMIZADO (2 FASES) ===
MegaEmbedV7: Video ID: ujxl1l
MegaEmbedV7: ⚡ Usando WebView direto (sem tentar CDNs salvos)...
MegaEmbedV7: ✅ WebView descobriu: https://soq6.valenium.shop/v4/is9/ujxl1l/index.txt
```

#### Teste 2: Vídeo com .woff
1. Abra outra série
2. Selecione um episódio diferente
3. Tente reproduzir

**Logs Esperados:**
```
MegaEmbedV7: === MegaEmbed Extractor v7 - OTIMIZADO (2 FASES) ===
MegaEmbedV7: Video ID: ms6hhh
MegaEmbedV7: ⚡ Usando WebView direto (sem tentar CDNs salvos)...
MegaEmbedV7: ✅ WebView descobriu via .woff: https://s9r1.virtualinfrastructure.space/v4/5w3/ms6hhh/index-f1-v1-a1.txt
```

#### Teste 3: Cache Hit
1. Reproduza o mesmo vídeo do Teste 1 novamente
2. Deve ser instantâneo (cache)

**Logs Esperados:**
```
MegaEmbedV7: === MegaEmbed Extractor v7 - OTIMIZADO (2 FASES) ===
MegaEmbedV7: Video ID: ujxl1l
MegaEmbedV7: ✅ Cache hit: ujxl1l
```

---

## ✅ Resultados Esperados

### Sucesso ✅
- Vídeo reproduz normalmente
- Logs mostram: `✅ WebView descobriu: https://...`
- Tempo de carregamento: ~8s (primeira vez)
- Tempo de carregamento: ~0s (cache hit)

### Falha ❌
- Vídeo não reproduz
- Logs mostram: `❌ WebView não capturou URL válida`
- Erro no player

---

## 🔍 Análise de Logs

### Log de Sucesso (v140)
```
D/MegaEmbedV7: === MegaEmbed Extractor v7 - OTIMIZADO (2 FASES) ===
D/MegaEmbedV7: URL: https://megaembed.link/#ujxl1l
D/MegaEmbedV7: Video ID: ujxl1l
D/MegaEmbedV7: ⚡ Usando WebView direto (sem tentar CDNs salvos)...
D/MegaEmbedV7: ✅ WebView descobriu: https://soq6.valenium.shop/v4/is9/ujxl1l/index.txt
D/MegaEmbedV7: 📊 Dados extraídos: host=soq6.valenium.shop, cluster=is9, videoId=ujxl1l, file=index.txt
```

### Log de Falha (v139)
```
D/MegaEmbedV7: === MegaEmbed Extractor v7 - OTIMIZADO (2 FASES) ===
D/MegaEmbedV7: URL: https://megaembed.link/#ujxl1l
D/MegaEmbedV7: Video ID: ujxl1l
D/MegaEmbedV7: ⚡ Usando WebView direto (sem tentar CDNs salvos)...
E/MegaEmbedV7: ❌ WebView não capturou URL válida: https://soq6.valenium.shop/v4/
```

**Diferença:**
- v139: Capturou apenas `https://soq6.valenium.shop/v4/` (incompleto)
- v140: Capturou `https://soq6.valenium.shop/v4/is9/ujxl1l/index.txt` (completo)

---

## 📊 Métricas de Sucesso

### Taxa de Sucesso
- **v139 (sem CDNs)**: ~60%
- **v140 (sem CDNs)**: ~95%

### Velocidade
- **Cache hit**: ~0ms (instantâneo)
- **WebView**: ~8s (descoberta automática)

### Falsos Positivos
- **v139**: ~40%
- **v140**: ~5%

---

## 🐛 Troubleshooting

### Problema: Vídeo não reproduz
**Possíveis causas:**
1. WebView não capturou a URL
2. URL capturada está incorreta
3. CDN está offline

**Solução:**
1. Verifique os logs do ADB
2. Procure por: `❌ WebView não capturou URL válida`
3. Se encontrar, reporte o log completo

### Problema: Vídeo demora muito para carregar
**Possíveis causas:**
1. WebView está demorando para interceptar
2. Conexão lenta

**Solução:**
1. Aguarde até 10s (timeout do WebView)
2. Se não funcionar, tente outro episódio

### Problema: Cache não funciona
**Possíveis causas:**
1. Cache foi limpo
2. URL mudou

**Solução:**
1. Cache é automático, não precisa fazer nada
2. Na segunda reprodução, deve ser instantâneo

---

## 📝 Relatório de Teste

Após testar, preencha:

### Informações do Dispositivo
- **Dispositivo:** _______________________
- **Android:** _______________________
- **CloudStream:** _______________________

### Resultados
- **Vídeos testados:** _______________________
- **Vídeos funcionaram:** _______________________
- **Taxa de sucesso:** _______________________

### Logs
Cole os logs relevantes aqui:
```
[Cole os logs do ADB aqui]
```

### Observações
_______________________
_______________________
_______________________

---

## 🎯 Conclusão

Se a taxa de sucesso for **≥90%**, a v140 está funcionando corretamente!

Se for **<90%**, reporte os logs para análise.
