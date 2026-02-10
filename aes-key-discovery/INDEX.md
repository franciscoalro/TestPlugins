# 📑 Índice de Documentação

## 🚀 Início Rápido

| Arquivo | Descrição | Para quem? |
|---------|-----------|------------|
| **[QUICKSTART.txt](QUICKSTART.txt)** | Referência visual rápida | Todos |
| **[README.md](README.md)** | Visão geral do projeto | Todos |
| **[SUMMARY.md](SUMMARY.md)** | Resumo executivo | Gestores, Pesquisadores |

## 📚 Documentação Detalhada

| Arquivo | Descrição | Para quem? |
|---------|-----------|------------|
| **[USAGE.md](USAGE.md)** | Guia completo de uso | Usuários técnicos |
| **[EXAMPLES.md](EXAMPLES.md)** | Exemplos práticos passo a passo | Iniciantes |
| **[INDEX.md](INDEX.md)** | Este arquivo | Navegação |

## 🛠️ Scripts Executáveis

### Windows

| Arquivo | Descrição | Uso |
|---------|-----------|-----|
| **[run_wsl.bat](run_wsl.bat)** | Launcher principal | `run_wsl.bat` |

### Linux/WSL

| Arquivo | Descrição | Uso |
|---------|-----------|-----|
| **[install_dependencies.sh](install_dependencies.sh)** | Instalar dependências | `bash install_dependencies.sh` |
| **[quick_test.sh](quick_test.sh)** | Teste rápido (5 min) | `bash quick_test.sh` |
| **[run_analysis.sh](run_analysis.sh)** | Análise completa (15-30 min) | `bash run_analysis.sh` |

## 📜 Scripts de Análise

Localização: `scripts/`

### Análise Estática

| Script | Descrição | Linguagem |
|--------|-----------|-----------|
| **extract_strings.sh** | Extrai strings relevantes | Bash |
| **find_crypto_patterns.sh** | Procura padrões de crypto | Bash |
| **analyze_importkey.sh** | Analisa crypto.subtle.importKey | Bash |
| **deobfuscate.js** | Deobfusca JavaScript | Node.js |
| **find_key_formula.py** | Identifica fórmula da chave | Python |
| **advanced_analysis.py** | Análise avançada de padrões | Python |

### Análise Dinâmica

| Script | Descrição | Ferramenta |
|--------|-----------|------------|
| **burp_intercept.sh** | Guia de uso do Burp Suite | Burp Suite |
| **mitmproxy_capture.py** | Script de captura | mitmproxy |
| **wireshark_filter.sh** | Guia de filtros | Wireshark |
| **frida_hook.js** | Hook em crypto.subtle | Frida |

## 📊 Arquivos de Saída

Localização: `output/` (gerado automaticamente)

| Arquivo | Descrição | Importância |
|---------|-----------|-------------|
| **key_formula.txt** | Fórmula básica identificada | ⭐⭐⭐⭐ |
| **advanced_analysis.txt** | Análise detalhada | ⭐⭐⭐⭐⭐ |
| **lite_deobf.js** | JavaScript deobfuscado | ⭐⭐⭐ |
| **crypto_patterns.txt** | Padrões de crypto | ⭐⭐⭐ |
| **importkey_analysis.txt** | Análise de importKey | ⭐⭐⭐ |
| **strings.txt** | Strings extraídas | ⭐⭐ |
| **lite.bundle.js** | Bundle original | ⭐ |

## 🎯 Fluxos de Trabalho

### Para Iniciantes

```
1. Ler: QUICKSTART.txt
2. Executar: run_wsl.bat (Windows) ou quick_test.sh (Linux)
3. Ler: output/key_formula.txt
4. Se não encontrar: Ler EXAMPLES.md
5. Executar: run_analysis.sh
6. Ler: output/advanced_analysis.txt
```

### Para Usuários Intermediários

```
1. Ler: README.md
2. Instalar: bash install_dependencies.sh
3. Executar: bash run_analysis.sh
4. Analisar: output/advanced_analysis.txt
5. Se necessário: Usar Burp Suite ou mitmproxy
6. Validar: Testar fórmula descoberta
```

### Para Usuários Avançados

```
1. Ler: SUMMARY.md
2. Executar: bash run_analysis.sh
3. Analisar: output/lite_deobf.js manualmente
4. Hook dinâmico: frida -U Chrome -l scripts/frida_hook.js
5. Interceptar: mitmproxy -s scripts/mitmproxy_capture.py
6. Validar: Implementar decriptação completa
```

## 📖 Guia de Leitura por Objetivo

### Objetivo: Entender o projeto

```
1. README.md          - Visão geral
2. SUMMARY.md         - Resumo executivo
3. USAGE.md           - Como usar
```

### Objetivo: Executar análise rápida

```
1. QUICKSTART.txt     - Referência rápida
2. quick_test.sh      - Executar teste
3. output/key_formula.txt - Ver resultado
```

### Objetivo: Análise completa

```
1. USAGE.md           - Guia completo
2. install_dependencies.sh - Instalar deps
3. run_analysis.sh    - Executar análise
4. output/advanced_analysis.txt - Ver resultado
```

### Objetivo: Aprender técnicas

```
1. EXAMPLES.md        - Exemplos práticos
2. scripts/*.py       - Ver código Python
3. scripts/*.js       - Ver código Node.js
4. scripts/*.sh       - Ver scripts Bash
```

### Objetivo: Análise avançada

```
1. USAGE.md (seção avançada)
2. scripts/burp_intercept.sh
3. scripts/mitmproxy_capture.py
4. scripts/frida_hook.js
5. EXAMPLES.md (cenários 3-5)
```

## 🔍 Busca Rápida

### Procurando por...

**Como instalar?**
→ `install_dependencies.sh` ou `USAGE.md` (seção Pré-requisitos)

**Como executar?**
→ `QUICKSTART.txt` ou `README.md` (seção Início Rápido)

**Exemplos práticos?**
→ `EXAMPLES.md`

**Problemas/Erros?**
→ `USAGE.md` (seção Troubleshooting) ou `EXAMPLES.md` (seção Troubleshooting)

**Entender o código?**
→ `scripts/` (ver código-fonte dos scripts)

**Resultados da análise?**
→ `output/advanced_analysis.txt` (após executar `run_analysis.sh`)

**Usar Burp Suite?**
→ `scripts/burp_intercept.sh` ou `EXAMPLES.md` (Cenário 3)

**Usar mitmproxy?**
→ `scripts/mitmproxy_capture.py` ou `EXAMPLES.md` (Cenário 4)

**Usar Frida?**
→ `scripts/frida_hook.js` ou `EXAMPLES.md` (Cenário 5)

**Análise manual?**
→ `EXAMPLES.md` (Cenário 6)

## 📞 Suporte

### Documentação
- Guia completo: `USAGE.md`
- Exemplos: `EXAMPLES.md`
- Resumo: `SUMMARY.md`

### Problemas Técnicos
- WSL: https://docs.microsoft.com/windows/wsl/
- Burp Suite: https://portswigger.net/burp/documentation
- mitmproxy: https://docs.mitmproxy.org/
- Frida: https://frida.re/docs/

## 🎓 Recursos de Aprendizado

### Criptografia
- Web Crypto API: https://developer.mozilla.org/en-US/docs/Web/API/Web_Crypto_API
- AES: https://en.wikipedia.org/wiki/Advanced_Encryption_Standard

### Reverse Engineering
- JavaScript Deobfuscation: https://github.com/javascript-obfuscator/javascript-obfuscator
- Frida: https://frida.re/docs/javascript-api/

### Análise de Rede
- Burp Suite: https://portswigger.net/burp/documentation
- mitmproxy: https://docs.mitmproxy.org/stable/

## 📊 Estatísticas do Projeto

### Arquivos
- Documentação: 6 arquivos
- Scripts executáveis: 3 arquivos (Windows/Linux)
- Scripts de análise: 10 arquivos
- Total: 19 arquivos

### Linhas de Código
- Bash: ~500 linhas
- Python: ~800 linhas
- JavaScript: ~200 linhas
- Total: ~1500 linhas

### Métodos de Análise
- Estática: 6 métodos
- Dinâmica: 4 métodos
- Total: 10 métodos

## 🏆 Checklist de Sucesso

- [ ] Ler `QUICKSTART.txt` ou `README.md`
- [ ] Instalar dependências (`install_dependencies.sh`)
- [ ] Executar teste rápido (`quick_test.sh`)
- [ ] Executar análise completa (`run_analysis.sh`)
- [ ] Ler `output/advanced_analysis.txt`
- [ ] Identificar fórmula candidata
- [ ] Testar fórmula com valores conhecidos
- [ ] Validar com múltiplos vídeos
- [ ] Documentar descoberta

## 🎯 Próximos Passos

1. **Começar**: Ler `QUICKSTART.txt`
2. **Executar**: `run_wsl.bat` (Windows) ou `bash quick_test.sh` (Linux)
3. **Analisar**: Ver `output/key_formula.txt`
4. **Aprofundar**: Se necessário, ler `USAGE.md` e `EXAMPLES.md`
5. **Validar**: Testar fórmula descoberta

---

**Dúvidas?** Consulte a documentação apropriada acima ou veja a seção de Suporte.

**Pronto para começar?** Vá para `QUICKSTART.txt` ou execute `run_wsl.bat`!
