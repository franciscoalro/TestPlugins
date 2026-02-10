# ✅ Checklist de Análise - AES Key Discovery

Use este checklist para acompanhar seu progresso na descoberta da chave AES.

## 📋 Preparação

- [ ] WSL instalado e funcionando
- [ ] Navegado até o diretório do projeto
- [ ] Lido `QUICKSTART.txt` ou `README.md`
- [ ] Entendido o objetivo do projeto

## 🔧 Instalação

- [ ] Executado `bash install_dependencies.sh`
- [ ] Verificado instalação de `curl`
- [ ] Verificado instalação de `jq`
- [ ] Verificado instalação de `python3`
- [ ] Verificado instalação de `nodejs`
- [ ] (Opcional) Instalado `mitmproxy`
- [ ] (Opcional) Instalado `frida`

## ⚡ Teste Rápido

- [ ] Executado `bash quick_test.sh`
- [ ] Arquivo `output/lite.bundle.js` baixado
- [ ] Arquivo `output/quick_importkey.txt` gerado
- [ ] Arquivo `output/quick_params.txt` gerado
- [ ] Arquivo `output/quick_md5.txt` gerado
- [ ] Revisado os resultados

### Resultado do Teste Rápido

- [ ] ✅ Fórmula identificada → Pular para **Validação**
- [ ] ❌ Fórmula não identificada → Continuar para **Análise Completa**

## 🔬 Análise Completa

- [ ] Executado `bash run_analysis.sh`
- [ ] Aguardado conclusão (15-30 min)
- [ ] Arquivo `output/strings.txt` gerado
- [ ] Arquivo `output/crypto_patterns.txt` gerado
- [ ] Arquivo `output/importkey_analysis.txt` gerado
- [ ] Arquivo `output/lite_deobf.js` gerado
- [ ] Arquivo `output/key_formula.txt` gerado
- [ ] Arquivo `output/advanced_analysis.txt` gerado

### Análise dos Resultados

- [ ] Lido `output/key_formula.txt`
- [ ] Lido `output/advanced_analysis.txt`
- [ ] Procurado por "POSSÍVEIS FÓRMULAS"
- [ ] Procurado por "TESTES SUGERIDOS"
- [ ] Identificado padrões de concatenação
- [ ] Identificado funções de hash (MD5, SHA256)

### Resultado da Análise Completa

- [ ] ✅ Fórmula identificada → Pular para **Validação**
- [ ] ❌ Fórmula não identificada → Continuar para **Análise Avançada**

## 🔍 Análise Avançada (Se necessário)

### Opção A: Burp Suite

- [ ] Lido `scripts/burp_intercept.sh`
- [ ] Iniciado Burp Suite
- [ ] Configurado proxy (127.0.0.1:8080)
- [ ] Configurado navegador
- [ ] Instalado certificado CA
- [ ] Aberto PlayerEmbedAPI no navegador
- [ ] Analisado HTTP History
- [ ] Procurado por `lite.bundle.js`
- [ ] Procurado por `/api/key` ou similar
- [ ] Procurado por headers customizados
- [ ] Procurado por JSON com campo "key"
- [ ] Salvado requisições interessantes

### Opção B: mitmproxy

- [ ] Instalado mitmproxy (`pip3 install mitmproxy`)
- [ ] Executado `mitmproxy -p 8080 -s scripts/mitmproxy_capture.py`
- [ ] Configurado navegador (proxy 127.0.0.1:8080)
- [ ] Aberto PlayerEmbedAPI
- [ ] Verificado `output/mitmproxy_crypto.txt`
- [ ] Analisado capturas

### Opção C: Frida Hook

- [ ] Instalado Frida (`pip3 install frida frida-tools`)
- [ ] Iniciado Chrome
- [ ] Executado `frida -U Chrome -l scripts/frida_hook.js`
- [ ] Aberto PlayerEmbedAPI no Chrome
- [ ] Capturado logs de `crypto.subtle.importKey`
- [ ] Capturado `keyData` (hex e text)
- [ ] Analisado stack trace

### Opção D: Análise Manual

- [ ] Aberto `output/lite_deobf.js` em editor
- [ ] Procurado por `importKey`
- [ ] Procurado por `user_id`, `slug`, `md5_id`
- [ ] Procurado por `MD5` ou `SHA`
- [ ] Identificado contexto de geração da chave
- [ ] Traçado fluxo de dados

### Resultado da Análise Avançada

- [ ] ✅ Fórmula identificada → Continuar para **Validação**
- [ ] ❌ Ainda não identificada → Tentar outro método

## ✅ Validação da Fórmula

### Implementação

- [ ] Criado script de teste
- [ ] Implementado função de geração de chave
- [ ] Usado valores conhecidos:
  - `user_id = "482120"`
  - `slug = "kBJLtxCD3"`
  - `md5_id = "28930647"`

### Testes de Combinações

Testar cada combinação e marcar a que funciona:

- [ ] `MD5(user_id + slug + md5_id)`
- [ ] `MD5(user_id + md5_id + slug)`
- [ ] `MD5(slug + user_id + md5_id)`
- [ ] `MD5(slug + md5_id + user_id)`
- [ ] `MD5(md5_id + user_id + slug)`
- [ ] `MD5(md5_id + slug + user_id)`
- [ ] `MD5(user_id + ":" + slug + ":" + md5_id)`
- [ ] `SHA256(user_id + slug + md5_id)`
- [ ] `user_id + slug + md5_id` (sem hash)
- [ ] Outra: ___________________________

### Comparação

- [ ] Hash gerado corresponde à chave capturada
- [ ] Testado decriptação com a chave gerada
- [ ] Decriptação bem-sucedida

### Validação com Múltiplos Vídeos

- [ ] Testado com vídeo 1: _______________
- [ ] Testado com vídeo 2: _______________
- [ ] Testado com vídeo 3: _______________
- [ ] Fórmula funciona para todos

## 📝 Documentação

- [ ] Documentado a fórmula exata descoberta
- [ ] Documentado a ordem dos parâmetros
- [ ] Documentado o tipo de hash (MD5, SHA256, etc.)
- [ ] Documentado separadores (se houver)
- [ ] Criado função reutilizável
- [ ] Testado com casos de borda

### Fórmula Descoberta

```
Fórmula: _________________________________________________

Exemplo:
user_id = "482120"
slug = "kBJLtxCD3"
md5_id = "28930647"

Chave gerada: ____________________________________________
```

## 🎯 Implementação Final

- [ ] Criado módulo de geração de chave
- [ ] Criado módulo de decriptação
- [ ] Testado integração completa
- [ ] Tratado casos de erro
- [ ] Adicionado logging
- [ ] Documentado código

## 📊 Métricas

### Tempo Gasto

- Preparação: _____ minutos
- Teste Rápido: _____ minutos
- Análise Completa: _____ minutos
- Análise Avançada: _____ minutos
- Validação: _____ minutos
- Documentação: _____ minutos
- **Total: _____ minutos**

### Métodos Utilizados

- [ ] quick_test.sh
- [ ] run_analysis.sh
- [ ] Burp Suite
- [ ] mitmproxy
- [ ] Frida
- [ ] Wireshark
- [ ] Análise Manual

### Taxa de Sucesso

- Tentativas até descobrir: _____
- Método que funcionou: _____________________

## 🎓 Aprendizados

### O que funcionou bem?

```
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________
```

### O que poderia ser melhorado?

```
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________
```

### Dicas para próxima vez

```
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________
```

## 🏆 Conclusão

- [ ] ✅ Fórmula descoberta e validada
- [ ] ✅ Documentação completa
- [ ] ✅ Código implementado e testado
- [ ] ✅ Pronto para uso em produção

---

## 📞 Notas Adicionais

```
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________
```

---

**Data de conclusão:** ___/___/______

**Assinatura:** _____________________

---

## 🔄 Checklist Rápido (TL;DR)

Para quem quer apenas o essencial:

1. [ ] `bash install_dependencies.sh`
2. [ ] `bash quick_test.sh`
3. [ ] `bash run_analysis.sh`
4. [ ] `cat output/advanced_analysis.txt`
5. [ ] Identificar fórmula
6. [ ] Testar e validar
7. [ ] Documentar

**Tempo estimado:** 1-2 horas
**Taxa de sucesso:** 80-90%

---

## 💡 Dicas Finais

- ✅ Começar sempre pelo mais simples
- ✅ Documentar tudo durante o processo
- ✅ Testar com múltiplos vídeos
- ✅ Não desistir se o primeiro método não funcionar
- ✅ Usar múltiplos métodos em paralelo se possível
- ✅ Manter notas sobre descobertas parciais
- ✅ Comparar resultados entre diferentes métodos

**Boa sorte! 🚀**
