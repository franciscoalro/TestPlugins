# Guia de Teste - PlayerEmbedAPI no CloudStream

## 🎯 Objetivo

Testar a implementação do PlayerEmbedAPI v3 (Playwright Optimized) no CloudStream app.

## 📋 Pré-requisitos

- ✅ CloudStream app instalado no Android
- ✅ MaxSeries.cs3 compilado com PlayerEmbedAPI v3
- ✅ ADB configurado (opcional, para logs)

## 🔨 Passo 1: Build do Provider

### Opção A: Script Automático (Recomendado)
```powershell
.\build-and-test-playerembedapi.ps1
```

### Opção B: Build Manual
```powershell
.\gradlew.bat :MaxSeries:make
```

**Resultado esperado**: `MaxSeries.cs3` gerado na raiz do projeto

## 📱 Passo 2: Instalar no CloudStream

### Método 1: Via Repositório (Recomendado)
1. Abrir CloudStream
2. Ir em **Settings** → **Extensions**
3. Adicionar repositório (se ainda não tiver):
   ```
   https://raw.githubusercontent.com/SEU_USUARIO/SEU_REPO/main/repo.json
   ```
4. Instalar/Atualizar **MaxSeries**

### Método 2: Instalação Manual
1. Copiar `MaxSeries.cs3` para o dispositivo
2. Abrir CloudStream
3. Ir em **Settings** → **Extensions**
4. Clicar em **+** (adicionar)
5. Selecionar `MaxSeries.cs3`
6. Confirmar instalação

## 🧪 Passo 3: Teste Básico

### 3.1 Buscar Série
1. Abrir CloudStream
2. Buscar: **"Terra de Pecados"** ou **"Land of Sin"**
3. Selecionar a série
4. Escolher um episódio

### 3.2 Verificar Players Disponíveis
Você deve ver os players nesta ordem de prioridade:

1. **PlayerEmbedAPI** ⭐ (PRIORIDADE 1)
2. MyVidPlay
3. Streamtape
4. Filemoon
5. DoodStream
6. Mixdrop
7. VidStack
8. Uqload
9. VidCloud
10. MegaEmbed

### 3.3 Testar PlayerEmbedAPI
1. Clicar em **PlayerEmbedAPI**
2. Aguardar carregamento (~5-15 segundos)
3. Verificar se o vídeo inicia

**Resultado esperado**:
- ✅ Vídeo carrega e reproduz
- ✅ Qualidade: 1080p
- ✅ Sem buffering excessivo
- ✅ Controles funcionando

## 🔍 Passo 4: Verificar Logs (Opcional)

### 4.1 Conectar via ADB
```bash
adb logcat | grep -i "playerembedapi\|maxseries"
```

### 4.2 Logs Esperados - Sucesso
```
🎬 [P1] PlayerEmbedAPIExtractor - MP4 direto (WebView)
📄 Iniciando captura WebView (v101)
Target: https://playerembedapi.link/?v=kBJLtxCD3
🎯 URL interceptada: https://storage.googleapis.com/mediastorage/1768755384966/az8sfdbewst/81347747.mp4
✅ PlayerEmbedAPI extraction successful
⏱️ Performance: 5234ms
Quality: 1080p
```

### 4.3 Logs Esperados - Fallback
```
🎬 [P1] PlayerEmbedAPIExtractor - MP4 direto (WebView)
⚠️ WebView timeout, tentando Stealth Extraction...
🔓 Stealth descompactou script (15234 chars)
🎯 Stealth capturou URL: https://storage.googleapis.com/...
✅ PlayerEmbedAPI extraction successful (Stealth)
```

### 4.4 Logs de Erro
```
❌ PlayerEmbedAPI extraction failed
Error: Timeout after 15000ms
Fallback: Tentando próximo extractor (MyVidPlay)
```

## ✅ Checklist de Validação

### Funcionalidade Básica
- [ ] PlayerEmbedAPI aparece na lista de players
- [ ] PlayerEmbedAPI é o primeiro da lista (PRIORIDADE 1)
- [ ] Vídeo carrega em menos de 20 segundos
- [ ] Vídeo reproduz sem erros
- [ ] Qualidade é 1080p ou superior

### Performance
- [ ] Tempo de carregamento: < 15 segundos
- [ ] Sem buffering excessivo
- [ ] Seek (avançar/voltar) funciona
- [ ] Controles de velocidade funcionam

### Confiabilidade
- [ ] Funciona em múltiplos episódios
- [ ] Funciona em diferentes séries
- [ ] Cache funciona (segundo acesso mais rápido)
- [ ] Fallback funciona se PlayerEmbedAPI falhar

### URL Capturada
- [ ] URL contém `storage.googleapis.com`
- [ ] URL contém `/mediastorage/`
- [ ] URL termina em `.mp4`
- [ ] Pattern: `{timestamp}/{random}/{video_id}.mp4`

## 🐛 Troubleshooting

### Problema 1: PlayerEmbedAPI não aparece
**Causa**: Provider não instalado corretamente

**Solução**:
1. Verificar se MaxSeries.cs3 foi instalado
2. Reiniciar CloudStream
3. Verificar versão do provider (deve ser v103+)

### Problema 2: Timeout (15 segundos)
**Causa**: Conexão lenta ou site fora do ar

**Solução**:
1. Verificar conexão de internet
2. Tentar novamente
3. Usar outro player (fallback automático)

### Problema 3: Vídeo não carrega
**Causa**: URL do Google Cloud Storage expirou

**Solução**:
1. Fechar e reabrir o episódio
2. Cache será limpo automaticamente
3. Nova URL será capturada

### Problema 4: Qualidade baixa
**Causa**: Detection automática falhou

**Solução**:
1. Verificar logs para ver URL capturada
2. URL deve conter `storage.googleapis.com`
3. Se não, fallback para outro player

## 📊 Métricas de Sucesso

### Taxa de Sucesso Esperada
- **PlayerEmbedAPI**: 90-95%
- **Com fallbacks**: 98-99%

### Tempo de Carregamento
- **Ideal**: 5-8 segundos
- **Aceitável**: 8-15 segundos
- **Timeout**: > 15 segundos (fallback)

### Qualidade
- **Esperada**: 1080p
- **Mínima**: 720p

## 🎬 Episódios de Teste Recomendados

### Série 1: Terra de Pecados (Land of Sin)
- **URL**: https://www.maxseries.one/series/terra-de-pecados/
- **Episódio**: S01E01
- **PlayerEmbedAPI**: ✅ Confirmado funcionando

### Série 2: O Gerente da Noite
- **URL**: https://www.maxseries.one/series/o-gerente-da-noite/
- **Episódio**: S01E01
- **PlayerEmbedAPI**: ⏳ Testar

### Série 3: Chapolin e Os Colorados
- **URL**: https://www.maxseries.one/series/chapolin-e-os-colorados/
- **Episódio**: S01E01
- **PlayerEmbedAPI**: ⏳ Testar

## 📝 Relatório de Teste

### Template
```markdown
## Teste PlayerEmbedAPI v3

**Data**: [DATA]
**Dispositivo**: [MODELO]
**CloudStream**: [VERSÃO]
**MaxSeries**: [VERSÃO]

### Série Testada
- Nome: [NOME]
- Episódio: [SxxExx]
- URL: [URL]

### Resultados
- [ ] PlayerEmbedAPI apareceu
- [ ] Vídeo carregou
- [ ] Tempo de carregamento: [X] segundos
- [ ] Qualidade: [QUALIDADE]
- [ ] URL capturada: [URL]

### Logs
```
[COLAR LOGS AQUI]
```

### Observações
[OBSERVAÇÕES ADICIONAIS]

### Status Final
- [ ] ✅ Sucesso
- [ ] ⚠️ Sucesso com ressalvas
- [ ] ❌ Falha
```

## 🚀 Próximos Passos Após Teste

### Se Sucesso (✅)
1. Documentar resultados
2. Testar com mais episódios
3. Validar em diferentes dispositivos
4. Deploy para produção

### Se Falha (❌)
1. Coletar logs completos
2. Identificar causa raiz
3. Ajustar timeout/interceptação
4. Rebuild e testar novamente

## 📚 Referências

- **Análise Completa**: `PLAYEREMBEDAPI_FINAL_SUMMARY.md`
- **Implementação**: `PLAYEREMBEDAPI_CLOUDSTREAM_IMPLEMENTATION.md`
- **Comparação**: `PLAYWRIGHT_VS_BURPSUITE.md`
- **Exemplos**: `EXEMPLOS_PRATICOS.md`

## 🎉 Conclusão

Este guia cobre todos os aspectos do teste do PlayerEmbedAPI v3 no CloudStream. Siga os passos em ordem e documente os resultados para validar a implementação.

**Boa sorte com os testes!** 🚀

---

**Última atualização**: Janeiro 2026  
**Versão**: v3 (Playwright Optimized)  
**Status**: Pronto para teste
