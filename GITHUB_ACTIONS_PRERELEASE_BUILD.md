# 🚀 Plano: Build MaxSeries via GitHub Actions (Pre-Release)

## 📋 Objetivo
Configurar GitHub Actions para compilar o plugin MaxSeries v80 para Cloudstream Pre-Release de forma rápida e automatizada.

## 🎯 Estratégia

### Opção 1: Fork do Cloudstream Pre-Release (RECOMENDADO)
**Vantagens:**
- ✅ Build completo do projeto
- ✅ Infraestrutura já configurada
- ✅ Todas as dependências disponíveis
- ✅ Workflow existente pode ser adaptado

**Passos:**
1. Fazer fork do repositório cloudstream pre-release
2. Adicionar MaxSeries ao fork
3. Configurar workflow para build do plugin
4. Gerar artifact (.aar ou .jar)

### Opção 2: Repositório Standalone (ALTERNATIVA)
**Vantagens:**
- ✅ Controle total do repositório
- ✅ Menor tamanho do repo

**Desvantagens:**
- ❌ Precisa configurar todas as dependências
- ❌ Mais complexo de manter

## 📝 Implementação - Opção 1 (Escolhida)

### Fase 1: Preparação Local ✅
- [x] Backup do MaxSeries original
- [x] Copiar MaxSeries para cloudstream-pre-release
- [x] Atualizar settings.gradle.kts
- [x] Criar build.gradle.kts moderno
- [x] Verificar AndroidManifest.xml

### Fase 2: Commit e Push
```bash
cd C:\Users\KYTHOURS\Desktop\cloudstream-pre-release

# Inicializar git se necessário
git init
git remote add origin <URL_DO_FORK>

# Adicionar arquivos
git add MaxSeries/
git add settings.gradle.kts

# Commit
git commit -m "feat: Add MaxSeries v80 plugin for pre-release"

# Push
git push origin master
```

### Fase 3: Criar GitHub Actions Workflow

**Arquivo:** `.github/workflows/build-maxseries.yml`

```yaml
name: Build MaxSeries Plugin

on:
  push:
    branches: [ master, main ]
    paths:
      - 'MaxSeries/**'
      - '.github/workflows/build-maxseries.yml'
  pull_request:
    branches: [ master, main ]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Set up JDK 17
      uses: actions/setup-java@v4
      with:
        java-version: '17'
        distribution: 'temurin'
        
    - name: Setup Gradle
      uses: gradle/actions/setup-gradle@v3
      
    - name: Grant execute permission for gradlew
      run: chmod +x gradlew
      
    - name: Build MaxSeries plugin
      run: ./gradlew :MaxSeries:assembleRelease --stacktrace
      
    - name: Upload build artifacts
      uses: actions/upload-artifact@v4
      with:
        name: maxseries-v80
        path: |
          MaxSeries/build/outputs/**/*.aar
          MaxSeries/build/libs/**/*.jar
        retention-days: 30
        
    - name: Create Release (on tag)
      if: startsWith(github.ref, 'refs/tags/')
      uses: softprops/action-gh-release@v1
      with:
        files: |
          MaxSeries/build/outputs/**/*.aar
          MaxSeries/build/libs/**/*.jar
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Fase 4: Alternativa - Build Simplificado

Se o workflow acima não funcionar, criar um workflow mais simples:

**Arquivo:** `.github/workflows/build-maxseries-simple.yml`

```yaml
name: Build MaxSeries (Simple)

on:
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - uses: actions/setup-java@v4
      with:
        java-version: '17'
        distribution: 'temurin'
    
    - name: Build library first
      run: |
        chmod +x gradlew
        ./gradlew :library:build --no-daemon
    
    - name: Build MaxSeries
      run: ./gradlew :MaxSeries:build --no-daemon --stacktrace
    
    - name: List build outputs
      run: |
        echo "=== MaxSeries Build Outputs ==="
        find MaxSeries/build -type f -name "*.aar" -o -name "*.jar"
    
    - uses: actions/upload-artifact@v4
      with:
        name: maxseries-plugin
        path: MaxSeries/build/**/*
```

## 🔄 Fluxo de Trabalho

### 1. Verificar se já existe repositório
```powershell
cd C:\Users\KYTHOURS\Desktop\cloudstream-pre-release
git remote -v
```

### 2. Se não existir, criar fork
- Ir para: https://github.com/recloudstream/cloudstream
- Clicar em "Fork"
- Clonar o fork localmente OU adicionar remote ao diretório existente

### 3. Adicionar remote (se necessário)
```powershell
git remote add origin https://github.com/SEU_USUARIO/cloudstream.git
```

### 4. Criar branch para o plugin
```powershell
git checkout -b feat/maxseries-plugin
```

### 5. Commit e push
```powershell
git add .
git commit -m "feat: Add MaxSeries v80 plugin for pre-release compatibility"
git push origin feat/maxseries-plugin
```

### 6. Criar workflow
- Criar arquivo `.github/workflows/build-maxseries.yml`
- Commit e push
- Ir para GitHub Actions e executar workflow manualmente

## 📊 Verificação de Sucesso

### Build Local (Cancelado - muito lento)
- ❌ `./gradlew :MaxSeries:build` - Demorou 5+ minutos só configurando

### Build GitHub Actions (Esperado)
- ⏱️ Tempo estimado: 3-5 minutos total
- ✅ Artifact gerado: `maxseries-v80.aar` ou `.jar`
- ✅ Logs disponíveis no GitHub

## 🎯 Próximos Passos

1. **Verificar repositório Git**
   - Checar se cloudstream-pre-release já é um repo git
   - Verificar remote configurado

2. **Criar/Atualizar workflow**
   - Adicionar arquivo de workflow
   - Configurar build do MaxSeries

3. **Push e executar**
   - Fazer commit das mudanças
   - Push para GitHub
   - Executar workflow manualmente

4. **Download do artifact**
   - Baixar .aar/.jar do GitHub Actions
   - Testar no Cloudstream pre-release app

## 📌 Notas Importantes

### Diferenças do Build Tradicional
- **Sem .cs3**: Pre-release pode não usar o formato .cs3
- **Output esperado**: `.aar` (Android Archive) ou `.jar`
- **Integração**: Plugin pode precisar ser integrado diretamente no app

### Compatibilidade
- ✅ Código do MaxSeries v79 é compatível
- ✅ APIs usadas estão disponíveis na pre-release
- ⚠️ Formato de distribuição pode ser diferente

### Fallback
Se GitHub Actions não funcionar:
1. Usar GitHub Codespaces (ambiente cloud completo)
2. Usar serviço de CI/CD alternativo (CircleCI, Travis)
3. Configurar VM na nuvem (AWS, GCP, Azure)

---

**Status**: 📋 Plano Criado - Aguardando Execução
**Próximo**: Verificar repositório Git e criar workflow
**Tempo Estimado**: 10-15 minutos
