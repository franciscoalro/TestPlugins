# Upload MaxSeries v256 para GitHub Releases

## 📦 Arquivos Gerados

- `releases/MaxSeries.cs3` (638 KB) - Versão atual
- `releases/MaxSeries-v256.cs3` - Versão v256 identificada

## 🚀 Método 1: Upload Automático (Recomendado)

### Pré-requisitos
1. Ter um token de acesso pessoal do GitHub
2. PowerShell 5.1 ou superior

### Passos

1. **Gerar token do GitHub:**
   - Acesse: https://github.com/settings/tokens
   - Clique em "Generate new token (classic)"
   - Selecione o scope `repo` (acesso completo ao repositório)
   - Copie o token gerado

2. **Configurar token:**
   ```powershell
   $env:GITHUB_TOKEN = "ghp_seu_token_aqui"
   ```

3. **Executar upload:**
   ```powershell
   .\upload-to-github-release.ps1
   ```

4. **Verificar:**
   - Acesse: https://github.com/franciscoalro/TestPlugins/releases
   - Confirme que a release v256 foi criada

## 🚀 Método 2: Upload Manual

1. **Acesse o GitHub:**
   - URL: https://github.com/franciscoalro/TestPlugins/releases/new

2. **Preencha os dados:**
   - **Choose a tag:** `v256` (crie nova)
   - **Release title:** `MaxSeries v256`
   - **Description:**
     ```
     ## MaxSeries v256 - PlayerEmbedAPI V8+V7 Fixes

     ### 🚀 Novidades
     - PlayerEmbedAPI V8 (Pure HTTP): 12 padrões de URL
     - PlayerEmbedAPI V7 (WebView): Memory leak corrigido
     - Timeout global: 15s → 25s
     - Max attempts: 3 → 5

     ### 🔧 Correções
     - Regex JWPlayer mais robusto
     - Novos CDNs: Akamai, CloudFront, Fastly, BunnyCDN, CDN77
     - Validação de URL aprimorada
     - Flag atômica no WebView cleanup
     ```

3. **Anexe o arquivo:**
   - Arraste ou selecione: `releases/MaxSeries.cs3`

4. **Publique:**
   - Clique em "Publish release"

## 📋 JSONs Atualizados

Os seguintes arquivos JSON foram atualizados para v256:

- ✅ `repo.json`
- ✅ `plugins.json`
- ✅ `plugins-complete.json`
- ✅ `repo-complete.json`
- ✅ `plugins-simple.json`

## 🔗 URLs Importantes

- **Repositório:** https://github.com/franciscoalro/TestPlugins
- **Releases:** https://github.com/franciscoalro/TestPlugins/releases
- **Repo JSON:** https://raw.githubusercontent.com/franciscoalro/TestPlugins/builds/repo.json
- **Plugins JSON:** https://raw.githubusercontent.com/franciscoalro/TestPlugins/builds/plugins.json

## ⚠️ Aviso

Sem o upload do arquivo `.cs3` para o GitHub Releases, o CloudStream não conseguirá baixar a versão v256!

Os usuários verão a atualização disponível mas não conseguirão instalá-la.

## 📊 Checklist Final

- [ ] Arquivo `releases/MaxSeries.cs3` gerado (638 KB)
- [ ] Todos JSONs atualizados para v256
- [ ] Upload para GitHub Releases realizado
- [ ] URL da release testada (deve retornar 200)
- [ ] Teste no CloudStream realizado
