# 🔧 Solução: MaxSeries Continua v207

## ⚠️ Problema
Mesmo após limpar cache e dados, o Cloudstream continua instalando MaxSeries v207 em vez de v210.

---

## 🎯 Causa Provável

O Cloudstream está usando um **repositório antigo** que ainda aponta para v207. Existem 2 repositórios possíveis:

1. **Repositório Antigo (v207):**
   ```
   https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/plugins.json
   ```

2. **Repositório Novo (v210):**
   ```
   https://raw.githubusercontent.com/franciscoalro/TestPlugins/builds/repo.json
   ```

---

## ✅ Solução Definitiva

### Passo 1: Desinstalar Completamente

1. **Abrir Cloudstream**
2. **Configurações → Extensões**
3. **Encontrar MaxSeries v207**
4. **Desinstalar** (Uninstall)
5. **Confirmar**

### Passo 2: Remover TODOS os Repositórios

1. **Ainda em Extensões**
2. **Ver lista de repositórios**
3. **Para CADA repositório:**
   - Clicar e segurar (long press)
   - Selecionar "Remover" ou "Delete"
   - Confirmar
4. **Garantir que NENHUM repositório reste**

### Passo 3: Adicionar Repositório Correto

1. **Clicar em + (Adicionar Repositório)**
2. **Colar EXATAMENTE esta URL:**
   ```
   https://raw.githubusercontent.com/franciscoalro/TestPlugins/builds/repo.json
   ```
3. **Clicar OK**
4. **Aguardar carregar**

### Passo 4: Instalar MaxSeries v210

1. **Na lista de extensões**
2. **Procurar "MaxSeries"**
3. **Verificar versão: deve mostrar v210**
4. **Clicar em "Instalar"**
5. **Aguardar download**

### Passo 5: Reiniciar Cloudstream

1. **Fechar completamente o app**
2. **Abrir novamente**
3. **Verificar versão instalada**

---

## 🔍 Verificação

Após seguir os passos, confirme:

1. **Versão Instalada:**
   - Configurações → Extensões → MaxSeries
   - Deve mostrar: **v210**

2. **Categorias:**
   - Abrir MaxSeries
   - Deve ter **25 categorias**
   - Deve ter "Adicionados Recentemente"

3. **Teste de Reprodução:**
   - Buscar "Breaking Bad"
   - Selecionar episódio
   - Testar reprodução
   - Deve funcionar (~99% sucesso)

---

## 🆘 Se Ainda Não Funcionar

### Opção 1: Download Direto (Mais Confiável)

1. **No navegador do celular, baixar:**
   ```
   https://github.com/franciscoalro/TestPlugins/releases/download/v210/MaxSeries.cs3
   ```

2. **No Cloudstream:**
   - Configurações → Extensões
   - Desinstalar MaxSeries v207
   - Clicar em **+** (adicionar)
   - Selecionar o arquivo **MaxSeries.cs3** baixado
   - Aguardar instalação

3. **Reiniciar Cloudstream**

4. **Verificar versão: deve ser v210**

### Opção 2: Verificar Repositório Usado

1. **Configurações → Extensões**
2. **Ver lista de repositórios**
3. **Verificar URL de cada um**
4. **Se encontrar URL diferente de:**
   ```
   https://raw.githubusercontent.com/franciscoalro/TestPlugins/builds/repo.json
   ```
5. **Remover esse repositório**
6. **Adicionar o correto**

### Opção 3: Reinstalar Cloudstream

Se nada funcionar:

1. **Fazer backup das configurações** (se possível)
2. **Desinstalar Cloudstream completamente**
3. **Reinstalar Cloudstream**
4. **Adicionar repositório correto:**
   ```
   https://raw.githubusercontent.com/franciscoalro/TestPlugins/builds/repo.json
   ```
5. **Instalar MaxSeries v210**

---

## 📊 Comparação de URLs

### ❌ URLs ANTIGAS (NÃO USAR)
```
https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/plugins.json
https://raw.githubusercontent.com/franciscoalro/brcloudstream/builds/repo.json
```

### ✅ URL CORRETA (USAR)
```
https://raw.githubusercontent.com/franciscoalro/TestPlugins/builds/repo.json
```

---

## 🎯 Por Que Isso Acontece?

1. **Cache do Cloudstream:**
   - O app guarda informações antigas
   - Mesmo limpando cache, pode manter repositórios

2. **Múltiplos Repositórios:**
   - Se você adicionou repositórios diferentes
   - O app pode usar o antigo

3. **URL Antiga:**
   - Se usou URL antiga antes
   - O app continua usando ela

---

## ✅ Checklist Final

Antes de testar, confirme:

- [ ] Desinstalou MaxSeries v207
- [ ] Removeu TODOS os repositórios antigos
- [ ] Adicionou repositório correto (builds/repo.json)
- [ ] Instalou MaxSeries v210
- [ ] Reiniciou Cloudstream
- [ ] Verificou versão (deve ser v210)
- [ ] Testou categorias (deve ter 25)
- [ ] Testou reprodução (deve funcionar)

---

## 📞 Informações Úteis

### Versões Disponíveis
- **v207:** Antiga (9 categorias, 3 extractors)
- **v208:** 24 categorias, 3 extractors
- **v209:** 24 categorias, 7 extractors
- **v210:** 25 categorias, 7 extractors ⭐ (ATUAL)

### URLs Corretas
- **Repositório:** https://raw.githubusercontent.com/franciscoalro/TestPlugins/builds/repo.json
- **Download Direto:** https://github.com/franciscoalro/TestPlugins/releases/download/v210/MaxSeries.cs3
- **Release Page:** https://github.com/franciscoalro/TestPlugins/releases/tag/v210

---

## 🎉 Resultado Esperado

Após seguir esta solução, você terá:
- ✅ MaxSeries v210 instalado
- ✅ 25 categorias disponíveis
- ✅ "Adicionados Recentemente" funcionando
- ✅ 7 extractors ativos
- ✅ ~99% taxa de sucesso

---

**Se seguir TODOS os passos corretamente, especialmente removendo TODOS os repositórios antigos, a v210 será instalada! 🎯**

---

**Desenvolvido por:** franciscoalro  
**Data:** 26 Janeiro 2026  
**Versão:** 210
