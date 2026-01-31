# GitHub Actions - Status da Configuração

## ✅ Workflows Criados

### 1. update-jsons.yml
**Local:** `.github/workflows/update-jsons.yml`

**Função:**
- Atualiza os arquivos `plugins.json` e `repo.json` automaticamente
- Roda no ambiente Ubuntu (Linux)
- Cria JSONs com encoding UTF-8 correto
- Faz commit e push automaticamente

**Triggers:**
- Push para branch `main`
- Manual (workflow_dispatch)

**Status:** ⚠️ Configurado mas pode estar falhando

### 2. upload-release.yml
**Local:** `.github/workflows/upload-release.yml`

**Função:**
- Faz upload do arquivo CS3 para GitHub Releases
- Cria/atualiza release com notas

**Triggers:**
- Manual apenas (workflow_dispatch)

**Status:** ⚠️ Configurado

---

## 🔧 Como usar os Workflows

### Atualizar JSONs automaticamente
1. Acesse: https://github.com/franciscoalro/CloudstreamRepo/actions
2. Clique em "Update JSONs for v256"
3. Clique em "Run workflow"
4. Aguarde a conclusão

### Fazer upload do CS3
1. Acesse: https://github.com/franciscoalro/CloudstreamRepo/actions
2. Clique em "Upload CS3 to GitHub Releases"
3. Clique em "Run workflow"
4. Preencha:
   - version: `256`
   - tag: `v256`
5. Clique em "Run workflow"

---

## ⚠️ Possíveis Problemas

Se os workflows estiverem falhando, pode ser devido a:

1. **Permissões do repositório**
   - Acesse: Settings → Actions → General
   - Em "Workflow permissions", selecione "Read and write permissions"
   - Salve as alterações

2. **GitHub Actions desabilitado**
   - Acesse: Settings → Actions → General
   - Em "Actions permissions", selecione "Allow all actions and reusable workflows"
   - Salve as alterações

3. **Branch protection**
   - Verifique se a branch main não tem proteções que impeçam push

---

## ✅ Status Atual (Manual)

Os JSONs foram atualizados manualmente com sucesso:

- ✅ `plugins.json` - Formato idêntico à v253
- ✅ `repo.json` - Formato limpo
- ✅ Sem BOM UTF-8
- ✅ Estrutura JSON válida

**URLs para testar:**
- Repo: https://franciscoalro.github.io/CloudstreamRepo/repo.json
- Plugins: https://franciscoalro.github.io/CloudstreamRepo/plugins.json

---

## 🚀 Próximos Passos

1. **Habilitar permissões do Actions** (se necessário)
2. **Testar workflow manualmente** na interface do GitHub
3. **Verificar se os JSONs estão corretos** no CloudStream

---

## 📞 Suporte

Se os workflows não funcionarem, os JSONs podem ser atualizados manualmente:
1. Editar diretamente no GitHub
2. Ou clonar, editar e fazer push
