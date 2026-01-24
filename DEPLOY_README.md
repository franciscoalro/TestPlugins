# 🚀 MaxSeries Auto-Deploy

Script de automação completa para deploy de novas versões do plugin MaxSeries.

## ✨ O Que Ele Faz

Quando você alterar a versão no `build.gradle.kts`, este script automatiza **TODO** o processo:

1. ✅ **Build** do plugin (Gradle)
2. ✅ **Calcula SHA256** do arquivo `.cs3`
3. ✅ **Atualiza JSONs** (plugins.json, plugins-simple.json, providers.json)
4. ✅ **Commit e Push** para GitHub
5. ✅ **Cria Release** no GitHub automaticamente com o arquivo `.cs3`

## 📋 Pré-requisitos

### 1. GitHub CLI (Obrigatório para criar releases automaticamente)

**Instalar via winget:**
```powershell
winget install GitHub.cli
```

**Ou baixar manualmente:**
https://cli.github.com/

**Autenticar após instalação:**
```powershell
gh auth login
```

Escolha:
- GitHub.com
- HTTPS
- Login via browser

## 🎯 Como Usar

### Método 1: Deploy Completo (Recomendado)

```powershell
# Simplesmente execute o script
.\deploy.ps1
```

Isso vai:
1. Detectar a versão do `build.gradle.kts`
2. Compilar o plugin
3. Atualizar todos os JSONs
4. Fazer commit e push
5. Criar release no GitHub

### Método 2: Pular Build (se já compilou)

```powershell
.\deploy.ps1 -SkipBuild
```

### Método 3: Sem Release Automática

```powershell
.\deploy.ps1 -SkipRelease
```

## 📝 Workflow Completo

### 1. Fazer Alterações no Código

```kotlin
// Exemplo: MaxSeries/src/main/kotlin/.../MegaEmbedExtractorV8.kt
// Faça suas alterações...
```

### 2. Atualizar Versão e Descrição

```kotlin
// MaxSeries/build.gradle.kts
version = 164  // ← Incrementar versão

cloudstream {
    description = "MaxSeries v164 - Nova funcionalidade XYZ"  // ← Atualizar descrição
    // ...
}
```

### 3. Executar Script de Deploy

```powershell
.\deploy.ps1
```

### 4. Aguardar Conclusão

O script vai mostrar o progresso:

```
============================================================
  MaxSeries Auto-Deploy Script v1.0
============================================================

ℹ️  STEP 1: Detectando versão atual...
✅ Versão detectada: v164
ℹ️  Descrição: MaxSeries v164 - Nova funcionalidade XYZ

ℹ️  STEP 2: Compilando plugin...
✅ Build concluído com sucesso!

ℹ️  STEP 3: Calculando SHA256...
✅ Arquivo: .\MaxSeries\build\MaxSeries.cs3
ℹ️  SHA256: ABC123...

ℹ️  STEP 4: Atualizando arquivos JSON...
✅ Atualizado: .\plugins.json
✅ Atualizado: .\plugins-simple.json
✅ Atualizado: .\providers.json

ℹ️  STEP 5: Fazendo commit e push...
✅ Commit criado: MaxSeries v164: Nova funcionalidade XYZ
✅ Push concluído!

ℹ️  STEP 6: Criando release no GitHub...
✅ Release v164 criada com sucesso!

============================================================
  ✅ DEPLOY CONCLUÍDO COM SUCESSO!
============================================================
```

### 5. Testar no CloudStream

1. Abra CloudStream no dispositivo
2. Configurações → Extensões → Atualizar
3. Atualize o plugin MaxSeries para v164
4. Teste a funcionalidade

## 🔧 Troubleshooting

### Erro: "gh: command not found"

**Solução**: Instale o GitHub CLI:
```powershell
winget install GitHub.cli
```

Depois autentique:
```powershell
gh auth login
```

### Erro: "Build failed"

**Solução**: Verifique se há erros de compilação:
```powershell
.\gradlew.bat MaxSeries:make --no-daemon
```

### Erro: "Push failed"

**Solução**: Verifique se você tem permissão de escrita no repositório:
```powershell
git remote -v
```

### Release não foi criada

**Opção 1**: Execute novamente só a parte de release:
```powershell
# Primeiro, crie a tag manualmente
git tag v164
git push origin v164

# Depois crie a release
gh release create v164 MaxSeries\build\MaxSeries.cs3 --title "MaxSeries v164" --notes "Nova funcionalidade XYZ"
```

**Opção 2**: Crie manualmente no GitHub:
1. Vá em: https://github.com/franciscoalro/TestPlugins/releases/new
2. Tag: `v164`
3. Anexe: `MaxSeries\build\MaxSeries.cs3`
4. Publique

## 📊 Estrutura de Arquivos Atualizados

```
brcloudstream/
├── deploy.ps1                    ← Script de automação
├── plugins.json                  ← Atualizado automaticamente
├── plugins-simple.json           ← Atualizado automaticamente
├── providers.json                ← Atualizado automaticamente
└── MaxSeries/
    ├── build.gradle.kts          ← Você atualiza manualmente
    ├── src/                      ← Você edita o código
    └── build/
        └── MaxSeries.cs3         ← Gerado pelo build
```

## 🎓 Dicas

### Sempre Incremente a Versão

```kotlin
// ❌ ERRADO - Não reutilizar versões
version = 163  // Já existe

// ✅ CORRETO - Sempre incrementar
version = 164  // Nova versão
```

### Descrição Clara

```kotlin
// ❌ ERRADO - Vago
description = "MaxSeries v164 - Fix"

// ✅ CORRETO - Específico
description = "MaxSeries v164 - FIX: MegaEmbed timeout aumentado para 120s"
```

### Testar Antes de Fazer Deploy

```powershell
# 1. Build local
.\gradlew.bat MaxSeries:make --no-daemon

# 2. Instalar manualmente no dispositivo via ADB
adb install -r MaxSeries\build\MaxSeries.cs3

# 3. Testar funcionalidade

# 4. Se tudo OK, fazer deploy
.\deploy.ps1
```

## 📚 Referências

- [GitHub CLI Documentation](https://cli.github.com/manual/)
- [CloudStream Plugin Development](https://recloudstream.github.io/dokka/)
- [Gradle Build Tool](https://gradle.org/)

## 🆘 Suporte

Se encontrar problemas:
1. Verifique os logs do script
2. Execute cada step manualmente para identificar onde falha
3. Consulte a seção Troubleshooting acima

---

**Criado por**: Antigravity AI  
**Data**: 23/01/2026  
**Versão**: 1.0
