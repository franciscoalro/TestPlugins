# Build System - CloudStream3 Plugins

## Estrutura do Projeto

Este projeto segue a estrutura oficial do CloudStream3 para criação de plugins.

### Diretórios

```
├── MaxSeries/                    # Plugin principal
│   ├── build.gradle.kts          # Configuração do plugin
│   └── src/
│       ├── main/
│       │   ├── AndroidManifest.xml
│       │   └── kotlin/
│       │       └── com/franciscoalro/maxseries/
│       │           ├── MaxSeriesPlugin.kt      # Classe Plugin
│       │           ├── MaxSeriesProvider.kt    # Classe MainAPI
│       │           └── extractors/             # Extractors de vídeo
│       └── test/                               # Testes unitários
├── AnimesOnlineCC/               # Outro plugin
├── Vizer/
├── NetCine/
├── MegaFlix/
├── PobreFlix/
├── OverFlix/
│
├── build.gradle.kts              # Configuração global (root)
├── settings.gradle.kts           # Inclusão dos projetos
├── plugins.json                  # Lista de plugins
├── repo.json                     # Manifest do repositório
└── build_plugins.py              # Script de build
```

## Como Funciona o Build

### 1. Código Fonte → AAR

O Gradle compila o código Kotlin e gera um arquivo `.aar` (Android Archive):

```kotlin
// MaxSeriesPlugin.kt
@CloudstreamPlugin
class MaxSeriesPlugin: Plugin() {
    override fun load(context: Context) {
        registerMainAPI(MaxSeriesProvider())
        registerExtractorAPI(MegaEmbedExtractorV9())
        // ... outros extractors
    }
}
```

### 2. AAR → CS3

O arquivo `.cs3` é simplesmente uma cópia do `.aar` com extensão diferente:

```bash
cp MaxSeries/build/outputs/aar/MaxSeries-release.aar MaxSeries.cs3
```

O CloudStream3 reconhece arquivos `.cs3` como plugins e os instala.

### 3. Estrutura do AAR/CS3

```
MaxSeries.cs3 (ZIP)
├── AndroidManifest.xml
├── classes.jar          # Código compilado (Kotlin → Bytecode)
├── R.txt               # Recursos
└── META-INF/
```

## Executar Build

### Opção 1: Script Python (Recomendado)

```bash
python build_plugins.py
```

Este script:
1. Executa `./gradlew assembleRelease`
2. Copia os AARs como CS3
3. Atualiza `plugins.json` e `repo.json`
4. Verifica a integridade dos arquivos

### Opção 2: Gradle Manual

```bash
# Build específico
./gradlew :MaxSeries:assembleRelease

# Build todos
./gradlew assembleRelease

# Copiar AAR como CS3
cp MaxSeries/build/outputs/aar/MaxSeries-release.aar MaxSeries.cs3
```

## Solução de Problemas

### Erro: "Plugin não instala"

Verifique:
1. **Nome do provider**: Não deve ter espaços ou caracteres especiais
   ```kotlin
   // ❌ Errado
   override var name = "MaxSeries v264"
   
   // ✅ Correto
   override var name = "MaxSeries"
   ```

2. **Classe Plugin**: Deve estender `Plugin()` com `Context`
   ```kotlin
   // ❌ Errado
   class MaxSeriesPlugin: BasePlugin()
   override fun load() { }
   
   // ✅ Correto
   class MaxSeriesPlugin: Plugin()
   override fun load(context: Context) { }
   ```

3. **AndroidManifest.xml**: Deve ser simples
   ```xml
   <?xml version="1.0" encoding="utf-8"?>
   <manifest />
   ```

### Erro: "Nenhum plugin encontrado"

Verifique `plugins.json`:
- Deve ser um **ARRAY** `[]`, não objeto `{}`
- Não deve ter BOM (Byte Order Mark)
- Primeiro byte deve ser `[` (0x5B)

### Erro: "Download falha"

Verifique:
1. URL do arquivo `.cs3` está acessível
2. Tamanho no `plugins.json` corresponde ao arquivo real
3. Arquivo `.cs3` é um ZIP válido (começa com `PK`)

## Links

- **Repo**: `https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/repo.json`
- **Plugins**: `https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/plugins.json`
