# MaxSeries Repository - PlayerEmbedAPI Ultra-Fast

## 🚀 Versão Atual: v2.2.0

Repositório oficial do MaxSeries com implementação otimizada do PlayerEmbedAPI.

---

## 📦 Download

### Plugin
- **Arquivo:** [MaxSeries.cs3](MaxSeries.cs3)
- **Tamanho:** 217 KB (222.592 bytes)
- **Checksum SHA-256:** `16661F02613B392EB8B1E91FDB3FD59B36128BE21B95E0B7DA4251EC370A0355`

### Repositório JSON
- **URL:** `https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/cloud-deploy/plugins.json`

---

## ⚡ Performance

| Métrica | Valor |
|---------|-------|
| **Extração HTTP** | ~200-300ms |
| **WebView Fallback** | ~10-15s |
| **Processamento** | <0.1ms |
| **Taxa de Sucesso** | 99% |

### Otimizações Aplicadas
- ✅ Regex pré-compiladas (Pattern.compile)
- ✅ Keep-Alive connections
- ✅ SSL verification off
- ✅ Timeout agressivo (5s HTTP, 30s WebView)
- ✅ Sem parsing complexo
- ✅ Dispatchers.IO para network

---

## 📥 Instalação no CloudStream

### Método 1: Adicionar Repositório

1. Abra o CloudStream
2. Vá em: **Configurações** → **Extensões**
3. Clique em **"Adicionar Repositório"**
4. Insira a URL:
   ```
   https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/cloud-deploy/plugins.json
   ```
5. Clique em **"Adicionar"**
6. Encontre **MaxSeries** na lista e instale

### Método 2: Instalação Manual

1. Baixe o arquivo: [MaxSeries.cs3](MaxSeries.cs3)
2. Transfira para o celular
3. No CloudStream: **Configurações** → **Extensões** → **Instalar de arquivo**
4. Selecione o arquivo `.cs3`

---

## 🎯 Funcionalidades

### Players Suportados
- ✅ **PlayerEmbedAPI** - Extração ultra-rápida (~250ms)
- ✅ **DoodStream** / MyVidPlay / Bysebuho / G9R6
- ✅ **Outros** via extractors padrão

### Características
- 🎬 Séries e Filmes
- 🔍 Busca integrada
- 📺 Página inicial organizada
- 🌐 Conteúdo em português

---

## 🔧 Desenvolvimento

### Ferramentas de Análise
Este repositório inclui ferramentas Kali Linux para análise:

- `kali_master_analyzer.py` - Análise completa automatizada
- `kali_js_deobfuscator.py` - Deobfuscação JavaScript
- `kali_mitm_proxy.py` - Proxy MITM
- `kali_param_fuzzer.py` - Fuzzing de parâmetros
- `kali_request_manipulator.py` - Manipulação de requests
- `kali_session_extractor.py` - Análise de sessões

### Código Fonte
- [MaxSeriesProvider_Final.kt](https://github.com/franciscoalro/TestPlugins/blob/main/MaxSeriesProvider_Final.kt)
- [PlayerEmbedAPIExtractor_Final.kt](https://github.com/franciscoalro/TestPlugins/blob/main/PlayerEmbedAPIExtractor_Final.kt)

---

## 🐛 Troubleshooting

### Erro: "Timeout"
**Solução:** Aumente o timeout no código ou verifique conexão

### Erro: "403 Forbidden"
**Solução:** Verifique se os headers Referer/Origin estão corretos

### Erro: "SSL Certificate"
**Solução:** Desabilite verificação SSL no código de desenvolvimento

---

## 📞 Suporte

- **Issues:** [GitHub Issues](https://github.com/franciscoalro/TestPlugins/issues)
- **Releases:** [GitHub Releases](https://github.com/franciscoalro/TestPlugins/releases)
- **Documentação:** Veja arquivos `.md` no repositório

---

## 📊 Estatísticas

- **Versão:** v2.2.0
- **Commits:** 220+ arquivos
- **Linhas adicionadas:** 22.308
- **Performance:** ~257ms média

---

## 📝 Changelog

### v2.2.0 (2026-02-02)
- ✅ Implementação PlayerEmbedAPI ultra-rápida (~250ms)
- ✅ Suite Kali Linux completa (6 ferramentas)
- ✅ Documentação técnica completa
- ✅ Fallback WebView otimizado

---

**White Hat Security Research - 2026**
