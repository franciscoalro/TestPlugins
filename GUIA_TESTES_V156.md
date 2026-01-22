# 🧪 GUIA DE TESTES: MaxSeries v156

## 🎯 Objetivo dos Testes

Validar que a versão v156 do MegaEmbed V8 realmente melhora:
1. ✅ Taxa de sucesso na captura de URLs
2. ✅ Tempo de carregamento
3. ✅ Compatibilidade com diferentes formatos de URL
4. ✅ Resiliência a timeouts

---

## 📋 PRÉ-REQUISITOS

### **Ferramentas Necessárias**
- [x] CloudStream3 instalado no dispositivo Android
- [x] ADB configurado no PC (opcional, mas recomendado)
- [x] Conexão WiFi estável
- [x] Pelo menos 30 minutos disponíveis

### **Preparação**
1. Instalar MaxSeries v156 no CloudStream3
2. Verificar versão instalada: Settings → Extensions → MaxSeries → deve mostrar "v156"
3. Conectar dispositivo via ADB (opcional)
4. Abrir terminal/PowerShell para logs

---

## 🧪 BATERIA DE TESTES

### **TESTE 1: Verificação de Versão** ⭐ OBRIGATÓRIO
**Objetivo**: Garantir que v156 está instalada

**Passos**:
1. Abrir CloudStream3
2. Settings → Extensions
3. Procurar "MaxSeries"
4. Verificar versão

**Resultado Esperado**:
```
✅ Versão: 156
✅ Descrição: "MegaEmbed V8 com Fetch/XHR Hooks"
```

**Tempo**: 1 minuto

---

### **TESTE 2: Cache Hit (Baseline)** ⭐
**Objetivo**: Verificar que cache continua funcionando

**Passos**:
1. Escolher qualquer episódio
2. Reproduzir até aparecer o player
3. Voltar e reproduzir novamente

**Resultado Esperado**:
```
✅ Segunda reprodução: < 1s (cache)
```

**Logs Esperados** (via ADB):
```
D/MegaEmbedV8: ✅ CACHE HIT: https://...
```

**Tempo**: 2 minutos

---

### **TESTE 3: URLs com Query Strings** ⭐⭐⭐ CRÍTICO
**Objetivo**: Validar que novo regex captura URLs com parâmetros

**Passos**:
1. Escolher episódio que usa MegaEmbed
2. Reproduzir
3. Verificar logs

**URLs que DEVEM ser capturadas agora**:
```
✅ https://host.com/v4/ab/123456/index?token=abc
✅ https://host.com/v4/ab/123456/cf-master.txt?signature=xyz
✅ https://host.com/v4/ab/123456/playlist.m3u8?auth=123&token=abc
```

**Logs Esperados**:
```
D/MegaEmbedV8: 📜 Script capturou: https://...?token=...
D/MegaEmbedV8: ✅ URL válida (200): https://...
```

**Resultado Esperado**:
```
✅ Reprodução iniciada com sucesso
✅ URL com query string capturada
```

**Tempo**: 3 minutos

---

### **TESTE 4: URLs Sem Extensão** ⭐⭐⭐ CRÍTICO
**Objetivo**: Validar que regex captura URLs sem .txt/.m3u8

**Passos**:
1. Escolher episódio diferente
2. Reproduzir
3. Verificar logs para URL sem extensão

**URLs que DEVEM ser capturadas agora**:
```
✅ https://host.com/v4/ab/123456/
✅ https://host.com/v4/ab/123456/index
✅ https://host.com/v4/ab/123456/playlist
```

**Logs Esperados**:
```
D/MegaEmbedV8: 📜 Script capturou: https://.../v4/.../... (sem .txt/.m3u8)
D/MegaEmbedV8: ✅ URL válida (200)
```

**Resultado Esperado**:
```
✅ Reprodução iniciada mesmo sem extensão visível
```

**Tempo**: 3 minutos

---

### **TESTE 5: Fetch/XHR Interception** ⭐⭐⭐ CRÍTICO
**Objetivo**: Validar que hooks estão funcionando

**Passos**:
1. Escolher episódio aleatório
2. Reproduzir
3. Procurar nos logs por mensagens de interceptação

**Logs Esperados**:
```
D/MegaEmbedV8: === MEGAEMBED V8 v156 FETCH/XHR INTERCEPTION ===
D/MegaEmbedV8: 🌐 Iniciando WebView com FETCH/XHR INTERCEPTION...
D/MegaEmbedV8: 📜 Script capturou: https://...
```

**Verificação**:
- [ ] Mensagem "FETCH/XHR INTERCEPTION" aparece
- [ ] URL foi capturada via script (não via rede)
- [ ] Tempo de captura < 5s

**Tempo**: 3 minutos

---

### **TESTE 6: Performance - 10 Episódios** ⭐⭐ IMPORTANTE
**Objetivo**: Medir tempo médio de carregamento

**Passos**:
1. Escolher 10 episódios diferentes
2. Para cada episódio:
   - Marcar tempo de início
   - Reproduzir
   - Marcar tempo quando vídeo inicia
   - Anotar tempo total

**Planilha de Resultados**:
```
| Episódio | Tempo (V7 esperado) | Tempo (V8 real) | Melhoria |
|----------|---------------------|-----------------|----------|
| 1        | 8-15s               | __________s     | ______%  |
| 2        | 8-15s               | __________s     | ______%  |
| 3        | 8-15s               | __________s     | ______%  |
| 4        | 8-15s               | __________s     | ______%  |
| 5        | 8-15s               | __________s     | ______%  |
| 6        | 8-15s               | __________s     | ______%  |
| 7        | 8-15s               | __________s     | ______%  |
| 8        | 8-15s               | __________s     | ______%  |
| 9        | 8-15s               | __________s     | ______%  |
| 10       | 8-15s               | __________s     | ______%  |
| MÉDIA    | ~11.5s              | __________s     | ______%  |
```

**Resultado Esperado**:
```
✅ Média V8: 2-5 segundos
✅ Melhoria: > 60%
```

**Tempo**: 15 minutos

---

### **TESTE 7: Taxa de Sucesso** ⭐⭐⭐ CRÍTICO
**Objetivo**: Medir quantos episódios reproduzem com sucesso

**Passos**:
1. Escolher 20 episódios aleatórios
2. Tentar reproduzir cada um
3. Marcar sucesso ou falha

**Planilha de Resultados**:
```
| # | Episódio              | Sucesso | Tempo | Observação |
|---|-----------------------|---------|-------|------------|
| 1 | _________________     | ☐ Sim   | ___s  |            |
| 2 | _________________     | ☐ Sim   | ___s  |            |
| 3 | _________________     | ☐ Sim   | ___s  |            |
...
| 20| _________________     | ☐ Sim   | ___s  |            |

Taxa de Sucesso: ____% (meta: > 95%)
```

**Resultado Esperado**:
```
✅ Taxa de sucesso: > 95% (19/20 ou 20/20)
✅ V7 esperado: ~70% (14/20)
✅ Melhoria: +36%
```

**Tempo**: 20 minutos

---

### **TESTE 8: Timeout Estendido** ⭐⭐
**Objetivo**: Verificar que timeout de 120s funciona

**Passos**:
1. Simular conexão lenta (se possível)
2. Reproduzir episódio
3. Aguardar até 2 minutos se necessário

**Resultado Esperado**:
```
✅ Não deve dar timeout antes de 120s
✅ V7 daria timeout em 60s
```

**Logs Esperados** (se der timeout):
```
D/MegaEmbedV8: ⏱️ Timeout após 120s
```

**Tempo**: 5 minutos

---

### **TESTE 9: Fallbacks Múltiplos** ⭐⭐
**Objetivo**: Verificar que fallbacks funcionam

**Passos**:
1. Escolher episódio problemático (se souber de algum)
2. Reproduzir
3. Verificar logs para ver qual estratégia funcionou

**Logs Esperados**:
```
D/MegaEmbedV8: 📜 Script capturou: null (primeira tentativa falhou)
D/MegaEmbedV8: 🔍 URL da rede: ... (segunda tentativa funcionou)
OU
D/MegaEmbedV8: ⚠️ Tentando fallback via HTML...
D/MegaEmbedV8: ✅ Encontrado no HTML: https://...
```

**Resultado Esperado**:
```
✅ Reprodução iniciada mesmo com primeira tentativa falhando
✅ Estratégia de fallback documentada nos logs
```

**Tempo**: 5 minutos

---

### **TESTE 10: Diferentes CDNs** ⭐⭐
**Objetivo**: Validar compatibilidade com múltiplos CDNs

**CDNs Conhecidos**:
```
1. valenium.shop
2. veritasholdings.cyou
3. srcf.*
4. soq6.*
5. Outros que aparecerem
```

**Passos**:
1. Reproduzir episódios de diferentes séries
2. Verificar qual CDN foi usado (via logs)
3. Marcar sucesso/falha por CDN

**Planilha**:
```
| CDN                     | Tentativas | Sucessos | Taxa |
|-------------------------|------------|----------|------|
| valenium.shop           | ___        | ___      | ___% |
| veritasholdings.cyou    | ___        | ___      | ___% |
| outros                  | ___        | ___      | ___% |
```

**Resultado Esperado**:
```
✅ Taxa de sucesso > 90% em TODOS os CDNs
```

**Tempo**: 10 minutos

---

## 📊 ANÁLISE DE RESULTADOS

### **Métricas a Calcular**

**1. Taxa de Sucesso Geral**
```
Taxa = (Sucessos / Total de Tentativas) × 100%
Meta: > 95%
```

**2. Tempo Médio de Carregamento**
```
Tempo Médio = Σ(Tempos) / N
Meta: < 5s
```

**3. Melhoria vs V7**
```
Melhoria% = ((Tempo V7 - Tempo V8) / Tempo V7) × 100%
Meta: > 60%
```

**4. Taxa de Fallback**
```
Taxa Fallback = (Sucessos via Fallback / Total Sucessos) × 100%
Info: Quanto menor, melhor (script principal funcionando)
```

---

## ✅ CHECKLIST DE VALIDAÇÃO

### **Validação Mínima** (Obrigatório)
- [ ] Teste 1: Versão verificada (v156)
- [ ] Teste 3: URLs com query strings funcionam
- [ ] Teste 5: Fetch/XHR interception ativo
- [ ] Teste 7: Taxa de sucesso > 95%

### **Validação Completa** (Recomendado)
- [ ] Todos os 10 testes executados
- [ ] Planilhas preenchidas
- [ ] Métricas calculadas
- [ ] Comparação com V7 documentada

---

## 📝 TEMPLATE DE RELATÓRIO

```markdown
# RELATÓRIO DE TESTES: MaxSeries v156

**Data**: _______________
**Testador**: _______________
**Dispositivo**: _______________
**CloudStream3 Version**: _______________

## Resultados Gerais

- Taxa de Sucesso: ____% (meta: > 95%)
- Tempo Médio: ____s (meta: < 5s)
- Melhoria vs V7: ____% (meta: > 60%)

## Testes Executados

### Teste 1: Verificação de Versão
- [ ] Passou
- Versão instalada: ___

### Teste 3: URLs com Query Strings
- [ ] Passou
- URLs capturadas: ___

### Teste 5: Fetch/XHR Interception
- [ ] Passou
- Observações: ___

### Teste 7: Taxa de Sucesso (20 episódios)
- [ ] Passou
- Sucessos: ___/20
- Taxa: ___%

## Problemas Encontrados

1. ___________________
2. ___________________

## Observações Adicionais

___________________

## Conclusão

- [ ] ✅ V156 aprovado para produção
- [ ] ⚠️ V156 precisa de ajustes
- [ ] ❌ V156 não passou nos testes

**Assinatura**: _______________
```

---

## 🐛 TROUBLESHOOTING

### **Problema: Versão não atualiza**
**Solução**:
1. Settings → Extensions → Remove MaxSeries
2. Reinstalar do repositório
3. Verificar versão novamente

### **Problema: Logs não aparecem**
**Solução**:
```powershell
# Verificar se ADB está conectado
adb devices

# Tentar comando diferente
adb logcat -s MegaEmbedV8
```

### **Problema: Taxa de sucesso baixa**
**Solução**:
1. Verificar conexão de internet
2. Testar com séries diferentes
3. Verificar se v156 realmente foi instalada

---

## 📞 REPORTAR RESULTADOS

Se encontrar problemas ou tiver resultados:

1. **GitHub Issues**: https://github.com/franciscoalro/TestPlugins/issues
2. Incluir:
   - Relatório completo de testes
   - Logs via ADB
   - Screenshots (se possível)
   - Versões (MaxSeries, CloudStream3, Android)

---

**Boa sorte com os testes! 🧪✨**
