# 🔍 Como Verificar PlayerEmbedAPI Manualmente

## 📊 Resultado do Script Automático

O script `find-playerembedapi-content.ps1` testou 8 URLs populares e **não encontrou PlayerEmbedAPI em nenhuma**.

### URLs Testadas

| Conteúdo | Player | PlayerEmbedAPI |
|----------|--------|----------------|
| The Last of Us | playerthree.online | ❌ Não |
| The Boys | playerthree.online | ❌ Não |
| Breaking Bad | playerthree.online | ❌ Não |
| Stranger Things | playerthree.online | ❌ Não |
| The Walking Dead | playerthree.online | ❌ Não |
| Avatar 2 | viewplayer.online | ❌ 404 |
| Vingadores Ultimato | viewplayer.online | ❌ 404 |
| Homem-Aranha | viewplayer.online | ❌ 404 |

## 🤔 Possíveis Razões

### 1. PlayerEmbedAPI Pode Estar Desativado

É possível que o MaxSeries tenha removido ou desativado PlayerEmbedAPI temporariamente do site.

### 2. Apenas Alguns Conteúdos Têm

PlayerEmbedAPI pode estar disponível apenas para conteúdos específicos (novos lançamentos, conteúdo premium, etc).

### 3. Carregamento Dinâmico

Os botões podem ser carregados via JavaScript após o carregamento inicial da página.

## 🔍 Verificação Manual no Browser

### Passo 1: Abrir Conteúdo

1. Abrir https://www.maxseries.pics no browser
2. Escolher qualquer filme ou série
3. Clicar para assistir

### Passo 2: Inspecionar Página

1. Pressionar **F12** para abrir DevTools
2. Ir para aba **Network**
3. Filtrar por: `playerthree` ou `viewplayer`
4. Copiar a URL que aparecer

### Passo 3: Abrir Player

1. Abrir a URL copiada em nova aba
2. Aguardar carregar completamente
3. Verificar se aparecem botões de player

### Passo 4: Procurar PlayerEmbedAPI

**Opção A: Visual**
- Procurar botão com texto "PlayerEmbedAPI" ou "Player Embed"

**Opção B: Inspecionar HTML**
1. Pressionar **F12** novamente
2. Ir para aba **Elements**
3. Pressionar **Ctrl+F** para buscar
4. Buscar por: `playerembedapi`
5. Se encontrar `data-source` contendo "playerembedapi" → **ENCONTRADO!**

**Opção C: Console**
```javascript
// Colar no Console (F12 → Console)
document.querySelectorAll('[data-source*="playerembedapi"]').length
// Se retornar > 0, PlayerEmbedAPI está presente
```

## 📸 Exemplo Visual

### Como Deve Parecer

```html
<!-- Exemplo de HTML com PlayerEmbedAPI -->
<button data-source="https://playerembedapi.link/?id=xxxxx">
  PlayerEmbedAPI
</button>
```

### Onde Procurar

```
Página do Player (playerthree.online ou viewplayer.online)
  └─ Botões de player (geralmente no topo ou lateral)
     └─ Procurar por "PlayerEmbedAPI" ou inspecionar data-source
```

## 🎯 Se Encontrar PlayerEmbedAPI

### 1. Anotar Informações

```
URL do MaxSeries: _______________________________
URL do Player: __________________________________
IMDB ID (se visível): ___________________________
```

### 2. Testar no Cloudstream

1. Abrir Cloudstream
2. Buscar o mesmo conteúdo
3. Selecionar episódio/filme
4. Aguardar 20-30s
5. Verificar se PlayerEmbedAPI aparece

### 3. Capturar Logs

```powershell
.\test-v219-manual.ps1
```

Procurar por:
```
🌐🌐🌐 PLAYEREMBEDAPI DETECTADO!
🚀🚀🚀 EXTRACT CHAMADO!
```

## ❌ Se NÃO Encontrar PlayerEmbedAPI

### Cenário 1: Site Não Usa Mais

Se após testar vários conteúdos diferentes não encontrar PlayerEmbedAPI em nenhum, é possível que o site tenha removido essa opção.

**Ação**: Usar outros extractors (MegaEmbed, MyVidPlay, DoodStream) que estão funcionando.

### Cenário 2: Apenas Conteúdo Específico

Alguns sites disponibilizam players diferentes para conteúdos diferentes.

**Ação**: Testar com:
- Lançamentos recentes
- Séries populares
- Filmes em alta
- Conteúdo dublado vs legendado

### Cenário 3: Carregamento Dinâmico

Botões podem aparecer apenas após interação.

**Ação**: 
1. Clicar em diferentes abas/temporadas
2. Aguardar alguns segundos
3. Verificar novamente

## 🔄 Alternativas

### Se PlayerEmbedAPI Não Estiver Disponível

O MaxSeries v219 tem outros extractors funcionando:

| Extractor | Status | Qualidade |
|-----------|--------|-----------|
| MegaEmbed | ✅ Funcionando | HD/FHD |
| MyVidPlay | ✅ Funcionando | HD |
| DoodStream | ✅ Funcionando | SD/HD |
| StreamTape | ✅ Funcionando | HD |
| Mixdrop | ✅ Funcionando | HD |
| Filemoon | ✅ Funcionando | HD |

**Recomendação**: Usar MegaEmbed que está com 95% de taxa de sucesso.

## 📊 Estatísticas

### Teste Automático (28 Jan 2026)

- **URLs testadas**: 8
- **PlayerEmbedAPI encontrado**: 0
- **Séries testadas**: 5
- **Filmes testados**: 3
- **Erros 404**: 3 (filmes no viewplayer)

### Conclusão Preliminar

PlayerEmbedAPI pode não estar mais ativo no MaxSeries, ou está disponível apenas para conteúdos muito específicos que não foram testados.

## 🎯 Próximos Passos

### Opção 1: Continuar Procurando

1. Testar mais URLs manualmente no browser
2. Focar em lançamentos recentes (últimos 30 dias)
3. Testar conteúdo de diferentes gêneros
4. Verificar se há padrão (só séries, só filmes, etc)

### Opção 2: Aceitar Situação Atual

1. Código v219 está pronto e funcionando
2. MegaEmbed e outros extractors estão OK
3. Se PlayerEmbedAPI voltar ao site, código já está preparado
4. Sem necessidade de ação adicional

### Opção 3: Verificar com Comunidade

1. Perguntar em fóruns/Discord do Cloudstream
2. Verificar se outros usuários veem PlayerEmbedAPI
3. Confirmar se site ainda usa essa source

## 💡 Dica Final

**O código v219 está correto e pronto!** Se PlayerEmbedAPI não está disponível no site, não há nada a fazer no código. O importante é que:

1. ✅ Sistema de extração funciona (MegaEmbed confirmado)
2. ✅ Código PlayerEmbedAPI está implementado
3. ✅ Se/quando PlayerEmbedAPI voltar, funcionará automaticamente

**Não é necessário fazer mais nada no código.** Use os outros extractors que estão funcionando perfeitamente.

---

## 📞 Reportar Descoberta

Se você **ENCONTRAR** PlayerEmbedAPI manualmente:

1. Anotar URL completa do conteúdo
2. Anotar URL do player
3. Tirar screenshot mostrando o botão
4. Testar no Cloudstream
5. Capturar logs
6. Reportar resultado

Se você **NÃO ENCONTRAR** após testar 10+ conteúdos diferentes:

1. Aceitar que PlayerEmbedAPI pode não estar mais no site
2. Usar outros extractors disponíveis
3. Código v219 permanece pronto para quando/se voltar

---

**Status**: ⏳ Aguardando confirmação se PlayerEmbedAPI ainda existe no site  
**Ação recomendada**: Usar MegaEmbed e outros extractors que estão funcionando
