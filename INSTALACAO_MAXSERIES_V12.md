# 🚀 MaxSeries v12 - Guia de Instalação

## ✅ Status: DISPONÍVEL PARA DOWNLOAD

O MaxSeries v12 foi compilado com sucesso e está pronto para instalação!

## 📦 Download Direto

### **Link de Download:**
```
https://github.com/franciscoalro/TestPlugins/releases/download/v12.0/MaxSeries.cs3
```

## 🔧 Como Instalar

### **Passo a Passo:**
1. **Baixe o arquivo**: Clique no link acima
2. **Abra CloudStream** → Configurações → Extensões
3. **Instalar extensão** → Selecione o arquivo `MaxSeries.cs3`
4. **Ative a extensão** na lista
5. **Teste** com filmes e séries

## 🎯 Melhorias na v12

### **✅ Detecção Robusta de Episódios:**
- **Múltiplos métodos**: DooPlay padrão + estruturas alternativas
- **Análise inteligente**: Detecta episódios no conteúdo da página
- **Numeração correta**: Extrai números de temporada/episódio automaticamente
- **Fallback inteligente**: Cria estrutura padrão quando necessário

### **🔍 Logs Detalhados:**
```
📺 Analisando série: [Nome da Série]
🎬 Processando temporada 1
✅ Episódio adicionado: T1E1 - Episódio 1
✅ Total de episódios encontrados: 10
```

### **🛠️ Estruturas Suportadas:**
- **DooPlay padrão**: `div.se-c` com `ul.episodios`
- **Listas alternativas**: `.episode-list`, `.episodes`
- **Links diretos**: URLs com "episodio" ou "episode"
- **Análise de texto**: Detecta padrões no conteúdo

## 🧪 Como Testar

### **Para Séries:**
1. Busque uma série no MaxSeries
2. Clique na série
3. **Verifique**: Episódios devem aparecer com números corretos (não só "Episódio 1")
4. **Observe**: Temporadas separadas se disponível
5. Teste a reprodução

### **Para Filmes:**
1. Busque um filme
2. Clique no filme
3. **Verifique**: Players aparecem (#1 Dublado, #2 Legendado, etc.)
4. Teste a reprodução

## 📋 O Que Esperar

### **✅ Séries Funcionando:**
- Episódios listados corretamente
- Números de temporada/episódio precisos
- Não mais "Episódio 1" para tudo
- Estrutura organizada

### **✅ Filmes Funcionando:**
- Múltiplos players detectados
- Links de vídeo encontrados
- Reprodução funcional

## 🐛 Se Ainda Não Funcionar

### **Verifique os Logs:**
Procure por estas mensagens no CloudStream:
```
📺 Analisando série: [Nome]
🎬 Processando temporada X
✅ Episódio adicionado: TXeY - [Título]
🔄 Tentando estrutura alternativa
⚠️ Nenhum episódio encontrado, criando estrutura padrão
```

### **Possíveis Problemas:**
1. **Cache antigo**: Limpe cache do CloudStream
2. **Versão incorreta**: Certifique-se que é v12
3. **Site mudou**: Estrutura pode ter sido alterada

### **Reportar Problemas:**
Se ainda não funcionar, forneça:
- Nome específico da série/filme testado
- Logs do CloudStream (se possível)
- Comportamento observado vs esperado

## 🎉 Conclusão

O MaxSeries v12 implementa:
- ✅ **Detecção robusta** de episódios e temporadas
- ✅ **Múltiplos métodos** de análise
- ✅ **Logs detalhados** para debug
- ✅ **Fallback inteligente** para casos especiais
- ✅ **Compatibilidade** com diferentes estruturas do site

**Instale agora e teste!** 🚀

---

**Download**: https://github.com/franciscoalro/TestPlugins/releases/download/v12.0/MaxSeries.cs3  
**Repositório**: https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/plugins.json  
**Versão**: 12  
**Data**: 2026-01-08