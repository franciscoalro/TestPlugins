# 🔍 DIAGNÓSTICO: Player Não Inicia

## Data: 22/01/2026 20:28

---

## ❌ PROBLEMA

**Player não inicia** para séries e filmes do maxseries.one

---

## 🔍 ERRO IDENTIFICADO NOS LOGS

```
MegaEmbedV8: ❌ Erro: Job was cancelled
kotlinx.coroutines.JobCancellationException: Job was cancelled
```

### **O que isso significa:**

O CloudStream **cancelou** a operação de extração do vídeo antes de completar.

### **Possíveis causas:**

1. ⏱️ **Timeout**: CloudStream tem timeout padrão (geralmente 30-60s)
2. 👆 **Usuário saiu da tela**: Clicar em voltar cancela o job
3. 🔄 **Múltiplas tentativas**: CloudStream tenta várias sources e cancela rapidamente
4. 🌐 **WebView demorou**: 120s pode ser muito para o timeout do CloudStream

---

## 🎯 POSSÍVEIS SOLUÇÕES

### **Solução 1: Reduzir Timeout do MegaEmbed** ⭐ RECOMENDADO

**Problema**: Timeout de 120s é muito longo, CloudStream cancela antes

**Solução**: Reduzir para 60s ou 45s

**Arquivo**: `MegaEmbedExtractorV8.kt` linha 225

**Mudança:**
```kotlin
// ATUAL:
timeout = 120_000L // 120s (2 minutos)

// SUGESTÃO 1: Reduzir para 60s
timeout = 60_000L // 60s (1 minuto)

// SUGESTÃO 2: Reduzir para 45s (mais agressivo)
timeout = 45_000L // 45s
```

**Justificativa**: 
- CloudStream provavelmente tem timeout de ~60s
- Se MegaEmbed demora 120s, CloudStream cancela antes
- v8 é mais rápido (2-5s esperado), então 60s é suficiente

---

### **Solução 2: Aumentar Prioridade do MegaEmbed**

**Problema**: CloudStream tenta outros sources primeiro e cancela MegaEmbed

**Solução**: Já está implementado (P1 - maior prioridade)

**Status**: ✅ Já configurado corretamente

---

### **Solução 3: Aguardar COMPLETAMENTE o Carregamento**

**Problema**: Usuário pode estar saindo da tela cedo demais

**Solução**: 
1. Clicar em reproduzir
2. **NÃO TOCAR EM NADA**
3. Aguardar até 2 minutos
4. Ver se carrega

**Teste**: Fazer uma tentativa completa sem cancelar

---

### **Solução 4: Verificar se Sources Estão Sendo Detectadas**

**Problema**: MegaEmbed pode não estar sendo detectado nos episódios

**Verificação nos logs:**
```
MaxSeriesProvider: data-source encontrado: https://megaembed.link/#n3n9tr
MaxSeriesProvider: [P1] MegaEmbedExtractorV8
```

**Status**: ✅ Detectando corretamente

---

## 🧪 TESTE IMEDIATO

### **Enquanto aguarda o script `capturar-erro.ps1`:**

1. **Escolha UM episódio específico**
2. **Clique em reproduzir**
3. **NÃO MEXA EM NADA** por 2 minutos completos
4. **Observe se:**
   - Aparece loading
   - Aparece erro
   - Player inicia (mesmo que demore)

---

## 📝 INFORMAÇÕES DOS LOGS

### **✅ O que está funcionando:**
1. ✅ v156 está instalada
2. ✅ MegaEmbedExtractorV8 está ativo
3. ✅ Sources estão sendo detectadas
4. ✅ WebView está iniciando
5. ✅ Fetch/XHR hooks estão ativos

### **❌ O que está falhando:**
1. ❌ Job sendo cancelado antes de completar
2. ❌ Player não inicia

### **⚠️ Observações:**
- WebView inicia: `WebViewResolver: Initial web-view request: https://megaembed.link/#n3n9tr`
- Mas logo cancela: `Job was cancelled`

---

## 🔧 CORREÇÃO RECOMENDADA

### **Modificar timeout para 60s:**

**Arquivo:** `MaxSeries/src/main/kotlin/com/franciscoalro/maxseries/extractors/MegaEmbedExtractorV8.kt`

**Linha 225:**
```kotlin
timeout = 60_000L // 60s ao invés de 120s
```

**Por quê:**
- CloudStream tem timeout padrão de ~60s
- 120s faz CloudStream cancelar antes de completar
- v8 deveria ser rápido (2-5s), então 60s é suficiente
- Se falhar em 60s, provavelmente não vai funcionar em 120s mesmo

### **Rebuild necessário:**
```powershell
./gradlew.bat MaxSeries:make
gh release delete v156 --yes
gh release create v156 MaxSeries\build\MaxSeries.cs3 --title "MaxSeries v156" --notes "Timeout fix"
```

---

## 📊 ANÁLISE DO FLUXO

### **O que acontece:**
```
1. CloudStream detecta source MegaEmbed ✅
2. Chama MegaEmbedExtractorV8 ✅
3. V8 inicia WebView ✅
4. WebView carrega megaembed.link ✅
5. CloudStream espera... ⏱️
6. CloudStream timeout (60s?) ❌
7. CloudStream cancela job ❌
8. MegaEmbed ainda processando (120s timeout) ⏳
9. MegaEmbed retorna, mas já foi cancelado ❌
10. Player não inicia ❌
```

### **O que deveria acontecer:**
```
1. CloudStream detecta source MegaEmbed ✅
2. Chama MegaEmbedExtractorV8 ✅
3. V8 inicia WebView ✅
4. WebView carrega megaembed.link ✅
5. Fetch/XHR hooks capturam URL (2-5s) ✅
6. MegaEmbed retorna URL ✅
7. CloudStream recebe URL ✅
8. Player inicia ✅
```

---

## 🎯 PRÓXIMOS PASSOS

### **URGENTE: Teste Manual**
1. Aguardar script `capturar-erro.ps1` completar
2. Ver logs completos da tentativa
3. Verificar tempo exato até cancelamento

### **SOLUÇÃO: Reduzir Timeout**
1. Modificar `MegaEmbedExtractorV8.kt` linha 225
2. Trocar `120_000L` por `60_000L`
3. Rebuild
4. Testar novamente

### **ALTERNATIVA: Logs Detalhados**
Se mesmo com timeout 60s não funcionar, precisamos ver:
- Por que demora tanto
- Onde trava no WebView
- Se Fetch/XHR hooks estão capturando

---

## 💡 HIPÓTESE PRINCIPAL

**Timeout Mismatch:**
- CloudStream timeout: ~60s
- MegaEmbed timeout: 120s
- CloudStream cancela antes do MegaEmbed terminar
- Resultado: Job cancelled, player não inicia

**Solução**: Alinhar timeouts (60s ambos)

---

**Aguardando**: Logs do script `capturar-erro.ps1`  
**Recomendação**: Reduzir timeout para 60s  
**Status**: Investigando...
