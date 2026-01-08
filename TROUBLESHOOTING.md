# 🔧 Guia de Troubleshooting - CloudStream Repository

## ❌ Problema: "Erro ao baixar" no CloudStream

### ✅ Soluções Testadas (em ordem de prioridade)

#### 1. **Use a URL Correta**
```
https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/repo.json
```

#### 2. **Limpe o Cache do CloudStream**
- Vá em **Configurações** → **Geral** → **Limpar Cache**
- Reinicie o app
- Tente adicionar o repositório novamente

#### 3. **Remova e Adicione o Repositório**
- **Configurações** → **Extensões** → **Repositórios**
- Remova o repositório existente
- Adicione novamente com a URL correta

#### 4. **Verifique a Conexão**
- Teste se consegue acessar: https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/plugins.json
- Deve mostrar o JSON dos plugins

#### 5. **URLs Alternativas para Testar**

**Repositório Principal:**
```
https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/repo.json
```

**Repositório Simplificado (para teste):**
```
https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/repo-simple.json
```

**Plugins Direto (para teste):**
```
https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/plugins.json
```

### 🔍 Diagnóstico Avançado

#### Teste 1: Verificar se o JSON é válido
```bash
curl -s "https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/plugins.json" | jq .
```

#### Teste 2: Verificar se os arquivos .cs3 existem
```bash
curl -I "https://github.com/franciscoalro/TestPlugins/releases/download/v8.0/MaxSeries.cs3"
curl -I "https://github.com/franciscoalro/TestPlugins/releases/download/v8.0/AnimesOnlineCC.cs3"
```

#### Teste 3: Verificar estrutura do repositório
```bash
curl -s "https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/repo.json" | jq .
```

### 📱 Passos Detalhados no CloudStream

1. **Abrir CloudStream**
2. **Ir para Configurações** (ícone de engrenagem)
3. **Selecionar "Extensões"**
4. **Clicar em "Adicionar Repositório"**
5. **Colar a URL:**
   ```
   https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/repo.json
   ```
6. **Dar um nome:** "TestPlugins"
7. **Clicar em "Adicionar"**
8. **Aguardar carregar**
9. **Instalar os plugins desejados**

### 🐛 Problemas Conhecidos e Soluções

#### Problema: "Repository not found"
**Solução:** Verifique se a URL está correta e sem espaços extras

#### Problema: "Invalid JSON format"
**Solução:** O JSON foi corrigido, use a versão mais recente

#### Problema: "Plugin download failed"
**Solução:** Os arquivos .cs3 existem na release v8.0, verifique conexão

#### Problema: "Encoding issues"
**Solução:** Removidos caracteres especiais que causavam problemas

### 📊 Status dos Componentes

| Componente | Status | URL |
|------------|--------|-----|
| repo.json | ✅ OK | https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/repo.json |
| plugins.json | ✅ OK | https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/plugins.json |
| MaxSeries.cs3 | ✅ OK | https://github.com/franciscoalro/TestPlugins/releases/download/v8.0/MaxSeries.cs3 |
| AnimesOnlineCC.cs3 | ✅ OK | https://github.com/franciscoalro/TestPlugins/releases/download/v8.0/AnimesOnlineCC.cs3 |

### 🔄 Se Ainda Não Funcionar

#### Opção 1: Download Manual
1. Baixe os arquivos .cs3 diretamente:
   - [MaxSeries.cs3](https://github.com/franciscoalro/TestPlugins/releases/download/v8.0/MaxSeries.cs3)
   - [AnimesOnlineCC.cs3](https://github.com/franciscoalro/TestPlugins/releases/download/v8.0/AnimesOnlineCC.cs3)
2. Instale manualmente no CloudStream

#### Opção 2: Repositório Alternativo
Use repositórios oficiais do CloudStream enquanto investigamos:
- https://raw.githubusercontent.com/recloudstream/cloudstream-extensions/builds/repo.json

### 📞 Reportar Problemas

Se nenhuma solução funcionar, reporte com:

1. **Versão do CloudStream**
2. **Sistema operacional**
3. **Mensagem de erro exata**
4. **Screenshots do erro**
5. **Resultado dos testes de diagnóstico**

### 🔧 Ferramentas de Teste

Execute este comando para testar tudo:
```powershell
# Windows PowerShell
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/repo.json" | Select-Object StatusCode, Content
```

```bash
# Linux/Mac
curl -s "https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/repo.json" && echo "✅ Repository JSON OK"
```

---

**Última atualização:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")  
**Status:** Todos os componentes funcionando ✅