# Guia de Teste - MaxSeries v126

## 📅 Data: 18/01/2026

## 🎯 O Que Foi Mudado

### MegaEmbed v5.2 - WebView Melhorado
- ✅ **Timeout**: 60s → **120s** (aguardar descriptografia)
- ✅ **tryPlay()**: Força play do vídeo a cada 1s
- ✅ **Pattern 6**: Busca em atributos do player (`data-src`, `data-url`, `src`)
- ✅ **Código limpo**: Removido duplicação

## 📋 Passo a Passo

### 1. Instalar v126
```powershell
# No diretório brcloudstream
adb install -r MaxSeries\build\MaxSeries.cs3
```

**Resultado esperado**:
```
Success
```

### 2. Iniciar Monitoramento
```powershell
.\monitor-v126.ps1
```

**O que vai aparecer**:
```
=== MONITOR MAXSERIES V126 ===
WebView Melhorado: 120s timeout + tryPlay + Pattern 6

Dispositivo conectado: Y9YP4XI7799P9LZT

=== MONITORANDO LOGS ===
```

### 3. Testar no App

1. Abrir **CloudStream** no celular
2. Ir em **Configurações** → **Extensões**
3. Verificar: **MaxSeries v126** instalado
4. Voltar para tela inicial
5. Buscar: **"Terra de Pecados"**
6. Selecionar série
7. Clicar em **Episódio 1**
8. Tentar reproduzir

### 4. Analisar Logs

#### ✅ SUCESSO - MegaEmbed
```
MegaEmbedExtractorV5_v126: === MEGAEMBED V5 ALL STRATEGIES (v126) ===
MegaEmbedExtractorV5_v126: 🆔 VideoId: 3wnuij
MegaEmbedExtractorV5_v126: 🔍 [3/5] Tentando WebView JavaScript-Only...
MegaEmbedExtractorV5_v126: 📜 JS Callback capturou: https://.../.txt
MegaEmbedExtractorV5_v126: 🎯 WebView JS capturou: https://.../.txt
MegaEmbedExtractorV5_v126: ✅ WebView JavaScript funcionou!
MaxSeriesProvider: ✅ ExtractorLink criado: MegaEmbed - Auto
```

#### ✅ SUCESSO - PlayerEmbedAPI
```
PlayerEmbedAPIExtractor_v3.3: === PLAYEREMBEDAPI V3 (v124) ===
PlayerEmbedAPIExtractor_v3.3: 🔍 Capturando com WebView...
PlayerEmbedAPIExtractor_v3.3: ✅ Capturado: https://htm4jbxon18.sssrr.org/...
MaxSeriesProvider: ✅ ExtractorLink criado: PlayerEmbedAPI
```

#### ❌ FALHA - Timeout
```
MegaEmbedExtractorV5_v126: 🔍 [3/5] Tentando WebView JavaScript-Only...
MegaEmbedExtractorV5_v126: ⚠️ WebView JS: Nenhuma URL capturada
MegaEmbedExtractorV5_v126: 🔍 [4/5] Tentando WebView com Interceptação...
MegaEmbedExtractorV5_v126: ❌ FALHA: Todas as 5 estratégias falharam
```

## 🔍 Diagnóstico

### Cenário 1: MegaEmbed Funciona
✅ **v126 resolveu o problema!**
- WebView aguardou descriptografia
- URL capturada com sucesso
- Vídeo deve reproduzir

### Cenário 2: MegaEmbed Timeout (120s)
❌ **Problema persiste**
- JavaScript não está descriptografando
- Ou URL não está sendo injetada no DOM
- **Próximo passo**: Reverse engineering da descriptografia

### Cenário 3: PlayerEmbedAPI Funciona
✅ **Alternativa funcionando**
- sssrr.org capturado
- Vídeo deve reproduzir

### Cenário 4: Ambos Falham
❌ **Problema crítico**
- Usuário não consegue assistir NADA
- **Próximo passo**: Investigar mudanças no site

## 📊 Comparação de Timeouts

| Versão | MegaEmbed | PlayerEmbedAPI | Resultado |
|--------|-----------|----------------|-----------|
| v124 | 60s | 30s | ❌ Ambos timeout |
| v125 | 60s | 30s | ❌ API criptografada |
| v126 | **120s** | 30s | ⏳ Testando... |

## 🚀 Próximos Passos

### Se v126 Funcionar:
1. ✅ Marcar como estável
2. ✅ Documentar solução
3. ✅ Monitorar por 1 semana

### Se v126 Falhar:
1. ❌ Reverse engineering da descriptografia
2. ❌ Ou implementar solução híbrida
3. ❌ Ou considerar usar Playwright/Selenium externo

## 📝 Notas

- **tryPlay()**: Pode acelerar carregamento forçando play
- **120s**: Tempo máximo razoável (2 minutos)
- **Pattern 6**: Busca direta em atributos do player
- **5 estratégias**: Tenta TUDO antes de falhar

---

**Versão**: 126  
**Status**: Aguardando teste  
**Prioridade**: Alta (usuário não consegue assistir)
