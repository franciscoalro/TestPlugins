# 📋 Plano de Migração: Cloudstream Pre-Release

## 🎯 Objetivo
Atualizar o plugin MaxSeries v79 para compatibilidade com Cloudstream Pre-Release localizado em:
`C:\Users\KYTHOURS\Desktop\cloudstream-pre-release`

## 📊 Análise Comparativa

### Versão Atual (TestPlugins-master)
- **Build System**: Gradle 8.2.1
- **Kotlin**: 2.1.0
- **Cloudstream Library**: `com.github.recloudstream.cloudstream:library:-SNAPSHOT`
- **Estrutura**: Plugin tradicional com `build.gradle.kts` customizado
- **Namespace**: `com.recloudstream`
- **Min SDK**: 21
- **Target SDK**: 34
- **Compile SDK**: 34

### Versão Pre-Release (cloudstream-pre-release)
- **Build System**: Gradle com version catalogs (libs.versions.toml)
- **Kotlin Multiplatform**: Suporte a Android + JVM
- **Cloudstream Library**: Biblioteca local multiplatform
- **Estrutura**: Arquitetura moderna com multiplatform
- **Namespace**: `com.lagradost.api` (biblioteca)
- **Anotação @Prerelease**: APIs exclusivas da pre-release

## 🔍 Principais Diferenças Detectadas

### 1. **API Changes**
```kotlin
// ✅ COMPATÍVEL - Mantido na pre-release
abstract class MainAPI {
    open var name = "NONE"
    open var mainUrl = "NONE"
    open var lang = "en"
    open val hasMainPage = false
    open val supportedTypes = setOf(...)
    
    open suspend fun getMainPage(page: Int, request: MainPageRequest): HomePageResponse?
    open suspend fun search(query: String): List<SearchResponse>?
    open suspend fun load(url: String): LoadResponse?
    open suspend fun loadLinks(...): Boolean
}
```

### 2. **Annotation @Prerelease**
- Nova anotação para APIs exclusivas da pre-release
- Causa crash em versões stable se usada
- **Ação**: Verificar se MaxSeries usa alguma API marcada com @Prerelease

### 3. **Build Configuration**
```kotlin
// ATUAL (TestPlugins-master)
buildscript {
    dependencies {
        classpath("com.android.tools.build:gradle:8.2.1")
        classpath("com.github.recloudstream:gradle:cce1b8d84d")
        classpath("org.jetbrains.kotlin:kotlin-gradle-plugin:2.1.0")
    }
}

// PRE-RELEASE (cloudstream-pre-release)
plugins {
    alias(libs.plugins.android.application) apply false
    alias(libs.plugins.kotlin.multiplatform) apply false
    alias(libs.plugins.buildkonfig) apply false
}
```

## 📝 Checklist de Compatibilidade

### ✅ APIs Compatíveis (Sem mudanças necessárias)
- [x] `MainAPI` base class
- [x] `TvType` enum (Movie, TvSeries)
- [x] `SearchResponse` / `LoadResponse`
- [x] `ExtractorLink` / `SubtitleFile`
- [x] `newMovieSearchResponse()`
- [x] `newTvSeriesLoadResponse()`
- [x] `newEpisode()`
- [x] `app.get()` / `app.post()`
- [x] `fixUrl()` / `fixUrlNull()`
- [x] `loadExtractor()`

### ⚠️ Verificações Necessárias
- [ ] Uso de `android.util.Log` → Migrar para `com.lagradost.api.Log`
- [ ] Imports de `com.lagradost.cloudstream3.*`
- [ ] WebView APIs (verificar se há mudanças)
- [ ] Extractors customizados (MegaEmbed, PlayerEmbedAPI, MyVidPlay)

### 🔧 Mudanças Recomendadas

#### 1. **Logging**
```kotlin
// ❌ ATUAL
import android.util.Log
Log.d(TAG, "mensagem")

// ✅ PRE-RELEASE
import com.lagradost.api.Log
Log.d(TAG, "mensagem")
```

#### 2. **Build.gradle.kts do Plugin**
```kotlin
// Manter estrutura atual, mas verificar dependências
version = 80 // Incrementar versão

cloudstream {
    description = "MaxSeries v80 - Cloudstream Pre-Release Compatible"
    authors = listOf("franciscoalro")
    status = 1
    tvTypes = listOf("TvSeries", "Movie")
    language = "pt-BR"
    iconUrl = "https://www.maxseries.one/wp-content/themes/dooplay/assets/img/favicon.png"
}
```

## 🚀 Plano de Ação

### Fase 1: Análise de Compatibilidade ✅
- [x] Comparar estruturas de diretórios
- [x] Analisar MainAPI.kt da pre-release
- [x] Identificar breaking changes
- [x] Documentar diferenças

### Fase 2: Preparação do Ambiente
1. **Backup do projeto atual**
   ```powershell
   Copy-Item "d:\TestPlugins-master" "d:\TestPlugins-master-backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')" -Recurse
   ```

2. **Verificar estrutura da pre-release**
   - Localizar `library/` module
   - Verificar `build.gradle.kts` root
   - Analisar `gradle.properties`

### Fase 3: Migração do Plugin
1. **Copiar plugin para pre-release**
   ```powershell
   # Criar diretório do plugin
   New-Item -Path "C:\Users\KYTHOURS\Desktop\cloudstream-pre-release\MaxSeries" -ItemType Directory -Force
   
   # Copiar arquivos
   Copy-Item "d:\TestPlugins-master\MaxSeries\*" "C:\Users\KYTHOURS\Desktop\cloudstream-pre-release\MaxSeries\" -Recurse
   ```

2. **Atualizar settings.gradle.kts**
   ```kotlin
   // Adicionar ao settings.gradle.kts da pre-release
   include(":MaxSeries")
   ```

3. **Ajustar imports se necessário**
   - Verificar `android.util.Log` → `com.lagradost.api.Log`
   - Confirmar imports de `com.lagradost.cloudstream3.*`

### Fase 4: Build e Teste
1. **Build local**
   ```powershell
   cd "C:\Users\KYTHOURS\Desktop\cloudstream-pre-release"
   .\gradlew.bat :MaxSeries:make
   ```

2. **Verificar .cs3 gerado**
   ```powershell
   Get-ChildItem -Path "C:\Users\KYTHOURS\Desktop\cloudstream-pre-release\MaxSeries\build" -Recurse -Filter "*.cs3"
   ```

3. **Testar no app**
   - Instalar .cs3 no Cloudstream pre-release
   - Testar busca, load, loadLinks
   - Verificar logs via `adb logcat`

### Fase 5: Validação
- [ ] Busca funciona
- [ ] Detalhes de séries carregam
- [ ] Episódios são listados
- [ ] Links de vídeo são extraídos
- [ ] Todos os extractors funcionam (PlayerEmbedAPI, MegaEmbed, MyVidPlay, etc.)

## 📌 Notas Importantes

### Compatibilidade Retroativa
O código atual do MaxSeries v79 **deve ser compatível** com a pre-release porque:
1. ✅ Não usa APIs marcadas com `@Prerelease`
2. ✅ Usa apenas APIs core do Cloudstream
3. ✅ Estrutura de plugin padrão
4. ✅ Dependências comuns (jsoup, okhttp, webkit)

### Possíveis Problemas
1. **Logging**: `android.util.Log` pode não estar disponível em contexto multiplatform
   - **Solução**: Usar `com.lagradost.api.Log`

2. **WebView**: Verificar se `androidx.webkit.WebView` funciona igual
   - **Solução**: Testar extractors que usam WebView (MegaEmbed, PlayerEmbedAPI)

3. **Build System**: Gradle pode ter configurações diferentes
   - **Solução**: Adaptar `build.gradle.kts` se necessário

## 🔄 Rollback Plan
Se houver problemas:
1. Manter versão atual em `d:\TestPlugins-master`
2. Criar branch separado para pre-release
3. Testar isoladamente antes de merge

## 📚 Referências
- Cloudstream Pre-Release: `C:\Users\KYTHOURS\Desktop\cloudstream-pre-release`
- Plugin Atual: `d:\TestPlugins-master\MaxSeries`
- Documentação: `d:\TestPlugins-master\docs\`

---

**Status**: ✅ Análise Completa - Pronto para Fase 2
**Próximo Passo**: Executar backup e copiar plugin para pre-release
**Risco**: 🟢 Baixo (APIs compatíveis, mudanças mínimas necessárias)
