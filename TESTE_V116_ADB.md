# 🧪 Guia de Teste - MaxSeries v116 via ADB

## 🎯 Objetivo

Verificar se a v116 está funcionando corretamente e se o WebView está capturando os vídeos do MegaEmbed.

## 📋 Pré-requisitos

1. ✅ Dispositivo Android conectado via USB
2. ✅ Modo de depuração ativado
3. ✅ ADB instalado em `C:\Users\KYTHOURS\Desktop\platform-tools`
4. ✅ Cloudstream instalado no dispositivo

## 🔧 Passo 1: Atualizar Plugin

### No Cloudstream (Android)

1. Abrir Cloudstream
2. Ir em **Configurações** → **Extensões**
3. Clicar em **MaxSeries**
4. Verificar se mostra **v116**
5. Se ainda estiver v115, clicar em **Atualizar**

**Ou forçar atualização**:
1. Remover MaxSeries
2. Adicionar novamente usando o repositório:
   ```
   https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/plugins.json
   ```

## 🔍 Passo 2: Iniciar Monitoramento ADB

### Abrir PowerShell

```powershell
cd C:\Users\KYTHOURS\Desktop\platform-tools
```

### Verificar Conexão

```powershell
.\adb devices
```

**Saída esperada**:
```
List of devices attached
2303ERA42L      device
```

### Iniciar Logs Filtrados

```powershell
.\adb logcat | Select-String "MegaEmbed"
```

**Ou para logs mais detalhados**:
```powershell
.\adb logcat | Select-String "MegaEmbedExtractorV5_v116|MaxSeriesProvider"
```

## 🎬 Passo 3: Testar Reprodução

### No Cloudstream (Android)

1. Abrir **MaxSeries**
2. Buscar uma série (ex: "O Gerente da Noite")
3. Selecionar um episódio
4. Aguardar carregar as fontes
5. Verificar se **MegaEmbed** aparece
6. Clicar em **MegaEmbed**
7. Tentar reproduzir

## 📊 Passo 4: Analisar Logs

### ✅ Logs de Sucesso (v116)

```
MegaEmbedExtractorV5_v116: === MEGAEMBED V5 WEBVIEW-ONLY (v116) ===
MegaEmbedExtractorV5_v116: 🎬 URL: https://megaembed.link/embed/abc123
MegaEmbedExtractorV5_v116: 🚀 Iniciando WebView Interception (Modo Exclusivo)...
MegaEmbedExtractorV5_v116: 🆔 VideoId alvo: abc123
MegaEmbedExtractorV5_v116: 📜 JS Callback capturou: https://spo3.marvellaholdings.sbs/v4/x6b/abc123/cf-master.1768694011.txt
MegaEmbedExtractorV5_v116: 🎯 URL VÁLIDA ENCONTRADA: https://spo3.marvellaholdings.sbs/...
MegaEmbedExtractorV5_v116: ✅ WebView interceptou com sucesso!
```

**Indicadores de sucesso**:
- ✅ TAG mostra `MegaEmbedExtractorV5_v116` (confirma v116)
- ✅ Log mostra "WEBVIEW-ONLY (v116)"
- ✅ WebView é iniciado imediatamente
- ✅ URL `.txt` é capturada
- ✅ Não há tentativas de `MegaEmbedLinkFetcher` (API tradicional)

### ❌ Logs de Falha (v115 ainda ativa)

```
MegaEmbedLinkFetcher: 🔬 [1/30] Testando: valenium.shop/is3
MegaEmbedLinkFetcher: 🔬 [2/30] Testando: valenium.shop/x6b
...
MegaEmbedLinkFetcher: ❌ Nenhuma URL construída funcionou
```

**Indicadores de problema**:
- ❌ `MegaEmbedLinkFetcher` está rodando (v115 ainda ativa)
- ❌ TAG não mostra `v116`
- ❌ 30 tentativas de hosts
- ❌ Todos falhando

**Solução**: Forçar atualização do plugin (ver Passo 1)

### ⚠️ Logs de Falha (v116 ativa mas WebView falhou)

```
MegaEmbedExtractorV5_v116: === MEGAEMBED V5 WEBVIEW-ONLY (v116) ===
MegaEmbedExtractorV5_v116: 🚀 Iniciando WebView Interception (Modo Exclusivo)...
MegaEmbedExtractorV5_v116: ⚠️ Interceptação direta falhou, tentando injeção JS...
MegaEmbedExtractorV5_v116: ❌ FALHA TOTAL: WebView não conseguiu capturar o vídeo.
```

**Indicadores**:
- ✅ v116 está ativa (TAG correto)
- ❌ WebView não conseguiu capturar
- ✅ Não há tentativas de API tradicional (correto)

**Possíveis causas**:
1. Vídeo não existe no MegaEmbed
2. MegaEmbed mudou estrutura
3. Timeout muito curto (30s)
4. Problema de rede/VPN

**Solução**: Testar outro episódio ou verificar se PlayerThree funciona

## 🔄 Passo 5: Verificar Fallback

Se MegaEmbed falhar, o MaxSeries deve tentar outros extractors automaticamente:

```
MaxSeriesProvider: 🔗 loadLinks: https://playerthree.online/embed/synden/|episodio|255704
MaxSeriesProvider: 🎬 Buscando episódio: https://playerthree.online/episodio/255704
MaxSeriesProvider: 📄 Resposta do episódio (6042 chars)
```

**Indicadores de fallback funcionando**:
- ✅ PlayerThree é tentado após MegaEmbed falhar
- ✅ HTML é capturado
- ✅ Outras fontes aparecem no player

## 📝 Passo 6: Salvar Logs

### Salvar logs completos

```powershell
.\adb logcat -d > logs_v116_teste.txt
```

### Filtrar apenas MegaEmbed

```powershell
.\adb logcat -d | Select-String "MegaEmbed" > logs_v116_megaembed.txt
```

## 🎯 Checklist de Validação

### ✅ v116 Funcionando Corretamente

- [ ] TAG mostra `MegaEmbedExtractorV5_v116`
- [ ] Log mostra "WEBVIEW-ONLY (v116)"
- [ ] Não há tentativas de `MegaEmbedLinkFetcher`
- [ ] WebView é iniciado imediatamente
- [ ] URL `.txt` é capturada (se vídeo existe)
- [ ] Vídeo reproduz (se URL válida)
- [ ] Tempo de resposta < 5 segundos

### ❌ Problemas Identificados

- [ ] TAG mostra `MegaEmbedExtractorV5_LIVE` (v115 ainda ativa)
- [ ] `MegaEmbedLinkFetcher` está rodando (API tradicional)
- [ ] 30 tentativas de hosts (bruteforce)
- [ ] Tempo de resposta > 9 segundos
- [ ] WebView não é tentado

## 🔧 Troubleshooting

### Problema: v116 não aparece

**Solução**:
1. Remover MaxSeries completamente
2. Limpar cache do Cloudstream
3. Reinstalar MaxSeries
4. Verificar versão novamente

### Problema: WebView falha sempre

**Possíveis causas**:
1. VPN bloqueando WebView
2. MegaEmbed mudou estrutura
3. Timeout muito curto

**Solução**:
1. Desativar VPN temporariamente
2. Testar múltiplos episódios
3. Verificar se PlayerThree funciona

### Problema: Vídeo não reproduz

**Possíveis causas**:
1. URL `.txt` capturada mas inválida
2. Headers incorretos
3. CDN bloqueando

**Solução**:
1. Verificar logs para ver URL capturada
2. Testar URL manualmente no navegador
3. Verificar se outros extractors funcionam

## 📊 Comparação de Performance

### v115 (Com API Tradicional)

```
⏱️ Tempo total: ~9 segundos
├─ MegaEmbedLinkFetcher: 9s (30 tentativas) ❌
└─ WebView: NÃO TENTADO ❌
```

### v116 (Só WebView)

```
⏱️ Tempo total: ~3-5 segundos
└─ WebView: Tentado imediatamente ✅
```

## 🎯 Resultado Esperado

Após seguir todos os passos:

1. ✅ v116 confirmada nos logs
2. ✅ WebView funcionando
3. ✅ URLs `.txt` sendo capturadas
4. ✅ Vídeos reproduzindo
5. ✅ Tempo de resposta < 5s
6. ✅ Fallback para PlayerThree funcionando

---

**Próximo passo**: Se tudo funcionar, documentar sucesso e considerar melhorias adicionais.
