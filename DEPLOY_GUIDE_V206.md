# Deploy Guide - Release v206

## Pre-requisitos

- Git instalado e configurado
- GitHub CLI (gh) instalado
- Autenticado no GitHub

## Passo a Passo

### 1. Verificar Build
```powershell
Get-ChildItem -Filter "*.cs3"
```

### 2. Commit e Push
```powershell
.\commit-and-push-v206.ps1
```

### 3. Criar Release
```powershell
.\create-release-v206.ps1
```

### 4. Verificar
- Acesse: https://github.com/franciscoalro/TestPlugins/releases/tag/v206
- Verifique os 7 arquivos .cs3

## Comandos Rapidos

### Build
```powershell
./gradlew make -x lint -x lintDebug -x lintRelease
```

### Deploy Completo
```powershell
./gradlew make -x lint -x lintDebug -x lintRelease
.\commit-and-push-v206.ps1
.\create-release-v206.ps1
```
