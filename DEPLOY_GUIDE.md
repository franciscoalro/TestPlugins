# Guia de Deploy - BRCloudStream Repository

Este guia explica como publicar seu repositorio de plugins do CloudStream online para que outros usuarios possam instalar.

## Metodo 1: GitHub Pages (Recomendado)

### Passo 1: Preparar os Arquivos

Os arquivos ja foram gerados na pasta `builds/`:

```
builds/
├── plugins.json          # Metadados dos plugins
├── repo.json             # Configuracao do repositorio
├── index.html            # Pagina web do repositorio
├── AnimesOnlineCC.cs3    # Plugins compilados
├── DonghuaNoSekai.cs3
├── Doramas.cs3
├── EmbedCanais.cs3
├── MaxSeries.cs3
├── MegaFlix.cs3
├── NetCine.cs3
├── NovelasFlix.cs3
├── OverFlix.cs3
├── PobreFlix.cs3
└── Vizer.cs3
```

### Passo 2: Criar Repositorio no GitHub

1. Acesse https://github.com/new
2. Nome do repositorio: `brcloudstream` (ou outro nome)
3. Deixe como Publico
4. Nao inicialize com README (ja temos)
5. Clique em "Create repository"

### Passo 3: Enviar Codigo para GitHub

Execute no terminal (dentro da pasta do projeto):

```bash
# Inicializar git (se ainda nao fez)
git init

# Adicionar remote
git remote add origin https://github.com/SEU_USUARIO/brcloudstream.git

# Commit na branch main
git add .
git commit -m "Initial commit"
git push -u origin main

# Criar e enviar branch gh-pages
git checkout --orphan gh-pages
git rm -rf .
git add builds/
git mv builds/* .
git commit -m "GitHub Pages deploy"
git push origin gh-pages

# Voltar para main
git checkout main
```

> **Nota:** Substitua `SEU_USUARIO` pelo seu nome de usuario do GitHub.

### Passo 4: Configurar GitHub Pages

1. No GitHub, va para **Settings** > **Pages**
2. Em "Source", selecione: **Deploy from a branch**
3. Em "Branch", selecione: **gh-pages** / **/(root)**
4. Clique em **Save**
5. Aguarde 2-5 minutos

### Passo 5: Testar

Acesse:
- Pagina: `https://SEU_USUARIO.github.io/brcloudstream/`
- Plugins JSON: `https://SEU_USUARIO.github.io/brcloudstream/plugins.json`

---

## Metodo 2: Script Automatico

Execute o script PowerShell fornecido:

```powershell
.\deploy-to-github-pages.ps1
```

Siga as instrucoes exibidas no terminal.

---

## Como os Usuarios Instalam

### Opcao 1: Link Curto (Shortcode)

1. Abra o CloudStream
2. Va em Configuracoes > Extensoes
3. Toque em "Adicionar Repositorio"
4. Digite: `brcs` (ou o shortcode que voce definir)
5. Toque em OK
6. Instale os providers desejados

### Opcao 2: URL Completa

1. Abra o CloudStream
2. Va em Configuracoes > Extensoes
3. Toque em "Adicionar Repositorio"
4. Digite: `https://SEU_USUARIO.github.io/brcloudstream/plugins.json`
5. Toque em OK

---

## Configurar Shortcode Personalizado

Para registrar um shortcode curto (ex: `brcs`):

1. Acesse: https://github.com/recloudstream/shortcode-api
2. Leia a documentacao
3. Faca um PR adicionando seu shortcode no arquivo `shortcodes.json`

Exemplo de entrada:
```json
{
  "brcs": "https://franciscoalro.github.io/brcloudstream/plugins.json"
}
```

---

## Estrutura do Repositório

### plugins.json

Contem metadados de todos os plugins:

```json
{
  "name": "BRCloudStream Repository",
  "description": "Repositorio brasileiro...",
  "author": "franciscoalro",
  "version": 3,
  "repositoryUrl": "https://github.com/franciscoalro/brcloudstream",
  "plugins": [
    {
      "name": "MaxSeries",
      "description": "Filmes e series...",
      "version": 256,
      "url": "https://franciscoalro.github.io/brcloudstream/MaxSeries.cs3",
      "status": 1,
      "lang": ["pt"],
      "tvTypes": ["Movie", "TvSeries"]
    }
  ]
}
```

### repo.json

Usado pelo CloudStream para identificar o repositorio:

```json
{
  "name": "BRCloudStream",
  "url": "https://franciscoalro.github.io/brcloudstream/plugins.json",
  "description": "Repositorio brasileiro...",
  "author": "franciscoalro"
}
```

---

## Atualizando o Repositório

Quando fizer alteracoes nos plugins:

```bash
# Build do projeto
.\gradlew.bat build

# Copiar novos arquivos
# (o script faz isso automaticamente)

# Commit e push
git add .
git commit -m "Update providers"
git push origin main

# Atualizar gh-pages
git checkout gh-pages
git checkout main -- builds/
git mv -f builds/* .
git add .
git commit -m "Update GitHub Pages"
git push origin gh-pages
git checkout main
```

---

## Solucao de Problemas

### Erro 404 no GitHub Pages

- Verifique se o branch `gh-pages` existe
- Confirme que os arquivos estao na raiz do branch
- Aguarde 5 minutos apos o push

### Plugins nao aparecem no CloudStream

- Verifique se a URL esta correta
- Teste a URL no navegador
- Verifique se o JSON e valido em https://jsonlint.com/

### Arquivos .cs3 nao baixam

- Verifique se os arquivos estao no branch gh-pages
- Confirme que os links no plugins.json estao corretos

---

## Links Uteis

- GitHub Pages: https://pages.github.com/
- Documentacao CloudStream: https://github.com/recloudstream/cloudstream
- Repositório de exemplo: https://github.com/saimuelbr/saimuelrepo

---

## Resumo

| Etapa | Comando/Acao |
|-------|--------------|
| Build | `.\gradlew.bat build` |
| Copiar arquivos | Automatico no script |
| Commit main | `git add . && git commit -m "msg" && git push origin main` |
| Deploy gh-pages | Script automatico ou manual |
| URL final | `https://USER.github.io/brcloudstream/plugins.json` |
| Shortcode | `brcs` (apos registro) |

---

**Pronto! Seu repositorio estara online e disponivel para todos os usuarios do CloudStream!**
