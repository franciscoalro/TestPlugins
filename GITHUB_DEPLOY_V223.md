# 🚀 Deploy MaxSeries v223 - GitHub Actions

## 📋 Resumo das Configurações

### ✅ Arquivos Atualizados

1. **`repo.json`** - Descrição do repositório atualizada
2. **`plugins.json`** - Versão 223 com link correto da release
3. **`.github/workflows/release-v223.yml`** - Workflow completo de deploy
4. **`deploy-v223-github.ps1`** - Script PowerShell para deploy manual

---

## 🔄 Fluxo de Deploy Automático

```
1. Push para main com alterações no PlayerEmbedAPI
         ↓
2. GitHub Actions executa: release-v223.yml
         ↓
3. Build do MaxSeries v223
         ↓
4. Cria tag v223
         ↓
5. Cria release v223 com o arquivo .cs3
         ↓
6. Atualiza branch builds (repo.json, plugins.json, .cs3)
         ↓
7. Deploy para CloudstreamRepo
```

---

## 🚀 Como Executar o Deploy

### Opção 1: GitHub Actions (Automático)

O deploy automático acontece quando você faz push para a branch `main` com alterações em:
- `PlayerEmbedAPIWebViewExtractor.kt`
- `MaxSeriesProvider.kt`

Ou execute manualmente:
1. Acesse: https://github.com/franciscoalro/TestPlugins/actions
2. Selecione o workflow "Release v223 - PlayerEmbedAPI Redirect Fix"
3. Clique em "Run workflow"

### Opção 2: PowerShell Script (Manual)

```powershell
# Na pasta brcloudstream
.\deploy-v223-github.ps1
```

Isso irá:
- ✅ Fazer commit das alterações (se houver)
- ✅ Criar a tag v223
- ✅ Atualizar a branch builds
- ⏳ **Criar a release manualmente** (ver instruções abaixo)

### Opção 3: Comandos Git (Manual)

```bash
# 1. Commit das alterações
git add -A
git commit -m "MaxSeries v223 - PlayerEmbedAPI Redirect Fix"
git push origin main

# 2. Criar tag
git tag -a v223 -m "MaxSeries v223 - PlayerEmbedAPI Redirect Fix"
git push origin v223

# 3. Atualizar branch builds
git checkout builds
cp MaxSeries/build/MaxSeries.cs3 .
cp plugins.json .
cp repo.json .
git add -A
git commit -m "MaxSeries v223"
git push origin builds
git checkout main

# 4. Criar release manualmente no GitHub
```

---

## 📦 Criar Release Manualmente (GitHub)

Após executar o deploy:

1. Acesse: https://github.com/franciscoalro/TestPlugins/releases/new
2. **Choose a tag**: Selecione `v223`
3. **Release title**: `MaxSeries v223 - PlayerEmbedAPI Redirect Fix`
4. **Description**:
```markdown
## 🚀 MaxSeries v223 - PlayerEmbedAPI Redirect Fix

### ✨ Novidades
- 🔄 **FIX FINAL**: Segue redirect `sssrr.org` → `googleapis.com` automaticamente
- 🎯 Headers completos para Google Storage
- ✅ Verificação se redirect foi bem-sucedido
- 🐛 Corrige `ERROR_CODE_IO_BAD_HTTP_STATUS (2004)`

### 📦 Arquivo
- **MaxSeries.cs3** - Build v223

### 📱 Como Usar
1. Instale o arquivo `.cs3` no CloudStream
2. Selecione **PlayerEmbedAPI**
3. Clique 3 vezes no WebView
4. O vídeo reproduzirá automaticamente!
```
5. **Attach binaries**: Faça upload do arquivo `MaxSeries/build/MaxSeries.cs3`
6. Clique em **Publish release**

---

## 🔗 URLs Importantes

| Recurso | URL |
|---------|-----|
| **Repo** | `https://raw.githubusercontent.com/franciscoalro/TestPlugins/builds/repo.json` |
| **Plugins** | `https://raw.githubusercontent.com/franciscoalro/TestPlugins/builds/plugins.json` |
| **Download** | `https://github.com/franciscoalro/TestPlugins/releases/download/v223/MaxSeries.cs3` |
| **Releases** | https://github.com/franciscoalro/TestPlugins/releases |

---

## 📊 Verificar Deploy

### Verificar branch builds:
```bash
git checkout builds
git log --oneline -5
ls -la *.cs3 *.json
```

### Verificar release:
```bash
# Abra no navegador
https://github.com/franciscoalro/TestPlugins/releases/tag/v223
```

### Testar no CloudStream:
1. Adicione o repositório:
   ```
   https://raw.githubusercontent.com/franciscoalro/TestPlugins/builds/repo.json
   ```
2. Instale o MaxSeries
3. Verifique se mostra "v223" nas informações do provider

---

## 🐛 Troubleshooting

### Tag já existe
```bash
# Deletar tag local e remota
git tag -d v223
git push origin :refs/tags/v223
```

### Branch builds não existe
```bash
# Criar branch builds
git checkout --orphan builds
git rm -rf .
git commit --allow-empty -m "Initial builds branch"
git push origin builds
```

### Workflow falhou
1. Acesse: https://github.com/franciscoalro/TestPlugins/actions
2. Clique no workflow que falhou
3. Verifique os logs de erro

---

## ✅ Checklist Pré-Deploy

- [ ] Build local funcionou (`./gradlew MaxSeries:make`)
- [ ] Arquivo `MaxSeries.cs3` foi gerado
- [ ] `plugins.json` atualizado com versão 223
- [ ] `repo.json` atualizado com descrição
- [ ] Código commitado na branch main
- [ ] Testado no CloudStream (opcional mas recomendado)

---

## 📞 Suporte

Se encontrar problemas:
1. Verifique os logs do GitHub Actions
2. Verifique se o token `CLOUDSTREAM_REPO_TOKEN` está configurado (Settings > Secrets)
3. Teste o build localmente primeiro
