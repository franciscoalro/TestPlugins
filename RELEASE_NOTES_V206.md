# Release v206 - Kotlin 2.3.0 Upgrade

## 🎉 Novidades

### 7 Providers Disponíveis
Esta release inclui **7 providers** totalmente funcionais:

1. **AnimesOnlineCC** v10 (15.57 KB)
2. **MaxSeries** v206 (190.49 KB)
3. **MegaFlix** v2 (16.41 KB)
4. **NetCine** v2 (19.59 KB)
5. **OverFlix** v2 (25.50 KB)
6. **PobreFlix** v2 (22.88 KB)
7. **Vizer** v2 (25.75 KB)

## 🔧 Mudanças Técnicas

### Kotlin 2.3.0 Upgrade
- ✅ Atualizado de Kotlin 1.9.23 para 2.3.0
- ✅ Compatível com Cloudstream library (commit 8a4480dc42)
- ✅ Todas as dependências atualizadas

### Correções de API
- ✅ **Vizer**: Corrigido uso da API `Score` (de `Int?` para `Score.from10()`)
- ✅ Todos os providers compilando sem erros
- ✅ Build otimizado e estável

### Dependências Atualizadas
```kotlin
- Kotlin: 2.3.0
- kotlinx-coroutines-android: 1.10.1
- kotlinx-serialization-json: 1.8.0
- Android Gradle Plugin: 8.13.2
```

## 📦 Instalação

### Método 1: Via Repositório (Recomendado)
1. Abra o Cloudstream
2. Vá em **Configurações** → **Extensões**
3. Adicione o repositório:
   ```
   https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/repo.json
   ```
4. Instale os providers desejados

### Método 2: Download Manual
1. Baixe os arquivos `.cs3` desta release
2. Abra o Cloudstream
3. Vá em **Configurações** → **Extensões** → **Instalar de arquivo**
4. Selecione o arquivo `.cs3` baixado

## 🔗 Links dos Providers

| Provider | Versão | Download |
|----------|--------|----------|
| AnimesOnlineCC | v10 | [Download](https://github.com/franciscoalro/TestPlugins/releases/download/v206/AnimesOnlineCC.cs3) |
| MaxSeries | v206 | [Download](https://github.com/franciscoalro/TestPlugins/releases/download/v206/MaxSeries.cs3) |
| MegaFlix | v2 | [Download](https://github.com/franciscoalro/TestPlugins/releases/download/v206/MegaFlix.cs3) |
| NetCine | v2 | [Download](https://github.com/franciscoalro/TestPlugins/releases/download/v206/NetCine.cs3) |
| OverFlix | v2 | [Download](https://github.com/franciscoalro/TestPlugins/releases/download/v206/OverFlix.cs3) |
| PobreFlix | v2 | [Download](https://github.com/franciscoalro/TestPlugins/releases/download/v206/PobreFlix.cs3) |
| Vizer | v2 | [Download](https://github.com/franciscoalro/TestPlugins/releases/download/v206/Vizer.cs3) |

## 🐛 Problemas Conhecidos

Nenhum problema conhecido nesta versão.

## 📝 Changelog Completo

### MaxSeries (v205 → v206)
- Upgrade para Kotlin 2.3.0
- Build fixes e otimizações
- Compatibilidade melhorada

### AnimesOnlineCC (v9 → v10)
- Upgrade para Kotlin 2.3.0
- Melhorias de estabilidade

### Novos Providers (v1 → v2)
- MegaFlix, NetCine, OverFlix, PobreFlix, Vizer
- Primeira release pública
- Upgrade para Kotlin 2.3.0
- API Score corrigida

## 🙏 Créditos

Desenvolvido por **franciscoalro**

## 📄 Licença

Este projeto é open source e está disponível sob a licença MIT.
