# Deploy do BRCloudStream Repository

## OpÃ§Ãµes de Hospedagem Gratuita

### 1. Netlify (Recomendado)
1. Acesse https://netlify.com
2. FaÃ§a login com GitHub
3. Arraste a pasta cloud-deploy para o site
4. Sua URL serÃ¡: https://SEU-SITE.netlify.app/repo.json

### 2. Vercel
1. Acesse https://vercel.com
2. FaÃ§a login com GitHub
3. Importe este projeto
4. Sua URL serÃ¡: https://SEU-SITE.vercel.app/repo.json

### 3. GitHub Pages
1. Crie um novo repositÃ³rio no GitHub
2. FaÃ§a upload dos arquivos desta pasta
3. Ative GitHub Pages nas configuraÃ§Ãµes
4. Sua URL serÃ¡: https://SEU-USUARIO.github.io/SEU-REPO/repo.json

### 4. Firebase Hosting
1. Instale Firebase CLI: 
pm install -g firebase-tools
2. Execute: irebase login
3. Execute: irebase init hosting
4. Execute: irebase deploy

### 5. Surge.sh
1. Instale Surge: 
pm install -g surge
2. Na pasta cloud-deploy, execute: surge
3. Sua URL serÃ¡: https://SEU-DOMINIO.surge.sh/repo.json

## Arquivos IncluÃ­dos
- epo.json - ConfiguraÃ§Ã£o principal do repositÃ³rio
- epo-alternative.json - VersÃ£o alternativa
- plugins.json - Lista de plugins
- plugins-minimal.json - VersÃ£o minimalista
- *.cs3 - Arquivos dos plugins (11 plugins)
- *.jar - Arquivos JAR dos plugins
- index.html - PÃ¡gina web para visualizaÃ§Ã£o

## Teste
ApÃ³s o deploy, teste a URL no Cloudstream:
https://SEU-DOMINIO/repo.json
