# 🔄 Atualizar MaxSeries para v209

## ⚠️ Problema: Aplicativo mostra v207

Se o Cloudstream ainda mostra MaxSeries v207, siga estes passos:

---

## 🔧 Solução 1: Atualizar pelo Cloudstream

### Passo a Passo

1. **Abrir Cloudstream**
2. **Ir em Configurações** (⚙️)
3. **Selecionar Extensões**
4. **Encontrar MaxSeries**
5. **Clicar em "Atualizar"** ou **"Update"**
6. **Aguardar download**
7. **Reiniciar Cloudstream**

**Resultado:** MaxSeries v209 instalado

---

## 🔧 Solução 2: Desinstalar e Reinstalar

### Passo a Passo

1. **Abrir Cloudstream**
2. **Ir em Configurações** → **Extensões**
3. **Encontrar MaxSeries v207**
4. **Clicar em "Desinstalar"** ou **"Uninstall"**
5. **Confirmar desinstalação**
6. **Aguardar alguns segundos**
7. **Clicar em "Instalar"** ou **"Install"** novamente
8. **Aguardar download**
9. **Reiniciar Cloudstream**

**Resultado:** MaxSeries v209 instalado

---

## 🔧 Solução 3: Limpar Cache do Repositório

### Passo a Passo

1. **Abrir Cloudstream**
2. **Ir em Configurações** → **Extensões**
3. **Encontrar o repositório** (TestPlugins Repository)
4. **Clicar e segurar** (long press)
5. **Selecionar "Remover"** ou **"Remove"**
6. **Confirmar remoção**
7. **Adicionar repositório novamente:**
   ```
   https://raw.githubusercontent.com/franciscoalro/TestPlugins/builds/repo.json
   ```
8. **Instalar MaxSeries v209**
9. **Reiniciar Cloudstream**

**Resultado:** MaxSeries v209 instalado

---

## 🔧 Solução 4: Limpar Cache do Aplicativo

### Android

1. **Ir em Configurações do Android**
2. **Aplicativos** → **Cloudstream**
3. **Armazenamento**
4. **Limpar Cache** (NÃO limpar dados)
5. **Abrir Cloudstream**
6. **Ir em Extensões**
7. **Atualizar MaxSeries**

**Resultado:** Cache limpo, v209 disponível

---

## 🔧 Solução 5: Download Direto (Manual)

### Passo a Passo

1. **Baixar MaxSeries.cs3:**
   ```
   https://github.com/franciscoalro/TestPlugins/releases/download/v209/MaxSeries.cs3
   ```

2. **No Cloudstream:**
   - Configurações → Extensões
   - Desinstalar MaxSeries v207
   - Clicar em **+** (adicionar)
   - Selecionar o arquivo **MaxSeries.cs3** baixado
   - Aguardar instalação

3. **Reiniciar Cloudstream**

**Resultado:** MaxSeries v209 instalado manualmente

---

## ✅ Verificar Versão Instalada

### Como Confirmar

1. **Abrir Cloudstream**
2. **Ir em Configurações** → **Extensões**
3. **Encontrar MaxSeries**
4. **Verificar número da versão**

**Deve mostrar:** MaxSeries v209

---

## 🎯 Diferenças v207 vs v209

### v207 (Antiga)
- 9 categorias
- 6 gêneros
- 3 extractors
- ~80% taxa de sucesso

### v209 (Nova) ⭐
- **24 categorias** (+166%)
- **23 gêneros** (+283%)
- **7+1 extractors** (+133%)
- **~99% taxa de sucesso** (+19%)

**Novos Extractors:**
- ✨ DoodStream
- ✨ StreamTape
- ✨ Mixdrop
- ✨ Filemoon

**Nova Categoria:**
- ✨ Em Alta (Trending)

---

## 🐛 Problemas Comuns

### "Não consigo atualizar"
**Solução:** Use Solução 2 (Desinstalar e Reinstalar)

### "Ainda mostra v207 após atualizar"
**Solução:** Use Solução 4 (Limpar Cache) ou Solução 5 (Download Direto)

### "Erro ao baixar"
**Solução:** 
- Verifique conexão com internet
- Tente novamente após alguns minutos
- Use Solução 5 (Download Direto)

### "Arquivo não instala"
**Solução:**
- Verifique espaço de armazenamento
- Desinstale v207 primeiro
- Reinicie o Cloudstream

---

## 📊 Validação

### Após Atualizar, Teste:

1. **Verificar versão:**
   - Deve mostrar v209

2. **Verificar categorias:**
   - Deve ter 24 categorias
   - Deve ter "Em Alta"

3. **Testar reprodução:**
   - Buscar "Breaking Bad"
   - Selecionar episódio
   - Testar reprodução
   - Deve funcionar (~99% sucesso)

---

## 🎉 Conclusão

Após seguir uma das soluções acima, você terá:
- ✅ MaxSeries v209 instalado
- ✅ 24 categorias disponíveis
- ✅ 7 extractors funcionando
- ✅ ~99% taxa de sucesso
- ✅ Melhor experiência de streaming

**Aproveite a nova versão! 🍿**

---

## 📞 Suporte

Se ainda tiver problemas:
- **GitHub Issues:** https://github.com/franciscoalro/TestPlugins/issues
- **Informe:** Versão do Cloudstream, mensagem de erro, passos realizados

---

**Desenvolvido por:** franciscoalro  
**Data:** 26 Janeiro 2026  
**Versão:** 209
