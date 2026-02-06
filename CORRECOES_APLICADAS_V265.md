# ✅ Correções Aplicadas - v265

**Data:** 05/02/2026  
**Repositório:** https://github.com/franciscoalro/TestPlugins

---

## 🎯 Problema Identificado

Os providers não estavam funcionando no CloudStream porque:

1. **Tamanhos dos arquivos .cs3 incorretos** - O CloudStream valida o checksum (tamanho) dos arquivos antes de instalar
2. **URLs apontando para repositório errado** - O `plugins.json` tinha URLs do `saimuelbr/saimuelrepo`
3. **Arquivos desatualizados no GitHub** - Os arquivos no seu repositório remoto estavam diferentes dos locais

### Providers que Funcionavam ✅
- DonghuaNoSekai (tamanho correto: 19,328 bytes)
- Doramas (tamanho correto: 16,792 bytes)
- NovelasFlix (tamanho correto: 18,629 bytes)

### Providers que NÃO Funcionavam ❌
- MaxSeries (tamanho incorreto)
- MegaFlix (tamanho incorreto)
- PobreFlix (tamanho incorreto)
- NetCine (tamanho incorreto)
- Streamberry (tamanho incorreto)
- TopFilmes (tamanho incorreto)
- E outros...

---

## 🔧 Correções Aplicadas

### 1. Arquivos .cs3 Atualizados
Todos os 19 arquivos `.cs3` foram sincronizados com os tamanhos corretos:

| Plugin | Tamanho | Status |
|--------|---------|--------|
| MaxSeries.cs3 | 747,166 bytes | ✅ |
| MegaFlix.cs3 | 15,126 bytes | ✅ |
| PobreFlix.cs3 | 20,855 bytes | ✅ |
| NetCine.cs3 | 17,639 bytes | ✅ |
| DonghuaNoSekai.cs3 | 19,328 bytes | ✅ |
| Doramas.cs3 | 16,792 bytes | ✅ |
| NovelasFlix.cs3 | 18,629 bytes | ✅ |
| Streamberry.cs3 | 20,378 bytes | ✅ |
| TopFilmes.cs3 | 13,586 bytes | ✅ |
| AnimesCloud.cs3 | 22,370 bytes | ✅ |
| AnimesDigital.cs3 | 27,391 bytes | ✅ |
| Anroll.cs3 | 35,987 bytes | ✅ |
| BetterAnime.cs3 | 18,515 bytes | ✅ |
| EmbedCanais.cs3 | 9,758 bytes | ✅ |
| FilmesOn.cs3 | 22,862 bytes | ✅ |
| GoFlix.cs3 | 18,662 bytes | ✅ |
| OverFlix.cs3 | 22,835 bytes | ✅ |
| UltraCine.cs3 | 17,613 bytes | ✅ |
| VisionCine.cs3 | 26,559 bytes | ✅ |

### 2. plugins.json Atualizado
- Todas as URLs agora apontam para `franciscoalro/TestPlugins`
- Todos os `fileSize` atualizados com os valores corretos
- Versão do MaxSeries atualizada para v265

### 3. repo.json Atualizado
- URL correta: `https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/builds/repo.json`

### 4. build.gradle.kts do MaxSeries
- Versão atualizada: 264 → 265
- Autor atualizado: `franciscoalro`

---

## 🚀 Como Fazer Deploy para o GitHub

### Opção 1: Usar o Script PowerShell (Recomendado)

```powershell
# No PowerShell, na pasta do projeto (brcloudstream)
.\deploy-to-github.ps1
```

Este script vai verificar todos os arquivos e mostrar os comandos git necessários.

### Opção 2: Comandos Git Manuais

```bash
# 1. Adicionar arquivos modificados
git add builds/*.cs3
git add builds/plugins.json
git add builds/repo.json
git add plugins.json
git add repo.json
git add MaxSeries/build.gradle.kts
git add CORRECOES_APLICADAS_V265.md
git add deploy-to-github.ps1

# 2. Fazer commit
git commit -m "Atualizar plugins v265 - corrigir tamanhos dos arquivos

- Sincronizar todos os arquivos .cs3 com tamanhos corretos
- Atualizar plugins.json com URLs do repositório correto
- Corrigir fileSize para todos os providers
- MaxSeries v265"

# 3. Enviar para o GitHub
git push origin main
```

### Opção 3: GitHub Desktop

1. Abra o GitHub Desktop
2. Selecione o repositório `TestPlugins`
3. Verifique as mudanças na aba "Changes"
4. Escreva o resumo: "Atualizar plugins v265"
5. Clique em "Commit to main"
6. Clique em "Push origin"

---

## 📱 Como Usar no CloudStream

### URL do Repositório
```
https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/builds/repo.json
```

### Passos para Adicionar

1. Abra o **CloudStream**
2. Vá em **Configurações** → **Extensões** → **Adicionar repositório**
3. Cole a URL acima
4. Toque em **Adicionar**
5. Os plugins aparecerão na lista para download

---

## 📁 Estrutura dos Arquivos

```
brcloudstream/
├── builds/                      # Arquivos compilados (.cs3)
│   ├── MaxSeries.cs3           # ✅ Atualizado (747KB)
│   ├── MegaFlix.cs3            # ✅ Atualizado (15KB)
│   ├── PobreFlix.cs3           # ✅ Atualizado (21KB)
│   ├── NetCine.cs3             # ✅ Atualizado (17KB)
│   ├── DonghuaNoSekai.cs3      # ✅ Atualizado (19KB)
│   ├── Doramas.cs3             # ✅ Atualizado (17KB)
│   ├── NovelasFlix.cs3         # ✅ Atualizado (18KB)
│   ├── Streamberry.cs3         # ✅ Atualizado (20KB)
│   ├── TopFilmes.cs3           # ✅ Atualizado (14KB)
│   ├── AnimesCloud.cs3         # ✅ Atualizado (22KB)
│   ├── AnimesDigital.cs3       # ✅ Atualizado (27KB)
│   ├── Anroll.cs3              # ✅ Atualizado (36KB)
│   ├── BetterAnime.cs3         # ✅ Atualizado (19KB)
│   ├── EmbedCanais.cs3         # ✅ Atualizado (10KB)
│   ├── FilmesOn.cs3            # ✅ Atualizado (23KB)
│   ├── GoFlix.cs3              # ✅ Atualizado (19KB)
│   ├── OverFlix.cs3            # ✅ Atualizado (23KB)
│   ├── UltraCine.cs3           # ✅ Atualizado (17KB)
│   ├── VisionCine.cs3          # ✅ Atualizado (27KB)
│   ├── plugins.json            # ✅ URLs corrigidas
│   └── repo.json               # ✅ URL corrigida
├── plugins.json                # ✅ Cópia na raiz
├── repo.json                   # ✅ Cópia na raiz
├── MaxSeries/
│   └── build.gradle.kts        # ✅ Versão 265
├── deploy-to-github.ps1        # ✅ Script de deploy
└── CORRECOES_APLICADAS_V265.md # ✅ Este arquivo
```

---

## ⚠️ Importante

### Antes de Funcionar no CloudStream

**Você PRECISA fazer o deploy para o GitHub!** Os arquivos locais estão corretos, mas o CloudStream baixa do repositório remoto.

### Verificação no GitHub

Após fazer o push, verifique se os arquivos estão corretos em:
```
https://github.com/franciscoalro/TestPlugins/tree/main/builds
```

### Teste no CloudStream

1. Remova o repositório antigo do CloudStream
2. Adicione novamente: `https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/builds/repo.json`
3. Tente baixar os plugins

---

## 🔄 Atualizações Futuras

Quando precisar atualizar os plugins no futuro:

1. Copie os novos arquivos `.cs3` do `saimuelrepo` (se for usar como base)
2. Atualize o `fileSize` no `plugins.json`
3. Incremente a versão no `build.gradle.kts`
4. Faça commit e push para o GitHub

---

## 🆘 Suporte

Se ainda tiver problemas após o deploy:

1. Verifique se o push foi feito corretamente: `git log`
2. Confira os tamanhos dos arquivos no GitHub (devem bater com a tabela acima)
3. Limpe o cache do CloudStream e tente novamente

**Repositório:** https://github.com/franciscoalro/TestPlugins  
**Versão Atual:** v265
