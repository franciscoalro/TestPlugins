#!/usr/bin/env python3
"""
Comparação entre dois projetos de plugins CloudStream3
PROJETO 1 (Funcional): https://github.com/saimuelbr/saimuelrepo
PROJETO 2 (Com problema): https://github.com/franciscoalro/TestPlugins
"""

import base64
import json

# ============================================
# 1. COMPARAÇÃO DOS build.gradle.kts (ROOT)
# ============================================

BUILD_GRADLE_SAIMUEL = """
import com.android.build.gradle.BaseExtension
import com.lagradost.cloudstream3.gradle.CloudstreamExtension
import org.jetbrains.kotlin.gradle.dsl.JvmTarget
import org.jetbrains.kotlin.gradle.tasks.KotlinJvmCompile

buildscript {
    repositories {
        google()
        mavenCentral()
        maven("https://jitpack.io")
    }

    dependencies {
        classpath("com.android.tools.build:gradle:8.7.3")
        classpath("com.github.recloudstream:gradle:master-SNAPSHOT")  
        classpath("org.jetbrains.kotlin:kotlin-gradle-plugin:2.1.0")
    }
}

allprojects {
    repositories {
        google()
        mavenCentral()
        maven("https://jitpack.io")
    }
}

fun Project.cloudstream(configuration: CloudstreamExtension.() -> Unit) = extensions.getByName<CloudstreamExtension>("cloudstream").configuration()

fun Project.android(configuration: BaseExtension.() -> Unit) = extensions.getByName<BaseExtension>("android").configuration()

subprojects {
    apply(plugin = "com.android.library")
    apply(plugin = "kotlin-android")
    apply(plugin = "com.lagradost.cloudstream3.gradle")

    cloudstream {
        setRepo("https://github.com/saimuelbr/saimuelrepo/main")  
        authors = listOf("saimuelbr")
    }

    android {
        namespace = "com.saimuelbr"

        defaultConfig {
            minSdk = 21
            compileSdkVersion(35)
            targetSdk = 35
        }

        compileOptions {
            sourceCompatibility = JavaVersion.VERSION_1_8
            targetCompatibility = JavaVersion.VERSION_1_8
        }

        tasks.withType<KotlinJvmCompile> {
            compilerOptions {
                jvmTarget.set(JvmTarget.JVM_1_8)
                freeCompilerArgs.addAll(
                    "-Xno-call-assertions",
                    "-Xno-param-assertions",
                    "-Xno-receiver-assertions"
                )
            }
        }
    }

    dependencies {
        val implementation by configurations
        val cloudstream by configurations
        cloudstream("com.lagradost:cloudstream3:pre-release")

        implementation(kotlin("stdlib"))
        implementation("com.github.Blazter:NiceHttp:0.4.13")
        implementation("org.jsoup:jsoup:1.19.1")
        implementation("com.fasterxml.jackson.module:jackson-module-kotlin:2.16.0")
        implementation("com.fasterxml.jackson.core:jackson-databind:2.16.0")
        implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.10.1")
        implementation("org.mozilla:rhino:1.8.0")
        implementation("me.xdrop:fuzzywuzzy:1.4.0")
        implementation("com.google.code.gson:gson:2.11.0")
        implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.8.0")
        implementation("app.cash.quickjs:quickjs-android:0.9.2")
        implementation("com.github.vidstige:jadb:v1.2.1")
    }
}

task<Delete>("clean") {
    delete(rootProject.layout.buildDirectory)
}
"""

BUILD_GRADLE_FRANCISCO = """
import com.android.build.gradle.BaseExtension
import com.lagradost.cloudstream3.gradle.CloudstreamExtension
import org.jetbrains.kotlin.gradle.dsl.JvmTarget
import org.jetbrains.kotlin.gradle.tasks.KotlinJvmCompile

buildscript {
    repositories {
        google()
        mavenCentral()
        maven("https://jitpack.io")
    }

    dependencies {
        classpath("com.android.tools.build:gradle:8.7.3")
        classpath("com.github.recloudstream:gradle:-SNAPSHOT")  
        classpath("org.jetbrains.kotlin:kotlin-gradle-plugin:2.1.0")
    }
}

allprojects {
    repositories {
        google()
        mavenCentral()
        maven("https://jitpack.io")
    }
}

fun Project.cloudstream(configuration: CloudstreamExtension.() -> Unit) = extensions.getByName<CloudstreamExtension>("cloudstream").configuration()

fun Project.android(configuration: BaseExtension.() -> Unit) = extensions.getByName<BaseExtension>("android").configuration()

subprojects {
    apply(plugin = "com.android.library")
    apply(plugin = "kotlin-android")
    apply(plugin = "com.lagradost.cloudstream3.gradle")

    cloudstream {
        setRepo(System.getenv("GITHUB_REPOSITORY") ?: "user/repo")
    }

    android {
        namespace = "com.example"

        defaultConfig {
            minSdk = 21
            compileSdkVersion(35)
            targetSdk = 35
        }

        compileOptions {
            sourceCompatibility = JavaVersion.VERSION_1_8
            targetCompatibility = JavaVersion.VERSION_1_8
        }

        tasks.withType<KotlinJvmCompile> {
            compilerOptions {
                jvmTarget.set(JvmTarget.JVM_1_8)
                freeCompilerArgs.addAll(
                    "-Xno-call-assertions",
                    "-Xno-param-assertions",
                    "-Xno-receiver-assertions"
                )
            }
        }
    }

    dependencies {
        val cloudstream by configurations
        val implementation by configurations

        cloudstream("com.lagradost:cloudstream3:pre-release")

        implementation(kotlin("stdlib"))
        implementation("com.github.Blazter:NiceHttp:0.4.11")
        implementation("org.jsoup:jsoup:1.18.3")
        implementation("com.fasterxml.jackson.module:jackson-module-kotlin:2.13.1")
    }
}

task<Delete>("clean") {
    delete(rootProject.layout.buildDirectory)
}
"""

# ============================================
# 2. COMPARAÇÃO DOS build.gradle.kts (PLUGIN)
# ============================================

PLUGIN_BUILD_SAIMUEL = """
version = 1

cloudstream {
    description = "AnimesCloud - Animes em FHD e HD"
    language = "pt-br"
    authors = listOf("saimuelbr")
    status = 1
    tvTypes = listOf("Anime", "AnimeMovie")
    iconUrl = "https://animesonline.cloud/wp-content/uploads/2025/06/logo_1_.png"
    isCrossPlatform = true
}
"""

PLUGIN_BUILD_FRANCISCO = """
dependencies {
    implementation("com.google.android.material:material:1.12.0")
    implementation("androidx.recyclerview:recyclerview:1.3.2")
}

version = 1

cloudstream {
    description = "Lorem ipsum"
    authors = listOf("Cloudburst", "Luna712")

    status = 1  // 0: Down, 1: Ok, 2: Slow, 3: Beta-only

    tvTypes = listOf("Movie")

    requiresResources = true
    language = "en"

    iconUrl = "https://upload.wikimedia.org/wikipedia/commons/2/2f/Koridune_Logo.png"
}

android {
    buildFeatures {
        buildConfig = true
        viewBinding = true
    }
}
"""

# ============================================
# 3. COMPARAÇÃO DAS CLASSES PLUGIN E PROVIDER
# ============================================

# Projeto Funcional (Saimuel)
SAIMUEL_PROVIDER_KT = """
package com.AnimesCloud

import com.lagradost.cloudstream3.plugins.BasePlugin
import com.lagradost.cloudstream3.plugins.CloudstreamPlugin

@CloudstreamPlugin
class AnimesCloudProvider : BasePlugin() {
    override fun load() {
        registerMainAPI(AnimesCloud())
    }
} 
"""

SAIMUEL_MAIN_KT = """
package com.AnimesCloud

import com.lagradost.cloudstream3.*
// ... imports

class AnimesCloud : MainAPI() {
    override var mainUrl = "https://animesonline.cloud"
    override var name = "AnimesCloud"
    override val hasMainPage = true
    override var lang = "pt-br"
    override val hasDownloadSupport = true
    override val hasQuickSearch = true
    override val supportedTypes = setOf(TvType.Anime, TvType.AnimeMovie)
    
    // ... resto da implementação
}
"""

# Projeto com Problema (Francisco)
FRANCISCO_PLUGIN_KT = """
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

        // All providers should be added in this manner
        registerMainAPI(ExampleProvider())

        openSettings = {
            val frag = BlankFragment(this)
            activity?.let {
                frag.show(it.supportFragmentManager, "Frag")
            }
        }
    }
}
"""

FRANCISCO_PROVIDER_KT = """
package com.example

import com.lagradost.cloudstream3.MainAPI
import com.lagradost.cloudstream3.SearchResponse
import com.lagradost.cloudstream3.TvType

class ExampleProvider : MainAPI() {
    override var mainUrl = "https://example.com/" 
    override var name = "Example provider"
    override val supportedTypes = setOf(TvType.Movie)

    override var lang = "en"

    override val hasMainPage = true

    override suspend fun search(query: String): List<SearchResponse> {
        return listOf()
    }
}
"""

# ============================================
# 4. COMPARAÇÃO DO AndroidManifest.xml
# ============================================

MANIFEST_SAIMUEL = """<?xml version="1.0" encoding="utf-8"?>
<manifest /> """

MANIFEST_FRANCISCO = """<?xml version="1.0" encoding="utf-8"?>
<manifest />"""

# ============================================
# 5. COMPARAÇÃO DAS CONFIGURAÇÕES GRADLE
# ============================================

GRADLE_PROPS_SAIMUEL = """
org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
android.useAndroidX=true
android.enableJetifier=true
android.buildFeatures.buildConfig=true
"""

GRADLE_PROPS_FRANCISCO = """
org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
android.useAndroidX=true
android.enableJetifier=true
"""

# ============================================
# ANÁLISE DAS DIFERENÇAS
# ============================================

print("=" * 80)
print("ANÁLISE COMPARATIVA: PROJETOS CLOUDSTREAM3")
print("=" * 80)

print("\n" + "=" * 80)
print("1. DIFERENÇAS NO build.gradle.kts (ROOT)")
print("=" * 80)

diferencas_build = """
[ERRO] PROBLEMAS CRÍTICOS ENCONTRADOS:

1. VERSÃO DO PLUGIN GRADLE (CRÍTICO):
   [OK] Funcional:  classpath("com.github.recloudstream:gradle:master-SNAPSHOT")
   [X] Problemático: classpath("com.github.recloudstream:gradle:-SNAPSHOT")
   
   -> O projeto problemático está usando "-SNAPSHOT" sem "master", pode pegar 
     versões instáveis ou incompatíveis!

2. CONFIGURAÇÃO DO REPOSITÓRIO (CRÍTICO):
   [OK] Funcional: 
       cloudstream {
           setRepo("https://github.com/saimuelbr/saimuelrepo/main")
           authors = listOf("saimuelbr")
       }
   
   [X] Problemático:
       cloudstream {
           setRepo(System.getenv("GITHUB_REPOSITORY") ?: "user/repo")
       }
   
   -> O projeto problemático usa variável de ambiente que pode não estar 
     configurada corretamente durante o build!

3. NAMESPACE (IMPORTANTE):
   [OK] Funcional:   namespace = "com.saimuelbr"
   [X] Problemático: namespace = "com.example"
   
   -> Namespace genérico pode causar conflitos.

4. DEPENDÊNCIAS (IMPORTANTE):
   [OK] Funcional: NiceHttp 0.4.13, jsoup 1.19.1, jackson 2.16.0
   [X] Problemático: NiceHttp 0.4.11, jsoup 1.18.3, jackson 2.13.1
   
   -> Versões mais antigas podem ter bugs ou incompatibilidades.

5. DEPENDÊNCIAS ADICIONAIS (FUNCIONAL):
   [OK] Funcional TEM (Problemático NÃO TEM):
     - kotlinx-coroutines-android:1.10.1
     - rhino:1.8.0
     - fuzzywuzzy:1.4.0
     - gson:2.11.0
     - kotlinx-serialization-json:1.8.0
     - quickjs-android:0.9.2
     - jadb:v1.2.1
"""
print(diferencas_build)

print("\n" + "=" * 80)
print("2. DIFERENÇAS NO build.gradle.kts (PLUGIN)")
print("=" * 80)

diferencas_plugin = """
[ERRO] PROBLEMAS CRÍTICOS:

1. DEPENDÊNCIAS DESNECESSÁRIAS (CRÍTICO):
   [X] Problemático tem:
       dependencies {
           implementation("com.google.android.material:material:1.12.0")
           implementation("androidx.recyclerview:recyclerview:1.3.2")
       }
   
   -> Plugins CloudStream3 NÃO devem incluir dependências de UI Android!
     Isso pode causar conflitos com o CloudStream.

2. BUILD FEATURES DESNECESSÁRIAS:
   [X] Problemativo tem:
       android {
           buildFeatures {
               buildConfig = true
               viewBinding = true
           }
       }
   
   -> viewBinding não é necessário para plugins CloudStream3 e pode
     aumentar o tamanho do arquivo desnecessariamente.

3. CONFIGURAÇÃO DE IDIOMA:
   [OK] Funcional: language = "pt-br"
   [X] Problemático: language = "en"
   
   -> Idioma incorreto pode afetar a categorização.

4. CROSS PLATFORM:
   [OK] Funcional: isCrossPlatform = true
   [X] Problemático: (não definido)
   
   -> Sem isCrossPlatform, o plugin pode não funcionar em todos os dispositivos.
"""
print(diferencas_plugin)

print("\n" + "=" * 80)
print("3. DIFERENÇAS NAS CLASSES PLUGIN E PROVIDER")
print("=" * 80)

diferencas_classes = """
[ERRO] PROBLEMAS CRÍTICOS:

1. CLASSE PLUGIN (CRÍTICO):
   [OK] Funcional NÃO precisa de classe Plugin separada, usa:
       @CloudstreamPlugin
       class AnimesCloudProvider : BasePlugin() {
           override fun load() {
               registerMainAPI(AnimesCloud())
           }
       }
   
   [X] Problemático tem classe Plugin complexa com:
       - Import de android.content.Context
       - Import de AppCompatActivity
       - Fragment para configurações
       - Manipulação de activity
   
   -> A classe Plugin do projeto problemático estende "Plugin()" e tenta
     manipular Activities Android, o que pode causar crashes no CloudStream3!
     
   -> A classe funcional estende "BasePlugin()" que é a forma correta e minimal.

2. CLASSE PROVIDER:
   [OK] Funcional: Implementação completa com todos os métodos necessários
      - search()
      - load()
      - getMainPage()
      - etc.
   
   [X] Problemático: Implementação mínima que só retorna lista vazia:
       override suspend fun search(query: String): List<SearchResponse> {
           return listOf()
       }
   
   -> O provider problemático não implementa métodos essenciais!
"""
print(diferencas_classes)

print("\n" + "=" * 80)
print("4. DIFERENÇAS NO AndroidManifest.xml")
print("=" * 80)

diferencas_manifest = """
[OK] AndroidManifest.xml está CORRETO em ambos:
   <?xml version="1.0" encoding="utf-8"?>
   <manifest />
   
-> Não há problemas aqui.
"""
print(diferencas_manifest)

print("\n" + "=" * 80)
print("5. DIFERENÇAS NOS ARQUIVOS GERADOS (.cs3)")
print("=" * 80)

diferencas_arquivos = """
[ERRO] ANÁLISE DOS ARQUIVOS NAS RELEASES:

PROJETO FUNCIONAL (saimuelbr/saimuelrepo):
- Tamanho típico: ~15-50KB por plugin
- Estrutura: Plugins individuais (AnimesCloud.cs3, NetCine.cs3, etc.)
- Formato: .cs3 (Android library comprimida)
- Sem arquivos .jar nas releases

PROJETO PROBLEMÁTICO (franciscoalro/TestPlugins):
- Tamanho típico: ~290KB a ~750KB (MaxSeries.cs3)
- Última versão (v264): MaxSeries.cs3 - 747.480 bytes
- O tamanho grande indica:
  * Muitas dependências incluídas
  * Possíveis recursos desnecessários
  * Bibliotecas Android UI (material, recyclerview) embutidas

[ERRO] PROBLEMAS NOS ARQUIVOS .cs3 DO PROJETO PROBLEMÁTICO:
1. Tamanho excessivamente grande (>700KB vs <50KB)
2. Inclui dependências UI que não deveriam estar lá
3. Estrutura de plugins pode estar incorreta
"""
print(diferencas_arquivos)

print("\n" + "=" * 80)
print("6. CONFIGURAÇÕES IMPORTANTES QUE ESTÃO FALTANDO")
print("=" * 80)

configs_faltando = """
[ERRO] CONFIGURAÇÕES CRÍTICAS FALTANDO NO PROJETO PROBLEMÁTICO:

1. GRADLE.PROPERTIES:
   [OK] Funcional tem: android.buildFeatures.buildConfig=true
   [X] Problemático não tem essa linha

2. ESTRUTURA DO PROJETO:
   [OK] Funcional: Múltiplos módulos (AnimesCloud, NetCine, etc.)
   [X] Problemático: Apenas ExampleProvider
   
3. WORKFLOW GITHUB ACTIONS:
   [OK] Funcional: Não usa GitHub Actions (build manual)
   [X] Problemático: Usa workflow complexo com checkout de branch "builds"
   
   O workflow do problemático:
   - Faz checkout do código
   - Faz checkout da branch "builds" separadamente
   - Copia arquivos .cs3 para pasta builds
   - Faz commit e push automático
   
   -> Esse processo pode estar causando problemas de permissão ou
     sincronização incorreta dos arquivos.

4. REPO.JSON:
   [OK] Funcional: Provavelmente tem repo.json configurado corretamente
   [X] Problemático: A release menciona raw.githubusercontent.com/.../repo.json
     mas pode estar mal configurado.

5. SETTINGS.GRADLE.KTS:
   -> Não conseguimos verificar, mas é essencial para incluir todos os módulos.
"""
print(configs_faltando)

print("\n" + "=" * 80)
print("7. CAUSA RAIZ DO ERRO 'NÃO CONSEGUE BAIXAR O PLUGIN'")
print("=" * 80)

causa_raiz = """
[ERRO][ERRO][ERRO] PRINCIPAIS CAUSAS DO ERRO: [ERRO][ERRO][ERRO]

1. **REPOSITÓRIO MAL CONFIGURADO NO BUILD.GRADLE.KTS** (MAIS CRÍTICO):
   
   O projeto problemático usa:
       setRepo(System.getenv("GITHUB_REPOSITORY") ?: "user/repo")
   
   Problemas:
   - Durante o build local, GITHUB_REPOSITORY pode não estar definido
   - O fallback "user/repo" é inválido
   - Resultado: O plugin é compilado com metadados incorretos
   
   Solução:
       setRepo("https://github.com/franciscoalro/TestPlugins/master")

2. **CLASSE PLUGIN INCORRETA**:
   
   O projeto problemático usa a abordagem antiga/complexa:
       class ExamplePlugin: Plugin() { ... }
   
   Com manipulação de Activity e Fragment, que pode:
   - Causar ClassNotFoundException no CloudStream
   - Conflitar com o ciclo de vida do app
   - Aumentar drasticamente o tamanho do .cs3
   
   Solução: Usar BasePlugin simplificado:
       @CloudstreamPlugin
       class ExampleProvider : BasePlugin() {
           override fun load() {
               registerMainAPI(ExampleProvider())
           }
       }

3. **DEPENDÊNCIAS DESNECESSÁRIAS**:
   
   implementation("com.google.android.material:material:1.12.0")
   implementation("androidx.recyclerview:recyclerview:1.3.2")
   
   Essas dependências:
   - Não são necessárias para plugins CloudStream
   - Aumentam o tamanho do arquivo em 500KB+
   - Podem causar conflitos de versão com o CloudStream

4. **WORKFLOW GITHUB ACTIONS PROBLEMÁTICO**:
   
   O workflow atual:
   - Faz checkout para pasta "src"
   - Faz checkout da branch "builds" separada
   - Copia arquivos entre pastas
   - Committa na branch builds
   
   Isso pode causar:
   - Desincronização entre código e artefatos
   - Arquivos .cs3 gerados com paths incorretos
   - Problemas de cache no GitHub Actions

5. **FALTA DE BUILDCONFIG**:
   
   No gradle.properties do projeto problemático falta:
       android.buildFeatures.buildConfig=true
   
   Isso pode causar erros durante a compilação.
"""
print(causa_raiz)

print("\n" + "=" * 80)
print("8. SOLUÇÕES RECOMENDADAS")
print("=" * 80)

solucoes = """
[OK] SOLUÇÕES PARA CORRIGIR O PROJETO PROBLEMÁTICO:

1. **CORRIGIR build.gradle.kts (ROOT)**:
   ```kotlin
   cloudstream {
       setRepo("https://github.com/franciscoalro/TestPlugins/master")
       authors = listOf("franciscoalro")
   }
   ```

2. **SIMPLIFICAR build.gradle.kts (PLUGIN)**:
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

3. **REFATORAR CLASSES PLUGIN E PROVIDER**:
   
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

4. **ATUALIZAR gradle.properties**:
   ```properties
   org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
   android.useAndroidX=true
   android.enableJetifier=true
   android.buildFeatures.buildConfig=true  // ADICIONAR
   ```

5. **SIMPLIFICAR WORKFLOW**:
   - Fazer upload direto dos .cs3 nas releases
   - Não usar branch separada "builds"
   - Usar action de release direta

6. **CRIAR repo.json CORRETO**:
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
"""
print(solucoes)

print("\n" + "=" * 80)
print("RESUMO EXECUTIVO")
print("=" * 80)

resumo = """
+-----------------------------------------------------------------------------+
|                        RESUMO DAS DIFERENÇAS CRÍTICAS                       |
+-----------------------------------------------------------------------------+
|                                                                             |
|  1. PLUGIN GRADLE: "-SNAPSHOT" vs "master-SNAPSHOT"                        |
|     -> Usar versão master-SNAPSHOT estável                                   |
|                                                                             |
|  2. CONFIGURAÇÃO setRepo(): Variável ambiente vs URL fixa                   |
|     -> Usar URL fixa do repositório                                          |
|                                                                             |
|  3. CLASSE PLUGIN: Plugin() vs BasePlugin()                                 |
|     -> Usar BasePlugin() simplificado                                        |
|                                                                             |
|  4. DEPENDÊNCIAS UI: Material + RecyclerView incluídos                      |
|     -> REMOVER completamente                                                 |
|                                                                             |
|  5. TAMANHO .cs3: 747KB vs ~50KB                                            |
|     -> Reduzir removendo dependências desnecessárias                         |
|                                                                             |
|  6. WORKFLOW: Complexo com múltiplos checkouts                              |
|     -> Simplificar para build e release direto                               |
|                                                                             |
|  7. buildConfig: Faltando no gradle.properties                              |
|     -> Adicionar android.buildFeatures.buildConfig=true                      |
|                                                                             |
+-----------------------------------------------------------------------------+

[LISTA] CHECKLIST PARA CORREÇÃO:

[ ] Atualizar build.gradle.kts root com setRepo fixo
[ ] Remover dependências UI do build.gradle.kts do plugin
[ ] Refatorar classe Plugin para usar BasePlugin
[ ] Remover manipulação de Activity/Fragment
[ ] Adicionar buildConfig=true no gradle.properties
[ ] Simplificar workflow GitHub Actions
[ ] Verificar repo.json está configurado corretamente
[ ] Testar build local antes de fazer push

"""
print(resumo)
