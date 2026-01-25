# ✅ URL Correta para Cloudstream - MaxSeries v210

## 🎯 URL DO REPOSITÓRIO

Use esta URL EXATA no Cloudstream:

```
https://raw.githubusercontent.com/franciscoalro/TestPlugins/builds/plugins.json
```

⚠️ **IMPORTANTE:** Use `plugins.json` diretamente, NÃO use `repo.json`!

---

## 📱 Como Adicionar no Cloudstream

### Passo a Passo

1. **Abrir Cloudstream**

2. **Ir em Configurações** (⚙️)

3. **Selecionar "Extensões"**

4. **Remover TODOS os repositórios antigos:**
   - Para cada repositório na lista
   - Clicar e segurar (long press)
   - Selecionar "Remover" ou "Delete"
   - Confirmar

5. **Adicionar novo repositório:**
   - Clicar em **+** (Adicionar Repositório)
   - Colar EXATAMENTE:
     ```
     https://raw.githubusercontent.com/franciscoalro/TestPlugins/builds/plugins.json
     ```
   - Clicar **OK**

6. **Aguardar carregar** (pode demorar 10-30 segundos)

7. **Verificar providers disponíveis:**
   - Deve mostrar 7 providers
   - MaxSeries deve mostrar **v210**

8. **Instalar MaxSeries v210**

9. **Reiniciar Cloudstream**

---

## ✅ Verificação

Após adicionar o repositório, você deve ver:

### 7 Providers Disponíveis:
1. ✅ **MaxSeries v210** (principal)
2. ✅ AnimesOnlineCC v1
3. ✅ MegaFlix v1
4. ✅ NetCine v1
5. ✅ OverFlix v1
6. ✅ PobreFlix v1
7. ✅ Vizer v1

### MaxSeries v210 Deve Ter:
- ✅ Versão: 210
- ✅ Descrição: "7 Extractors + 25 Categories"
- ✅ Tamanho: ~191 KB

---

## 🔧 Se Não Aparecer

### Solução 1: Aguardar Cache do GitHub
- Aguarde 2-3 minutos
- Remova o repositório
- Adicione novamente
- Tente instalar

### Solução 2: Limpar Cache do Cloudstream
1. Configurações do Android
2. Aplicativos → Cloudstream
3. Armazenamento
4. **Limpar Cache** (NÃO limpar dados)
5. Abrir Cloudstream
6. Adicionar repositório novamente

### Solução 3: Download Direto (Mais Confiável)

Se o repositório não funcionar, baixe diretamente:

1. **No navegador do celular:**
   ```
   https://github.com/franciscoalro/TestPlugins/releases/download/v210/MaxSeries.cs3
   ```

2. **No Cloudstream:**
   - Configurações → Extensões
   - Clicar em **+** (adicionar)
   - Selecionar arquivo **MaxSeries.cs3** baixado
   - Aguardar instalação

3. **Reiniciar Cloudstream**

---

## 📊 Comparação de URLs

### ❌ URLs que NÃO FUNCIONAM
```
https://raw.githubusercontent.com/franciscoalro/TestPlugins/builds/repo.json
https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/plugins.json
https://raw.githubusercontent.com/franciscoalro/brcloudstream/builds/repo.json
```

### ✅ URL que FUNCIONA
```
https://raw.githubusercontent.com/franciscoalro/TestPlugins/builds/plugins.json
```

---

## 🎯 Por Que Usar plugins.json Diretamente?

O Cloudstream espera um **array de plugins** diretamente, não um objeto com `pluginLists`.

**Formato Correto (plugins.json):**
```json
[
  {
    "name": "MaxSeries",
    "version": 210,
    ...
  },
  ...
]
```

**Formato Incorreto para Cloudstream (repo.json):**
```json
{
  "name": "Repository",
  "pluginLists": ["..."]
}
```

---

## ✅ Teste Rápido

Para confirmar que a URL está correta, abra no navegador:

```
https://raw.githubusercontent.com/franciscoalro/TestPlugins/builds/plugins.json
```

Você deve ver:
- ✅ Um array JSON começando com `[`
- ✅ 7 objetos de providers
- ✅ MaxSeries com version: 210

---

## 🎉 Resultado Final

Após usar a URL correta, você terá:
- ✅ 7 providers disponíveis
- ✅ MaxSeries v210 instalado
- ✅ 25 categorias (incluindo "Adicionados Recentemente")
- ✅ 7 extractors funcionando
- ✅ ~99% taxa de sucesso

---

## 📞 Suporte

Se ainda tiver problemas:
- **GitHub:** https://github.com/franciscoalro/TestPlugins/issues
- **Release v210:** https://github.com/franciscoalro/TestPlugins/releases/tag/v210

---

**Use a URL correta e MaxSeries v210 funcionará perfeitamente! 🎯**

---

**Desenvolvido por:** franciscoalro  
**Data:** 26 Janeiro 2026  
**Versão:** 210
