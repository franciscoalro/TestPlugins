# Como Criar GitHub Release v56.0 Manualmente

## 🎯 RESUMO
O código MaxSeries v56 foi enviado para o GitHub com sucesso, mas o GitHub Release precisa ser criado manualmente.

## ✅ O QUE JÁ FOI FEITO
- ✅ Código MaxSeries v56 commitado e enviado
- ✅ plugins.json atualizado para v56
- ✅ MaxSeries.cs3 gerado (128,164 bytes)
- ✅ Documentação criada

## 📋 PASSOS PARA CRIAR O RELEASE

### Opção 1: Interface Web do GitHub
1. Acesse: https://github.com/franciscoalro/TestPlugins/releases
2. Clique em "Create a new release"
3. Preencha os campos:

**Tag version**: `v56.0`
**Release title**: `MaxSeries v56 - Critical AnimesOnlineCC Fixes`
**Description**:
```
## 🔧 MaxSeries v56 - Critical AnimesOnlineCC Fixes

### ✅ CORREÇÕES CRÍTICAS APLICADAS:
- **Tratamento de erro robusto**: Try/catch em todas as funções principais
- **Logs detalhados**: Log.d() ao invés de println() para debug no Android
- **Busca de imagem robusta**: Suporte a src, data-src, data-lazy-src, data-original
- **URLs consistentes**: Uso de fixUrl() e fixUrlNull() em todos os lugares
- **Melhor busca de elementos**: Seletores mais robustos para título e poster
- **Suporte híbrido**: Funciona com formato MaxSeries e AnimesOnlineCC de episódios

### 🎯 BASEADO NO ANIMESONLINECC FUNCIONANDO:
- Estrutura de error handling idêntica ao AnimesOnlineCC
- Padrões de busca de elementos similares
- Logs detalhados para facilitar troubleshooting
- Tratamento robusto de URLs e imagens

### 📱 DEVE RESOLVER:
- **Problema principal**: Conteúdo não aparecendo no CloudStream app
- **Logs vazios**: Agora com logs detalhados para debug
- **Imagens quebradas**: Busca robusta em múltiplos atributos
- **URLs malformadas**: fixUrl() consistente

### 🔍 TESTE AUTOMATIZADO:
```
🌐 Site: https://www.maxseries.one ✅ (Status: 200)
🔍 Seletor 'div.items article.item': ✅ (36 itens encontrados)
🎬 Página de filmes: ✅ (1 filme encontrado)
📺 Página de séries: ✅ (42 séries encontradas)
🔍 Pesquisa: ✅ (funcional)
```

**Site**: https://www.maxseries.one/
**Filtro YouTube**: ✅ Ativo
**Extractors**: DoodStream, MegaEmbed, PlayerEmbedAPI
```

4. **Upload do arquivo**: Arraste o arquivo `MaxSeries.cs3` para a área de assets
5. Clique em "Publish release"

### Opção 2: Linha de Comando (se GitHub CLI estiver instalado)
```powershell
gh release create v56.0 MaxSeries.cs3 --title "MaxSeries v56 - Critical AnimesOnlineCC Fixes" --notes-file RELEASE_NOTES_V56.txt
```

## 🔗 LINKS IMPORTANTES
- **Repositório**: https://github.com/franciscoalro/TestPlugins
- **Releases**: https://github.com/franciscoalro/TestPlugins/releases
- **plugins.json**: https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/plugins.json

## ✅ VERIFICAÇÃO FINAL
Após criar o release, verificar:
1. ✅ Release v56.0 aparece na lista
2. ✅ Arquivo MaxSeries.cs3 está disponível para download
3. ✅ URL no plugins.json está correta: `https://github.com/franciscoalro/TestPlugins/releases/download/v56.0/MaxSeries.cs3`

## 🎯 RESULTADO ESPERADO
Com o release v56.0 criado, o CloudStream poderá baixar e instalar a versão v56 do MaxSeries, que deve resolver o problema de conteúdo não aparecer no app.