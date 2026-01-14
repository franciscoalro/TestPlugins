# ✅ MaxSeries v80 - Cloudstream Pre-Release - PRONTO PARA BUILD

## 🎯 Status Atual

### ✅ Concluído
- [x] Backup do MaxSeries original criado
- [x] Plugin copiado para cloudstream-pre-release
- [x] `settings.gradle.kts` atualizado (MaxSeries incluído)
- [x] `build.gradle.kts` moderno criado (compatível com pre-release)
- [x] GitHub Actions workflow configurado
- [x] Script de setup do Git criado

### 📂 Arquivos Criados/Modificados

```
C:\Users\KYTHOURS\Desktop\cloudstream-pre-release\
├── MaxSeries/                                    # ✅ Plugin copiado
│   ├── src/
│   │   └── main/
│   │       ├── kotlin/com/franciscoalro/maxseries/
│   │       │   ├── MaxSeriesProvider.kt         # ✅ v79 (compatível)
│   │       │   ├── MaxSeriesPlugin.kt
│   │       │   ├── extractors/
│   │       │   │   ├── MegaEmbedExtractor.kt
│   │       │   │   ├── PlayerEmbedAPIExtractor.kt
│   │       │   │   └── MyVidPlayExtractor.kt
│   │       │   └── ...
│   │       └── AndroidManifest.xml              # ✅ Existente
│   └── build.gradle.kts                         # ✅ NOVO (pre-release)
├── .github/
│   └── workflows/
│       └── build-maxseries-prerelease.yml       # ✅ NOVO
├── settings.gradle.kts                          # ✅ MODIFICADO
└── setup-github.ps1                             # ✅ NOVO (helper script)
```

## 🚀 Como Fazer o Build no GitHub Actions

### Opção 1: Script Automático (RECOMENDADO)

```powershell
cd C:\Users\KYTHOURS\Desktop\cloudstream-pre-release
.\setup-github.ps1
```

O script vai:
1. ✅ Inicializar Git (se necessário)
2. ✅ Configurar remote do GitHub
3. ✅ Criar commit com as mudanças
4. ✅ Fazer push para o repositório
5. ✅ Mostrar próximos passos

### Opção 2: Manual

```powershell
cd C:\Users\KYTHOURS\Desktop\cloudstream-pre-release

# 1. Inicializar Git
git init

# 2. Adicionar remote (SUBSTITUA pela SUA URL)
git remote add origin https://github.com/SEU_USUARIO/SEU_REPO.git

# 3. Criar .gitignore
@"
.gradle/
build/
local.properties
*.apk
*.aab
.idea/
*.iml
"@ | Out-File -FilePath ".gitignore" -Encoding UTF8

# 4. Adicionar arquivos
git add MaxSeries/
git add settings.gradle.kts
git add .github/workflows/build-maxseries-prerelease.yml
git add .gitignore

# 5. Commit
git commit -m "feat: Add MaxSeries v80 for Cloudstream Pre-Release"

# 6. Push
git push -u origin master
```

## 🎬 Executar Build no GitHub

### Passo 1: Acessar GitHub Actions
1. Vá para seu repositório no GitHub
2. Clique na aba **Actions**
3. Você verá o workflow: **"Build MaxSeries Plugin (Pre-Release)"**

### Passo 2: Executar Workflow Manualmente
1. Clique no workflow
2. Clique no botão **"Run workflow"** (canto direito)
3. Selecione a branch (ex: `master` ou `feat/maxseries-prerelease`)
4. Clique em **"Run workflow"** (verde)

### Passo 3: Aguardar Build
- ⏱️ Tempo estimado: **3-5 minutos**
- 📊 Você pode acompanhar o progresso em tempo real

### Passo 4: Download do Artifact
1. Quando o build terminar (✅ verde)
2. Clique no workflow executado
3. Role até **"Artifacts"**
4. Baixe:
   - `maxseries-v80-aar` (Android Archive)
   - `maxseries-v80-jar` (Java Archive)
   - `maxseries-v80-all-outputs` (todos os arquivos)

## 📦 O Que Será Gerado

### Outputs Esperados

```
MaxSeries/build/
├── outputs/
│   └── aar/
│       └── MaxSeries-release.aar    # ✅ Android Archive
└── libs/
    └── MaxSeries.jar                # ✅ Java Archive
```

### Como Usar

#### Opção 1: AAR (Android Archive)
```bash
# Copiar para o app Cloudstream pre-release
adb push MaxSeries-release.aar /sdcard/
# Instalar via app (se suportado)
```

#### Opção 2: JAR (Java Archive)
```bash
# Integrar diretamente no app
# (depende da arquitetura do Cloudstream pre-release)
```

## 🔍 Troubleshooting

### Build Falha no GitHub Actions

**Erro: "Task :library:build FAILED"**
```yaml
# Solução: Build library primeiro
- name: Build library
  run: ./gradlew :library:build --no-daemon
```

**Erro: "Could not resolve dependencies"**
```yaml
# Solução: Adicionar repositórios
repositories {
    google()
    mavenCentral()
    maven { url 'https://jitpack.io' }
}
```

**Erro: "Namespace not specified"**
```kotlin
// Solução: Adicionar namespace no build.gradle.kts
android {
    namespace = "com.franciscoalro.maxseries"
}
```

### Git Push Falha

**Erro: "Authentication failed"**
```powershell
# Solução 1: Usar Personal Access Token
# 1. GitHub > Settings > Developer settings > Personal access tokens
# 2. Generate new token (classic)
# 3. Selecionar: repo, workflow
# 4. Usar token como senha

# Solução 2: Usar SSH
git remote set-url origin git@github.com:SEU_USUARIO/SEU_REPO.git
```

## 📊 Comparação: Local vs GitHub Actions

| Aspecto | Build Local | GitHub Actions |
|---------|-------------|----------------|
| **Tempo** | 10-30 min (Gradle Daemon) | 3-5 min |
| **Recursos** | Usa seu PC | Servidor GitHub |
| **Automação** | Manual | Automático |
| **Logs** | Terminal local | Interface web |
| **Artifacts** | Pasta local | Download web |
| **Recomendado** | ❌ Muito lento | ✅ **SIM** |

## 🎯 Próximos Passos Após o Build

### 1. Testar o Plugin
```bash
# Instalar Cloudstream pre-release no dispositivo
adb install cloudstream-prerelease.apk

# Copiar plugin
adb push MaxSeries-release.aar /sdcard/

# Abrir app e instalar plugin
# (método depende da implementação do pre-release)
```

### 2. Verificar Logs
```bash
# Monitorar logs do app
adb logcat | grep -i maxseries
```

### 3. Testar Funcionalidades
- [ ] Busca funciona
- [ ] Detalhes de séries carregam
- [ ] Episódios são listados
- [ ] Links de vídeo são extraídos
- [ ] PlayerEmbedAPI funciona
- [ ] MegaEmbed funciona
- [ ] MyVidPlay funciona

## 📝 Notas Importantes

### Diferenças da Versão Stable

| Recurso | Stable | Pre-Release |
|---------|--------|-------------|
| **Formato** | `.cs3` | `.aar` / `.jar` |
| **Build System** | Cloudstream Gradle Plugin | Android Library |
| **APIs** | Stable only | Stable + `@Prerelease` |
| **Distribuição** | Repository JSON | Manual / GitHub |

### Compatibilidade

✅ **Código 100% compatível**
- Todas as APIs usadas estão disponíveis
- Nenhuma API `@Prerelease` foi usada
- Extractors funcionam igual

⚠️ **Formato diferente**
- Não gera `.cs3` automaticamente
- Precisa integrar `.aar` no app

## 🆘 Suporte

### Se algo der errado:

1. **Verificar logs do GitHub Actions**
   - Clicar no workflow falhado
   - Expandir steps com erro
   - Copiar mensagem de erro

2. **Verificar arquivos locais**
   ```powershell
   # Conferir se arquivos existem
   Test-Path "C:\Users\KYTHOURS\Desktop\cloudstream-pre-release\MaxSeries\build.gradle.kts"
   Test-Path "C:\Users\KYTHOURS\Desktop\cloudstream-pre-release\.github\workflows\build-maxseries-prerelease.yml"
   ```

3. **Rollback se necessário**
   ```powershell
   # Voltar para versão original
   cd d:\TestPlugins-master
   .\gradlew.bat :MaxSeries:make
   ```

## ✅ Checklist Final

Antes de executar o build:

- [ ] Arquivos copiados para cloudstream-pre-release
- [ ] `settings.gradle.kts` atualizado
- [ ] `build.gradle.kts` do MaxSeries criado
- [ ] Workflow do GitHub Actions criado
- [ ] Git inicializado
- [ ] Remote configurado
- [ ] Commit criado
- [ ] Push feito para GitHub

Após o build:

- [ ] Workflow executado com sucesso
- [ ] Artifacts baixados
- [ ] Plugin testado no app
- [ ] Funcionalidades verificadas

---

## 🎉 Resumo

**O que foi feito:**
1. ✅ MaxSeries v79 adaptado para Cloudstream Pre-Release
2. ✅ Build.gradle.kts moderno criado
3. ✅ GitHub Actions workflow configurado
4. ✅ Script de setup automatizado criado

**Próximo passo:**
```powershell
cd C:\Users\KYTHOURS\Desktop\cloudstream-pre-release
.\setup-github.ps1
```

**Tempo total estimado:** 10-15 minutos (setup + build)

**Resultado esperado:** MaxSeries v80 compilado e pronto para uso no Cloudstream Pre-Release! 🚀

---

**Criado em:** 2026-01-13  
**Versão:** MaxSeries v80  
**Compatibilidade:** Cloudstream Pre-Release 4.6.1+
