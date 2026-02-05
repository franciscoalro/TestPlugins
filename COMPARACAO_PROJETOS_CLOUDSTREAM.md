# COMPARAÇÃO DE PROJETOS CLOUDSTREAM3

## PROJETOS ANALISADOS

| | PROJETO 1 (Funcional) | PROJETO 2 (Com problema) |
|---|----------------------|-------------------------|
| **Repositório** | https://github.com/saimuelbr/saimuelrepo | https://github.com/franciscoalro/TestPlugins |
| **Build** | Manual | GitHub Actions |
| **Tamanho .cs3** | ~15-50 KB | ~290-750 KB |

---

## 1. DIFERENÇAS NO build.gradle.kts (ROOT)

### 1.1 VERSÃO DO PLUGIN GRADLE (CRÍTICO)

| Funcional | Problemático |
|-----------|--------------|
| `classpath("com.github.recloudstream:gradle:master-SNAPSHOT")` | `classpath("com.github.recloudstream:gradle:-SNAPSHOT")` |

**PROBLEMA**: O projeto problemático usa `"-SNAPSHOT"` sem `"master"`, pode pegar versões instáveis ou incompatíveis!

### 1.2 CONFIGURAÇÃO DO REPOSITÓRIO (CRÍTICO)

**Funcional:**
```kotlin
cloudstream {
    setRepo("https://github.com/saimuelbr/saimuelrepo/main")
    authors = listOf("saimuelbr")
}
```

**Problemático:**
```kotlin
cloudstream {
    setRepo(System.getenv("GITHUB_REPOSITORY") ?: "user/repo")
}
```

**PROBLEMA**: O projeto problemático usa variável de ambiente que pode não estar configurada corretamente durante o build!

### 1.3 NAMESPACE

| Funcional | Problemático |
|-----------|--------------|
| `namespace = "com.saimuelbr"` | `namespace = "com.example"` |

**PROBLEMA**: Namespace genérico pode causar conflitos.

### 1.4 DEPENDÊNCIAS

| Biblioteca | Funcional | Problemático |
|------------|-----------|--------------|
| NiceHttp | 0.4.13 | 0.4.11 |
| jsoup | 1.19.1 | 1.18.3 |
| jackson | 2.16.0 | 2.13.1 |

**PROBLEMA**: Versões mais antigas podem ter bugs ou incompatibilidades.

### 1.5 DEPENDÊNCIAS ADICIONAIS (Funcional)

O projeto funcional inclui bibliotecas adicionais que o problemático não tem:
- `kotlinx-coroutines-android:1.10.1`
- `rhino:1.8.0`
- `fuzzywuzzy:1.4.0`
- `gson:2.11.0`
- `kotlinx-serialization-json:1.8.0`
- `quickjs-android:0.9.2`
- `jadb:v1.2.1`

---

## 2. DIFERENÇAS NO build.gradle.kts (PLUGIN)

### 2.1 DEPENDÊNCIAS DESNECESSÁRIAS (CRÍTICO)

**Problemático tem:**
```kotlin
dependencies {
    implementation("com.google.android.material:material:1.12.0")
    implementation("androidx.recyclerview:recyclerview:1.3.2")
}
```

**PROBLEMA**: Plugins CloudStream3 NÃO devem incluir dependências de UI Android! Isso pode causar conflitos com o CloudStream.

### 2.2 BUILD FEATURES DESNECESSÁRIAS

**Problemático tem:**
```kotlin
android {
    buildFeatures {
        buildConfig = true
        viewBinding = true
    }
}
```

**PROBLEMA**: `viewBinding` não é necessário para plugins CloudStream3 e pode aumentar o tamanho do arquivo desnecessariamente.

### 2.3 CONFIGURAÇÃO DE IDIOMA

| Funcional | Problemático |
|-----------|--------------|
| `language = "pt-br"` | `language = "en"` |

### 2.4 CROSS PLATFORM

| Funcional | Problemático |
|-----------|--------------|
| `isCrossPlatform = true` | (não definido) |

**PROBLEMA**: Sem `isCrossPlatform`, o plugin pode não funcionar em todos os dispositivos.

---

## 3. DIFERENÇAS NAS CLASSES PLUGIN E PROVIDER

### 3.1 CLASSE PLUGIN (CRÍTICO)

**Funcional:**
```kotlin
package com.AnimesCloud

import com.lagradost.cloudstream3.plugins.BasePlugin
import com.lagradost.cloudstream3.plugins.CloudstreamPlugin

@CloudstreamPlugin
class AnimesCloudProvider : BasePlugin() {
    override fun load() {
        registerMainAPI(AnimesCloud())
    }
}
```

**Problemático:**
```kotlin
package com.example

import android.content.Context
import androidx.appcompat.app.AppCompatActivity
import com.lagradost.cloudstream3.plugins.CloudstreamPlugin
import com.lagradost.cloudstream3.plugins.Plugin

@CloudstreamPlugin
class ExamplePlugin: Plugin() {
    private var activity: AppCompatActivity? = null

    override fun load(context: Context) {
        activity = context as? AppCompatActivity
        registerMainAPI(ExampleProvider())
        
        openSettings = {
            val frag = BlankFragment(this)
            activity?.let {
                frag.show(it.supportFragmentManager, "Frag")
            }
        }
    }
}
```

**PROBLEMAS**:
- A classe Plugin do projeto problemático estende `Plugin()` e tenta manipular Activities Android
- Isso pode causar crashes no CloudStream3
- A classe funcional estende `BasePlugin()` que é a forma correta e minimal

### 3.2 CLASSE PROVIDER

**Funcional**: Implementação completa com todos os métodos necessários (search, load, getMainPage, etc.)

**Problemático**: Implementação mínima que só retorna lista vazia

---

## 4. DIFERENÇAS NO AndroidManifest.xml

**Ambos estão corretos:**
```xml
<?xml version="1.0" encoding="utf-8"?>
<manifest />
```

---

## 5. DIFERENÇAS NOS ARQUIVOS GERADOS (.cs3)

### PROJETO FUNCIONAL (saimuelbr/saimuelrepo):
- Tamanho típico: ~15-50KB por plugin
- Estrutura: Plugins individuais (AnimesCloud.cs3, NetCine.cs3, etc.)
- Formato: .cs3 (Android library comprimida)

### PROJETO PROBLEMÁTICO (franciscoalro/TestPlugins):
- Tamanho típico: ~290KB a ~750KB (MaxSeries.cs3)
- Última versão (v264): MaxSeries.cs3 - 747.480 bytes

**PROBLEMAS**:
1. Tamanho excessivamente grande (>700KB vs <50KB)
2. Inclui dependências UI que não deveriam estar lá
3. Estrutura de plugins pode estar incorreta

---

## 6. CONFIGURAÇÕES IMPORTANTES QUE ESTÃO FALTANDO

### 6.1 GRADLE.PROPERTIES

**Funcional tem:**
```properties
android.buildFeatures.buildConfig=true
```

**Problemático NÃO tem essa linha**

### 6.2 WORKFLOW GITHUB ACTIONS

**Problemático**: Usa workflow complexo com checkout de branch "builds"

O workflow:
- Faz checkout do código
- Faz checkout da branch "builds" separadamente
- Copia arquivos .cs3 para pasta builds
- Faz commit e push automático

**PROBLEMA**: Esse processo pode estar causando problemas de permissão ou sincronização incorreta dos arquivos.

---

## 7. CAUSA RAIZ DO ERRO 'NÃO CONSEGUE BAIXAR O PLUGIN'

### 7.1 REPOSITÓRIO MAL CONFIGURADO NO BUILD.GRADLE.KTS (MAIS CRÍTICO)

O projeto problemático usa:
```kotlin
setRepo(System.getenv("GITHUB_REPOSITORY") ?: "user/repo")
```

**Problemas**:
- Durante o build local, GITHUB_REPOSITORY pode não estar definido
- O fallback "user/repo" é inválido
- Resultado: O plugin é compilado com metadados incorretos

**Solução**:
```kotlin
setRepo("https://github.com/franciscoalro/TestPlugins/master")
```

### 7.2 CLASSE PLUGIN INCORRETA

O projeto problemático usa a abordagem antiga/complexa:
```kotlin
class ExamplePlugin: Plugin() { ... }
```

Com manipulação de Activity e Fragment, que pode:
- Causar ClassNotFoundException no CloudStream
- Conflitar com o ciclo de vida do app
- Aumentar drasticamente o tamanho do .cs3

**Solução**: Usar BasePlugin simplificado:
```kotlin
@CloudstreamPlugin
class ExampleProvider : BasePlugin() {
    override fun load() {
        registerMainAPI(ExampleProvider())
    }
}
```

### 7.3 DEPENDÊNCIAS DESNECESSÁRIAS

```kotlin
implementation("com.google.android.material:material:1.12.0")
implementation("androidx.recyclerview:recyclerview:1.3.2")
```

Essas dependências:
- Não são necessárias para plugins CloudStream
- Aumentam o tamanho do arquivo em 500KB+
- Podem causar conflitos de versão com o CloudStream

### 7.4 WORKFLOW GITHUB ACTIONS PROBLEMÁTICO

O workflow atual pode causar:
- Desincronização entre código e artefatos
- Arquivos .cs3 gerados com paths incorretos
- Problemas de cache no GitHub Actions

### 7.5 FALTA DE BUILDCONFIG

No gradle.properties do projeto problemático falta:
```properties
android.buildFeatures.buildConfig=true
```

---

## 8. SOLUÇÕES RECOMENDADAS

### 8.1 CORRIGIR build.gradle.kts (ROOT)

```kotlin
cloudstream {
    setRepo("https://github.com/franciscoalro/TestPlugins/master")
    authors = listOf("franciscoalro")
}
```

### 8.2 SIMPLIFICAR build.gradle.kts (PLUGIN)

```kotlin
version = 1

cloudstream {
    description = "MaxSeries - Séries e Filmes"
    language = "pt-br"
    authors = listOf("franciscoalro")
    status = 1
    tvTypes = listOf("TvSeries", "Movie")
    iconUrl = "https://..."
    isCrossPlatform = true
}

// REMOVER completamente:
// - dependencies { material, recyclerview }
// - android { buildFeatures }
```

### 8.3 REFATORAR CLASSES PLUGIN E PROVIDER

Remover completamente a classe ExamplePlugin.kt atual.

Usar apenas uma classe Provider:
```kotlin
package com.maxseries

import com.lagradost.cloudstream3.plugins.BasePlugin
import com.lagradost.cloudstream3.plugins.CloudstreamPlugin

@CloudstreamPlugin
class MaxSeriesProvider : BasePlugin() {
    override fun load() {
        registerMainAPI(MaxSeries())
    }
}
```

### 8.4 ATUALIZAR gradle.properties

```properties
org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
android.useAndroidX=true
android.enableJetifier=true
android.buildFeatures.buildConfig=true  // ADICIONAR
```

### 8.5 SIMPLIFICAR WORKFLOW

- Fazer upload direto dos .cs3 nas releases
- Não usar branch separada "builds"
- Usar action de release direta

### 8.6 CRIAR repo.json CORRETO

```json
{
    "name": "TestPlugins",
    "description": "Repositório de plugins para CloudStream",
    "manifestVersion": 1,
    "pluginLists": [
        "https://raw.githubusercontent.com/franciscoalro/TestPlugins/builds/plugins.json"
    ]
}
```

---

## RESUMO EXECUTIVO

```
+-----------------------------------------------------------------------------+
|                        RESUMO DAS DIFERENÇAS CRÍTICAS                       |
+-----------------------------------------------------------------------------+
|                                                                             |
|  1. PLUGIN GRADLE: "-SNAPSHOT" vs "master-SNAPSHOT"                         |
|     -> Usar versão master-SNAPSHOT estável                                  |
|                                                                             |
|  2. CONFIGURAÇÃO setRepo(): Variável ambiente vs URL fixa                   |
|     -> Usar URL fixa do repositório                                         |
|                                                                             |
|  3. CLASSE PLUGIN: Plugin() vs BasePlugin()                                 |
|     -> Usar BasePlugin() simplificado                                       |
|                                                                             |
|  4. DEPENDÊNCIAS UI: Material + RecyclerView incluídos                      |
|     -> REMOVER completamente                                                |
|                                                                             |
|  5. TAMANHO .cs3: 747KB vs ~50KB                                            |
|     -> Reduzir removendo dependências desnecessárias                        |
|                                                                             |
|  6. WORKFLOW: Complexo com múltiplos checkouts                              |
|     -> Simplificar para build e release direto                              |
|                                                                             |
|  7. buildConfig: Faltando no gradle.properties                              |
|     -> Adicionar android.buildFeatures.buildConfig=true                     |
|                                                                             |
+-----------------------------------------------------------------------------+
```

---

## CHECKLIST PARA CORREÇÃO

- [ ] Atualizar build.gradle.kts root com setRepo fixo
- [ ] Remover dependências UI do build.gradle.kts do plugin
- [ ] Refatorar classe Plugin para usar BasePlugin
- [ ] Remover manipulação de Activity/Fragment
- [ ] Adicionar buildConfig=true no gradle.properties
- [ ] Simplificar workflow GitHub Actions
- [ ] Verificar repo.json está configurado corretamente
- [ ] Testar build local antes de fazer push
