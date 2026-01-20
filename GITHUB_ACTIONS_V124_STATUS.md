# GitHub Actions - v124 Status

## Data
18 de Janeiro de 2026

## Status Atual
✅ **TUDO PRONTO PARA GITHUB ACTIONS**

## Arquivos Atualizados

### 1. Build Configuration
- ✅ `MaxSeries/build.gradle.kts` - version = 124
- ✅ `MaxSeries/src/main/kotlin/.../PlayerEmbedAPIExtractor.kt` - v3.3

### 2. Repository JSONs
- ✅ `plugins.json` - Atualizado para v124
  - URL: `https://github.com/franciscoalro/TestPlugins/releases/download/v124.0/MaxSeries.cs3`
  - Version: 124
  - Description: "MaxSeries v124 - PlayerEmbedAPI v3.3 (SSSRR.ORG CDN Fix) - Regex corrigido"
- ✅ `repo.json` - Mantido (não precisa alteração)

### 3. Git Status
- ✅ Commit: "Update plugins.json to v124 - SSSRR.ORG CDN Fix"
- ✅ Tag: v124.0
- ✅ Push: Realizado com sucesso
- ✅ GitHub Release: Criado em https://github.com/franciscoalro/TestPlugins/releases/tag/v124.0

## GitHub Actions Workflow

### Arquivo: `.github/workflows/build.yml`
```yaml
name: Build and Release

on:
  push:
    branches: [ master, main ]
    tags:
      - 'v*'
  workflow_dispatch:
```

### Triggers
1. ✅ **Push to main** - Já ativado (commit feito)
2. ✅ **Tag v124.0** - Já criado e pushed
3. ⏳ **Workflow Dispatch** - Pode ser acionado manualmente

### Build Steps
1. Checkout código
2. Setup JDK 17
3. Setup Gradle
4. Build com retry (5 tentativas, 15min timeout)
5. Upload artifacts
6. Create GitHub Release (se tag)

## Como Verificar o Build

### 1. Via GitHub Web
```
https://github.com/franciscoalro/TestPlugins/actions
```

### 2. Via GitHub CLI
```powershell
gh run list --limit 5
gh run watch
```

### 3. Verificar Release
```
https://github.com/franciscoalro/TestPlugins/releases/tag/v124.0
```

## O Que o GitHub Actions Vai Fazer

### Quando o workflow rodar:
1. ✅ Fazer checkout do código (commit 9420f86)
2. ✅ Configurar JDK 17
3. ✅ Executar `./gradlew MaxSeries:make AnimesOnlineCC:make`
4. ✅ Gerar `MaxSeries.cs3` (v124) e `AnimesOnlineCC.cs3`
5. ✅ Upload dos artifacts
6. ✅ Atualizar release v124.0 com os arquivos .cs3

## Arquivos que Serão Gerados

### MaxSeries.cs3
- **Versão**: 124
- **Tamanho esperado**: ~143 KB
- **Extractor**: PlayerEmbedAPIExtractor v3.3
- **Mudança principal**: Regex corrigido para sssrr.org

### AnimesOnlineCC.cs3
- **Versão**: 10 (mantida)
- **Sem alterações**

## URLs Importantes

### 1. GitHub Release
```
https://github.com/franciscoalro/TestPlugins/releases/tag/v124.0
```

### 2. Raw plugins.json
```
https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/plugins.json
```

### 3. GitHub Actions
```
https://github.com/franciscoalro/TestPlugins/actions
```

### 4. Download Direto (após build)
```
https://github.com/franciscoalro/TestPlugins/releases/download/v124.0/MaxSeries.cs3
```

## Como Usuários Vão Atualizar

### No CloudStream App:
1. Abrir CloudStream
2. Ir em **Extensions** / **Extensões**
3. Clicar em **Update** / **Atualizar** no MaxSeries
4. App vai baixar de: `https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/plugins.json`
5. Ver versão 124 disponível
6. Baixar de: `https://github.com/franciscoalro/TestPlugins/releases/download/v124.0/MaxSeries.cs3`
7. Instalar automaticamente

## Verificação Pós-Build

### Checklist:
- [ ] GitHub Actions completou com sucesso
- [ ] MaxSeries.cs3 está no release v124.0
- [ ] Tamanho do arquivo ~143 KB
- [ ] plugins.json aponta para v124.0
- [ ] Usuários conseguem atualizar no app

## Comandos Úteis

### Acionar build manualmente:
```powershell
gh workflow run build.yml
```

### Ver logs do último build:
```powershell
gh run view --log
```

### Baixar artifacts:
```powershell
gh run download
```

## Próximos Passos

1. ⏳ Aguardar GitHub Actions completar o build
2. ⏳ Verificar se MaxSeries.cs3 foi adicionado ao release
3. ⏳ Testar download do plugins.json
4. ⏳ Testar atualização no app CloudStream
5. ⏳ Monitorar com ADB se PlayerEmbedAPI funciona

## Notas

- O build local já foi feito e testado com sucesso
- O GitHub Actions vai recriar o mesmo build em ambiente limpo
- Se o build falhar, o workflow tem 5 tentativas com retry
- O arquivo já está no release (upload manual), GitHub Actions vai sobrescrever

---

**Status**: ✅ PRONTO PARA GITHUB ACTIONS  
**Versão**: 124  
**Data**: 18/01/2026  
**Commit**: 9420f86
