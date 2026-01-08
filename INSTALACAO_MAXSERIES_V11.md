# 🚀 MaxSeries v11 - Guia de Instalação

## ✅ Status: PRONTO PARA INSTALAÇÃO

O MaxSeries v11 foi compilado com sucesso e está disponível para download!

## 📦 Links de Download

### **Opção 1: Download Direto (RECOMENDADO)**
```
https://github.com/franciscoalro/TestPlugins/releases/download/v11.0/MaxSeries.cs3
```

### **Opção 2: Via Repositório CloudStream**
URL do repositório: `https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/plugins.json`

## 🔧 Como Instalar

### **Método 1: Download Direto**
1. **Baixe o arquivo**: Clique no link acima ou acesse:
   - GitHub → franciscoalro/TestPlugins → Releases → v11.0 → MaxSeries.cs3

2. **Instale no CloudStream**:
   - Abra CloudStream
   - Vá em **Configurações** → **Extensões** → **Instalar extensão**
   - Selecione o arquivo `MaxSeries.cs3` baixado
   - Aguarde a instalação

3. **Ative a extensão**:
   - Vá em **Configurações** → **Extensões**
   - Encontre "MaxSeries" na lista
   - Certifique-se que está **ativado**

### **Método 2: Via Repositório**
1. **Adicione o repositório**:
   - CloudStream → **Configurações** → **Extensões** → **Adicionar repositório**
   - Cole: `https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/plugins.json`

2. **Instale o MaxSeries**:
   - Vá em **Extensões** → **Repositórios**
   - Encontre "MaxSeries v11"
   - Clique em **Instalar**

## 🎯 O Que Foi Corrigido na v11

### ✅ Problemas Resolvidos:
- **"Em breve" nas séries**: Episódios agora são listados corretamente
- **Links não encontrados**: Detecta players ViewPlayer com botões data-source
- **Múltiplos players**: Suporte para #1, #2, #3 Dublado/Legendado
- **Estrutura moderna**: Compatível com playerembedapi.link, megaembed.link, myvidplay.com

### 🔧 Melhorias Técnicas:
- Detecção específica do ViewPlayer iframe
- Extração de botões com `data-source`
- Análise de scripts `gleam.config` e `jwplayer`
- Logs detalhados para debug
- Múltiplos métodos de fallback

## 🧪 Como Testar

### **Teste com Filmes:**
1. Busque por um filme no MaxSeries
2. Clique no filme
3. Verifique se aparecem players: "#1 Dublado", "#2 Legendado", etc.
4. Teste a reprodução

### **Teste com Séries:**
1. Busque por uma série
2. Clique na série
3. Verifique se os episódios são listados (não "Em breve")
4. Clique em um episódio e teste a reprodução

## 📋 Informações da Versão

- **Versão**: 11
- **Compatibilidade**: CloudStream 3.x
- **Idioma**: Português (pt-BR)
- **Tipos**: Séries (TvSeries) e Filmes (Movie)
- **Site**: maxseries.one

## 🐛 Se Ainda Não Funcionar

### **Logs para Verificar:**
Procure por estas mensagens nos logs do CloudStream:
```
📺 Carregando player iframe: https://viewplayer.online/...
🎯 Player encontrado: #1 Dublado -> https://playerembedapi.link/...
🎬 Script de configuração encontrado
✅ Total de links encontrados: X
```

### **Possíveis Problemas:**
1. **Cache antigo**: Limpe o cache do CloudStream
2. **Versão antiga**: Certifique-se que instalou a v11
3. **Site mudou**: O MaxSeries pode ter alterado a estrutura

### **Reportar Problemas:**
Se ainda não funcionar, forneça:
- Logs do CloudStream
- Nome do filme/série testado
- Mensagens de erro específicas

## 🎉 Conclusão

O MaxSeries v11 foi especificamente desenvolvido para resolver os problemas que você relatou:
- ✅ Séries não mostram mais "Em breve"
- ✅ Filmes encontram links de vídeo
- ✅ Suporte para múltiplos players
- ✅ Compatível com a estrutura atual do site

**Instale agora e teste!** 🚀

---

**Download**: https://github.com/franciscoalro/TestPlugins/releases/download/v11.0/MaxSeries.cs3  
**Repositório**: https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/plugins.json