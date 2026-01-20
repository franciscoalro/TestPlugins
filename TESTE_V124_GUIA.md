# Guia de Teste - MaxSeries v124

## 📱 Pré-requisitos
- ✅ Dispositivo Android conectado via ADB
- ✅ CloudStream instalado
- ✅ MaxSeries v124 disponível no repositório

## 🔧 Passo 1: Atualizar Plugin no CloudStream

### No CloudStream:
1. Abra **CloudStream**
2. Vá em **Configurações** → **Extensões**
3. Encontre **MaxSeries**
4. Clique em **Atualizar** (deve mostrar v124)
5. Aguarde download e instalação

**OU**

### Instalação Manual:
1. Baixe: https://github.com/franciscoalro/TestPlugins/releases/download/v124.0/MaxSeries.cs3
2. Abra CloudStream
3. Configurações → Extensões → Instalar de arquivo
4. Selecione MaxSeries.cs3

## 🔍 Passo 2: Iniciar Monitoramento ADB

### No PowerShell:
```powershell
cd C:\Users\KYTHOURS\Desktop\brcloudstream

# Limpar logs antigos
D:\Android\platform-tools\adb.exe logcat -c

# Iniciar monitoramento em tempo real
D:\Android\platform-tools\adb.exe logcat -v time | Select-String "PlayerEmbedAPI|sssrr|MaxSeries|ExtractorLink"
```

**Deixe este terminal aberto!**

## 🎬 Passo 3: Testar Reprodução

### No CloudStream:
1. Busque: **"Terra de Pecados"** (ou qualquer série)
2. Selecione um episódio
3. Clique em **Play**
4. Aguarde carregar (até 30 segundos)

## 📊 Passo 4: Analisar Logs

### O que procurar nos logs:

#### ✅ SUCESSO - Deve aparecer:
```
PlayerEmbedAPI: Iniciando extração...
PlayerEmbedAPI: Iniciando captura WebView
sssrr.org/sora/
PlayerEmbedAPI: AES-CTR capturou HLS
ExtractorLink: https://...sssrr.org/...
```

#### ❌ FALHA - Se aparecer:
```
Timeout
Falha ao interceptar URL
Final: https://playerembedapi.link/?v=...
```

## 🐛 Passo 5: Capturar Logs Completos

Se houver problemas:

```powershell
# Capturar últimos 1000 linhas
D:\Android\platform-tools\adb.exe logcat -v time -d -t 1000 > adb_debug_v124.txt
```

Envie o arquivo `adb_debug_v124.txt` para análise.

## 🎯 Resultados Esperados

### Cenário 1: ✅ SUCESSO (v124 funciona)
- Vídeo carrega em até 30 segundos
- Logs mostram URLs `sssrr.org`
- Reprodução inicia normalmente

### Cenário 2: ⚠️ TIMEOUT (ainda há problema)
- Vídeo não carrega após 30 segundos
- Logs mostram "Timeout" ou "Falha ao interceptar"
- URL final é `playerembedapi.link` (não chegou no sssrr.org)

### Cenário 3: ❌ ERRO (outro problema)
- Erro antes de chegar no PlayerEmbedAPI
- Problema na busca ou carregamento de episódios
- Erro de rede ou servidor

## 📝 Checklist de Teste

- [ ] CloudStream atualizado para v124
- [ ] ADB conectado e monitorando
- [ ] Episódio selecionado
- [ ] Aguardado 30 segundos
- [ ] Logs capturados
- [ ] Resultado documentado

## 🔄 Próximos Passos

### Se v124 FUNCIONAR:
✅ Problema resolvido!
✅ PlayerEmbedAPI agora intercepta sssrr.org corretamente

### Se v124 NÃO FUNCIONAR:
1. Capturar logs completos
2. Analisar por que WebView não intercepta sssrr.org
3. Considerar abordagens alternativas:
   - Aumentar timeout para 45s
   - Melhorar script de captura JavaScript
   - Adicionar mais padrões de URL ao regex

---

**Versão**: 124  
**Data**: 18/01/2026  
**Correção**: Regex sssrr.org (CDN real)
