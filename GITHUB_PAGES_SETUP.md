# Configuração GitHub Pages para CloudStream

## Opção 1: GitHub Pages (Recomendado)

### Vantagens:
- ✅ Não precisa de segundo repositório
- ✅ Não precisa de token de acesso pessoal
- ✅ Deploy automático a cada push
- ✅ URL amigável: `https://franciscoalro.github.io/TestPlugins/repo.json`

### Passos para configurar:

1. **Ativar GitHub Pages**:
   - Vá em Settings → Pages
   - Source: GitHub Actions
   - Salvar

2. **Fazer push deste workflow**:
   ```bash
   git add .github/workflows/deploy-to-pages.yml
   git commit -m "Add GitHub Pages deploy workflow"
   git push
   ```

3. **Aguardar o workflow completar**:
   - Acesse Actions → Deploy to GitHub Pages
   - Aguarde o deploy (≈ 1-2 minutos)

4. **Usar no CloudStream**:
   ```
   https://franciscoalro.github.io/TestPlugins/repo.json
   ```

---

## Opção 2: Dois Repositórios (CloudstreamRepo)

Se preferir manter a estrutura com dois repositórios:

### Criar o Token de Acesso:

1. **Gerar Token**:
   - GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Generate new token (classic)
   - Selecionar scopes: `repo` (Full control of private repositories)
   - Copiar o token gerado

2. **Adicionar ao Repositório**:
   - Vá no repositório TestPlugins → Settings → Secrets and variables → Actions
   - New repository secret
   - Name: `CLOUDSTREAM_REPO_TOKEN`
   - Value: Cole o token copiado
   - Add secret

3. **O workflow atual funcionará automaticamente**

---

## Verificação

Após configurar, verifique se os arquivos estão acessíveis:

```bash
# Teste o repo.json
curl https://franciscoalro.github.io/TestPlugins/repo.json

# Ou se usar CloudstreamRepo:
curl https://raw.githubusercontent.com/franciscoalro/CloudstreamRepo/main/repo.json
```

## Troubleshooting

### Erro "Plugin not found":
- Verifique se o `.jar` existe em `builds/`
- Verifique se o `fileSize` em `plugins.json` corresponde ao tamanho do `.jar`
- Verifique se a URL em `jarUrl` está correta

### Erro 404 no repo.json:
- Verifique se GitHub Pages está ativado
- Aguarde 2-5 minutos após o deploy
- Limpe o cache do CloudStream

### Erro de autenticação no workflow:
- Verifique se o token `CLOUDSTREAM_REPO_TOKEN` está configurado
- Verifique se o token tem permissão para acessar o CloudstreamRepo
