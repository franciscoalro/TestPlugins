# 📱 Guia de Instalação e Teste - BRCloudstream

## 🎯 Objetivo

Instalar e testar todos os 7 providers brasileiros no Cloudstream.

---

## 📋 Pré-requisitos

- ✅ Cloudstream 3.x instalado no Android
- ✅ Conexão com internet
- ✅ Espaço de armazenamento (~10MB)

---

## 🚀 Método 1: Via Repositório (Recomendado)

### Passo 1: Adicionar Repositório

1. Abra o **Cloudstream**
2. Vá em **Configurações** (⚙️)
3. Selecione **Extensões**
4. Clique em **Adicionar Repositório** (+)
5. Cole a URL:
   ```
   https://raw.githubusercontent.com/franciscoalro/brcloudstream/builds/repo.json
   ```
6. Clique em **OK**

### Passo 2: Instalar Providers

1. Na lista de extensões, você verá:
   - ⭐ **MaxSeries v209** (recomendado)
   - AnimesOnlineCC
   - MegaFlix
   - NetCine
   - OverFlix
   - PobreFlix
   - Vizer

2. Clique em cada provider que deseja instalar
3. Clique em **Instalar**
4. Aguarde o download e instalação

### Passo 3: Ativar Providers

1. Após instalação, os providers aparecerão na tela inicial
2. Selecione os que deseja usar
3. Pronto! Já pode começar a assistir

---

## 📦 Método 2: Instalação Manual

### Para cada provider:

1. Baixe o arquivo `.cs3` do GitHub:
   - [MaxSeries.cs3](https://github.com/franciscoalro/brcloudstream/releases/download/v209/MaxSeries.cs3)
   - [AnimesOnlineCC.cs3](https://github.com/franciscoalro/brcloudstream/releases/download/v1.0.0/AnimesOnlineCC.cs3)
   - [MegaFlix.cs3](https://github.com/franciscoalro/brcloudstream/releases/download/v1.0.0/MegaFlix.cs3)
   - [NetCine.cs3](https://github.com/franciscoalro/brcloudstream/releases/download/v1.0.0/NetCine.cs3)
   - [OverFlix.cs3](https://github.com/franciscoalro/brcloudstream/releases/download/v1.0.0/OverFlix.cs3)
   - [PobreFlix.cs3](https://github.com/franciscoalro/brcloudstream/releases/download/v1.0.0/PobreFlix.cs3)
   - [Vizer.cs3](https://github.com/franciscoalro/brcloudstream/releases/download/v1.0.0/Vizer.cs3)

2. No Cloudstream:
   - Vá em **Configurações** → **Extensões**
   - Clique em **+** (adicionar)
   - Selecione o arquivo `.cs3` baixado
   - Aguarde instalação

---

## 🧪 Testes Recomendados

### Teste 1: MaxSeries v209 (Principal)

#### 1.1 Testar Categorias
```
1. Abrir MaxSeries
2. Verificar categorias disponíveis:
   - Início
   - Em Alta ⭐ (novo)
   - Filmes
   - Séries
   - 20 gêneros diferentes
3. Navegar por cada categoria
```

**Resultado esperado:** ✅ Todas as 24 categorias carregam conteúdo

#### 1.2 Testar Busca
```
1. Clicar na lupa (🔍)
2. Buscar: "Breaking Bad"
3. Verificar resultados
```

**Resultado esperado:** ✅ Resultados aparecem rapidamente

#### 1.3 Testar Reprodução
```
1. Selecionar uma série (ex: "Breaking Bad")
2. Escolher um episódio
3. Clicar em "Assistir"
4. Aguardar carregamento
```

**Resultado esperado:** ✅ Vídeo carrega e reproduz

#### 1.4 Testar Extractors
```
1. Durante reprodução, verificar qual extractor está sendo usado
2. Se falhar, tentar outro episódio
3. Verificar logs (se disponível)
```

**Extractors disponíveis:**
- MegaEmbed V9 (~95% sucesso)
- PlayerEmbedAPI (~90% sucesso)
- MyVidPlay (~85% sucesso)
- DoodStream (~80% sucesso)
- StreamTape (~75% sucesso)
- Mixdrop (~70% sucesso)
- Filemoon (~65% sucesso)

**Resultado esperado:** ✅ ~99% dos vídeos funcionam

---

### Teste 2: AnimesOnlineCC

```
1. Abrir AnimesOnlineCC
2. Buscar um anime popular (ex: "Naruto")
3. Selecionar episódio
4. Testar reprodução
```

**Resultado esperado:** ✅ Anime carrega e reproduz

---

### Teste 3: Outros Providers

Repetir processo para:
- MegaFlix
- NetCine
- OverFlix
- PobreFlix
- Vizer

**Resultado esperado:** ✅ Todos funcionam

---

## 🐛 Troubleshooting

### Problema: "Extensão não instalada"
**Solução:**
1. Verificar se o arquivo `.cs3` está correto
2. Tentar baixar novamente
3. Verificar espaço de armazenamento

### Problema: "Vídeo não carrega"
**Solução:**
1. Verificar conexão com internet
2. Tentar outro episódio
3. Tentar outro provider
4. Aguardar alguns segundos (pode estar carregando)

### Problema: "Erro 404" ao adicionar repositório
**Solução:**
1. Verificar se a URL está correta
2. Verificar se o branch `builds` existe no GitHub
3. Tentar método de instalação manual

### Problema: "Provider não aparece na lista"
**Solução:**
1. Atualizar lista de extensões (puxar para baixo)
2. Reiniciar Cloudstream
3. Verificar se o repositório foi adicionado corretamente

---

## 📊 Checklist de Validação

### MaxSeries v209
- [ ] Instalação bem-sucedida
- [ ] 24 categorias visíveis
- [ ] Busca funcionando
- [ ] Vídeo reproduz (testar 3 diferentes)
- [ ] Múltiplos extractors funcionando

### AnimesOnlineCC
- [ ] Instalação bem-sucedida
- [ ] Animes aparecem
- [ ] Vídeo reproduz

### MegaFlix
- [ ] Instalação bem-sucedida
- [ ] Conteúdo carrega
- [ ] Vídeo reproduz

### NetCine
- [ ] Instalação bem-sucedida
- [ ] Filmes e animes aparecem
- [ ] Vídeo reproduz

### OverFlix
- [ ] Instalação bem-sucedida
- [ ] Conteúdo carrega
- [ ] Vídeo reproduz

### PobreFlix
- [ ] Instalação bem-sucedida
- [ ] Busca funcionando
- [ ] Vídeo reproduz

### Vizer
- [ ] Instalação bem-sucedida
- [ ] Conteúdo carrega
- [ ] Vídeo reproduz

---

## 📈 Métricas de Sucesso

### Instalação
- **Meta:** 100% dos providers instalam sem erro
- **Tempo:** < 30 segundos por provider

### Reprodução
- **Meta:** ≥ 95% dos vídeos reproduzem
- **Tempo de carregamento:** < 10 segundos

### Experiência
- **Meta:** Interface responsiva
- **Meta:** Busca rápida (< 3 segundos)

---

## 🎯 Providers Recomendados por Tipo

### Para Séries e Filmes
1. **MaxSeries v209** ⭐ (melhor opção)
2. MegaFlix
3. PobreFlix
4. Vizer

### Para Animes
1. **AnimesOnlineCC** ⭐
2. NetCine

### Para Tudo
1. **MaxSeries v209** ⭐
2. NetCine

---

## 📝 Relatório de Teste

Após testar, preencha:

```
Data: __/__/____
Versão Cloudstream: _______
Dispositivo: _______

MaxSeries v209:
- Instalação: [ ] OK [ ] Falhou
- Categorias: [ ] OK [ ] Falhou
- Busca: [ ] OK [ ] Falhou
- Reprodução: [ ] OK [ ] Falhou
- Taxa de sucesso: ____%
- Observações: _______

[Repetir para outros providers]

Conclusão:
[ ] Todos funcionando perfeitamente
[ ] Alguns problemas (especificar)
[ ] Problemas graves (especificar)
```

---

## 🆘 Suporte

**GitHub Issues:**
https://github.com/franciscoalro/brcloudstream/issues

**Informações úteis para reportar:**
- Versão do Cloudstream
- Provider com problema
- Mensagem de erro (se houver)
- Passos para reproduzir

---

## ✅ Conclusão

Após seguir este guia, você terá:
- ✅ 7 providers brasileiros instalados
- ✅ Acesso a milhares de filmes e séries
- ✅ Múltiplas opções de extractors
- ✅ Melhor experiência de streaming

**Aproveite! 🎉**

---

**Desenvolvido por:** franciscoalro  
**Data:** 26 Janeiro 2026  
**Versão:** 1.0.0
