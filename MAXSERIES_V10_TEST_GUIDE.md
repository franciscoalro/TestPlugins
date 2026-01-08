# 🧪 Guia de Teste - MaxSeries v10

## 📋 Checklist de Teste

### ✅ Pré-requisitos
- [ ] Build do GitHub Actions completado
- [ ] Plugin MaxSeries v10 disponível para download
- [ ] CloudStream atualizado para versão compatível
- [ ] Repositório atualizado no CloudStream

### 🔍 Testes de Funcionalidade

#### 1. **Teste de Instalação**
- [ ] Plugin aparece na lista do repositório
- [ ] Download e instalação sem erros
- [ ] Plugin ativo na lista de extensões

#### 2. **Teste de Busca e Navegação**
- [ ] Busca por séries funciona
- [ ] Resultados aparecem corretamente
- [ ] Páginas principais carregam (Home, Séries, Filmes)

#### 3. **Teste de Séries (CRÍTICO)**
- [ ] Séries aparecem na busca
- [ ] Ao clicar em uma série, episódios são listados
- [ ] Episódios não mostram "Em breve"
- [ ] Números de temporada/episódio corretos

#### 4. **Teste de Reprodução (CRÍTICO)**
- [ ] Ao clicar em um episódio, players aparecem
- [ ] Links de vídeo são encontrados
- [ ] Reprodução funciona sem erros
- [ ] Qualidade de vídeo adequada

#### 5. **Teste de Filmes**
- [ ] Filmes aparecem na busca
- [ ] Links de vídeo são encontrados para filmes
- [ ] Reprodução de filmes funciona

## 🔧 Debug e Troubleshooting

### Logs Importantes para Verificar

```
📺 Carregando episódios do iframe: https://...
✅ Encontrados X episódios para [SÉRIE]
📺 Processando episódio: Season=X, Episode=Y
🔄 Tentando endpoint: /episode/X/Y
✅ Resposta do endpoint: {...}
🎯 URL encontrada na resposta: https://...
```

### Problemas Esperados e Soluções

#### ❌ "Nenhum episódio encontrado"
**Possíveis causas:**
- Iframe não encontrado
- Estrutura HTML mudou
- JavaScript bloqueado

**Debug:**
```
⚠️ Tentando método padrão DooPlay
❌ Erro ao carregar episódios do iframe
```

#### ❌ "Nenhum link de vídeo encontrado"
**Possíveis causas:**
- Endpoints AJAX mudaram
- Headers incorretos
- Bloqueio de requests

**Debug:**
```
⚠️ Endpoint /episode/X/Y falhou
❌ Erro no player AJAX
```

#### ❌ Links encontrados mas não reproduzem
**Possíveis causas:**
- URLs inválidas
- Referer incorreto
- Formato não suportado

## 🛠️ Comandos de Teste

### Teste Manual de URLs
```bash
# Testar se o repositório está acessível
curl -s "https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/plugins.json" | jq .

# Verificar se o arquivo .cs3 existe
curl -I "https://github.com/franciscoalro/TestPlugins/releases/download/v10.0/MaxSeries.cs3"
```

### Teste de Estrutura HTML
```javascript
// No console do navegador, em uma página de série do MaxSeries
console.log("Episódios encontrados:", document.querySelectorAll('li[data-season-id][data-episode-id]').length);
console.log("Scripts de player:", document.querySelectorAll('script[src*="app.js"], script[src*="jwplayer"]').length);
```

## 📊 Métricas de Sucesso

### ✅ Sucesso Total
- Episódios listados corretamente
- Links de vídeo encontrados
- Reprodução funcional
- Sem erros nos logs

### ⚠️ Sucesso Parcial
- Episódios listados mas alguns links falham
- Alguns players funcionam, outros não
- Logs mostram tentativas de fallback

### ❌ Falha
- "Em breve" ainda aparece
- Nenhum link encontrado
- Erros constantes nos logs

## 🔄 Próximos Passos Baseados nos Resultados

### Se Funcionar ✅
1. Testar com múltiplas séries
2. Verificar diferentes tipos de conteúdo
3. Documentar séries que funcionam bem

### Se Falhar Parcialmente ⚠️
1. Analisar logs específicos
2. Identificar padrões de falha
3. Ajustar endpoints ou headers

### Se Falhar Completamente ❌
1. Verificar se a estrutura HTML mudou
2. Analisar o JavaScript do site
3. Considerar abordagem alternativa

## 📝 Relatório de Teste

**Data:** ___________
**Versão:** MaxSeries v10
**Testador:** ___________

### Resultados:
- [ ] ✅ Funcionando perfeitamente
- [ ] ⚠️ Funcionando parcialmente
- [ ] ❌ Não funcionando

### Observações:
```
[Descrever problemas encontrados, logs relevantes, etc.]
```

### Séries Testadas:
1. _________________ - Status: _______
2. _________________ - Status: _______
3. _________________ - Status: _______

---

**Próxima ação:** ___________________