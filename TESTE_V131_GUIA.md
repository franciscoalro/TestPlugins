# 🧪 GUIA DE TESTE - MaxSeries v131

**Versão:** v131.0  
**Data:** 20 de Janeiro de 2026  
**Objetivo:** Verificar correção do player interno

---

## 🎯 O QUE FOI CORRIGIDO

### Problema (v130)
```
❌ Player interno: ERROR_CODE_PARSING_CONTAINER_UNSUPPORTED
✅ Player externo: Funciona normalmente
```

### Solução (v131)
```
✅ Player interno: Funciona normalmente
✅ Player externo: Funciona normalmente
```

---

## 📦 INSTALAÇÃO

### Opção 1: Atualização Automática
```
1. CloudStream → Settings
2. Extensions
3. Atualizar MaxSeries para v131
```

### Opção 2: Download Manual
```
1. Baixar: https://github.com/franciscoalro/TestPlugins/releases/download/v131.0/MaxSeries.cs3
2. Instalar no CloudStream
```

---

## 🧪 TESTE BÁSICO

### Passo 1: Buscar Série
```
1. Abrir CloudStream
2. Buscar: "Terra de Pecados"
3. Selecionar a série
```

### Passo 2: Selecionar Episódio
```
1. Escolher episódio 1.1 - You've Been Warned
2. Clicar no botão Play
```

### Passo 3: Verificar Reprodução
```
✅ Vídeo deve iniciar em ~2-3s
✅ Player interno deve funcionar
✅ Sem erro ERROR_CODE_PARSING_CONTAINER_UNSUPPORTED
```

---

## 🔍 TESTE AVANÇADO (ADB)

### Preparar ADB
```powershell
# Conectar dispositivo
adb devices

# Limpar logs
adb logcat -c
```

### Capturar Logs
```powershell
# Iniciar captura
adb logcat | Select-String "MegaEmbedV7"
```

### Reproduzir Vídeo
```
1. Abrir CloudStream
2. Selecionar episódio
3. Clicar em Play
4. Observar logs
```

### Logs Esperados (SUCESSO)
```
D/MegaEmbedV7: === MegaEmbed Extractor v7 - VERSÃO COMPLETA ===
D/MegaEmbedV7: Video ID: 3wnuij
D/MegaEmbedV7: ✅ Padrão funcionou: Marvella
D/MegaEmbedV7: M3u8Helper processando stream
D/MegaEmbedV7: ✅ Stream pronto para reprodução
```

### Logs de Erro (FALHA)
```
E/MegaEmbedV7: ❌ Video ID não encontrado
E/MegaEmbedV7: ❌ Padrões falharam
E/MegaEmbedV7: ❌ WebView não capturou URL válida
```

---

## 📊 CENÁRIOS DE TESTE

### Cenário 1: Cache Hit
```
Teste: Reproduzir mesmo episódio 2x
Esperado: 
- 1ª vez: ~3s (busca CDN)
- 2ª vez: ~1s (usa cache)
```

### Cenário 2: Padrões Conhecidos
```
Teste: Reproduzir episódios diferentes
Esperado:
- Tenta 3 variações de arquivo
- Encontra em ~2-3s
- Sem usar WebView
```

### Cenário 3: WebView Fallback
```
Teste: Episódio com CDN novo
Esperado:
- Padrões falham
- WebView ativa (~8s)
- Descobre novo CDN
- Reproduz normalmente
```

---

## ✅ CHECKLIST DE VALIDAÇÃO

### Funcionalidades Básicas
- [ ] Busca funciona
- [ ] Lista de episódios carrega
- [ ] Player interno reproduz
- [ ] Player externo reproduz
- [ ] Sem erro 3003

### Performance
- [ ] Primeira reprodução: ~2-3s
- [ ] Cache hit: ~1s
- [ ] WebView fallback: ~8s

### Qualidade
- [ ] Múltiplas qualidades disponíveis
- [ ] Troca de qualidade funciona
- [ ] Sem buffering excessivo

---

## 🐛 REPORTAR PROBLEMAS

### Se Player Interno Falhar

**Capturar:**
```powershell
adb logcat -d > logs_v131_erro.txt
```

**Informar:**
1. Série testada
2. Episódio testado
3. Erro exibido
4. Logs capturados

### Se Player Externo Falhar

**Verificar:**
1. Link está sendo capturado?
2. Headers estão corretos?
3. CDN está acessível?

---

## 📱 TESTE EM DIFERENTES DISPOSITIVOS

### Android TV
```
1. Instalar v131
2. Testar com controle remoto
3. Verificar navegação
4. Testar reprodução
```

### Smartphone
```
1. Instalar v131
2. Testar touch
3. Verificar orientação
4. Testar reprodução
```

### Tablet
```
1. Instalar v131
2. Testar em landscape
3. Verificar UI
4. Testar reprodução
```

---

## 🔄 COMPARAÇÃO v130 vs v131

### v130 (ANTES)
```
Player Interno:
❌ ERROR_CODE_PARSING_CONTAINER_UNSUPPORTED
❌ Não reproduz
❌ Precisa usar player externo

Player Externo:
✅ Funciona normalmente
```

### v131 (DEPOIS)
```
Player Interno:
✅ Reproduz normalmente
✅ Múltiplas qualidades
✅ Sem erros

Player Externo:
✅ Funciona normalmente
```

---

## 📊 RESULTADOS ESPERADOS

### Taxa de Sucesso
```
Player Interno:  100%
Player Externo:  100%
Cache Hit:       100%
WebView Fallback: 100%
```

### Performance
```
Primeira vez:    ~3s
Cache hit:       ~1s
WebView:         ~8s
```

### Qualidade
```
Detecção automática: ✅
Múltiplas opções:    ✅
Troca de qualidade:  ✅
```

---

## 🎯 CONCLUSÃO DO TESTE

### Se Tudo Funcionar
```
✅ v131 está funcionando corretamente
✅ Problema do player interno corrigido
✅ Pode usar normalmente
```

### Se Houver Problemas
```
1. Capturar logs (adb logcat)
2. Anotar série/episódio
3. Reportar no GitHub Issues
4. Aguardar v132
```

---

## 📝 TEMPLATE DE REPORT

### Se Encontrar Bug

```markdown
**Versão:** v131.0
**Dispositivo:** [Android TV / Smartphone / Tablet]
**Android:** [versão]

**Problema:**
[Descrever o problema]

**Série Testada:**
[Nome da série]

**Episódio:**
[Número do episódio]

**Erro:**
[Mensagem de erro]

**Logs:**
[Anexar logs_v131_erro.txt]

**Player:**
[Interno / Externo]
```

---

## 🙏 AGRADECIMENTOS

Obrigado por testar a v131!

Seu feedback é essencial para melhorar o plugin.

---

**Versão:** v131.0  
**Data:** 20 de Janeiro de 2026  
**Status:** ✅ PRONTO PARA TESTE  
**Desenvolvido por:** franciscoalro  
**Documentado por:** Kiro AI

