# TestPlugins - CloudStream Extensions

[![Build and Release](https://github.com/franciscoalro/TestPlugins/actions/workflows/build.yml/badge.svg)](https://github.com/franciscoalro/TestPlugins/actions/workflows/build.yml)
[![Deploy to CloudstreamRepo](https://github.com/franciscoalro/TestPlugins/actions/workflows/deploy-to-cloudstream-repo.yml/badge.svg)](https://github.com/franciscoalro/TestPlugins/actions/workflows/deploy-to-cloudstream-repo.yml)

Repositório de desenvolvimento de extensões para CloudStream 3.

## 🔌 Plugins Disponíveis

### MaxSeries v187 ✅
- **Descrição**: MaxSeries v187 - MegaEmbed V9 (Universal + Triple Click)
- **Status**: ✅ Funcionando (Janeiro 2026)
- **Idioma**: Português (pt-BR)
- **Tipos**: Séries, Filmes
- **Última atualização**: MegaEmbed V9 Integration (Triple Click Bypass)

### AnimesOnlineCC v6 ✅
- **Descrição**: Assista animes online grátis em HD
- **Status**: ✅ Funcionando
- **Idioma**: Português (pt-BR)
- **Tipos**: Anime, OVA, AnimeMovie
- **Última atualização**: Estável

### PobreFlix v1 🆕
- **Descrição**: Assista filmes e séries grátis no PobreFlix
- **Status**: 🆕 Integrado do saimuelrepo-main
- **Idioma**: Português (pt-BR)
- **Tipos**: Filmes, Séries
- **Autor**: saimuelbr

### OverFlix v1 🆕
- **Descrição**: Filmes e séries em alta qualidade no OverFlix
- **Status**: 🆕 Integrado do saimuelrepo-main
- **Idioma**: Português (pt-BR)
- **Tipos**: Filmes, Séries
- **Autor**: saimuelbr

### Vizer v1 🆕
- **Descrição**: Streaming de filmes e séries no Vizer
- **Status**: 🆕 Integrado do saimuelrepo-main
- **Idioma**: Português (pt-BR)
- **Tipos**: Filmes, Séries
- **Autor**: saimuelbr

### MegaFlix v1 🆕
- **Descrição**: Filmes e séries online no MegaFlix
- **Status**: 🆕 Integrado do saimuelrepo-main
- **Idioma**: Português (pt-BR)
- **Tipos**: Filmes, Séries
- **Autor**: saimuelbr

### NetCine v1 🆕
- **Descrição**: Cinema online no NetCine
- **Status**: 🆕 Integrado do saimuelrepo-main
- **Idioma**: Português (pt-BR)
- **Tipos**: Filmes, Séries
- **Autor**: saimuelbr

## 📦 Instalação

### Método 1: Repositório Oficial
1. Abra o CloudStream
2. Vá em **Configurações** → **Extensões** → **Adicionar Repositório**
3. Cole a URL: `https://raw.githubusercontent.com/franciscoalro/CloudstreamRepo/main/plugins.json`
4. Instale os plugins desejados

### Método 2: Download Manual
1. Baixe os arquivos `.cs3` das [Releases](https://github.com/franciscoalro/TestPlugins/releases)
2. Instale manualmente no CloudStream

## 🛠️ Desenvolvimento

### Pré-requisitos
- Java 17+
- Android SDK
- Git

### Build Local
```bash
# Clone o repositório
git clone https://github.com/franciscoalro/TestPlugins.git
cd TestPlugins

# Build todos os plugins
./gradlew build

# Build plugin específico
./gradlew MaxSeries:make
./gradlew AnimesOnlineCC:make
./gradlew PobreFlix:make
./gradlew OverFlix:make
./gradlew Vizer:make
./gradlew MegaFlix:make
./gradlew NetCine:make
```

### Estrutura do Projeto
```
TestPlugins/
├── MaxSeries/                 # Plugin MaxSeries
│   ├── src/main/kotlin/      # Código fonte
│   └── build.gradle.kts      # Configuração do build
├── AnimesOnlineCC/           # Plugin AnimesOnlineCC
│   ├── src/main/kotlin/      # Código fonte
│   └── build.gradle.kts      # Configuração do build
├── PobreFlix/                # Plugin PobreFlix (saimuelrepo-main)
│   ├── src/main/kotlin/      # Código fonte
│   └── build.gradle.kts      # Configuração do build
├── OverFlix/                 # Plugin OverFlix (saimuelrepo-main)
│   ├── src/main/kotlin/      # Código fonte
│   └── build.gradle.kts      # Configuração do build
├── Vizer/                    # Plugin Vizer (saimuelrepo-main)
│   ├── src/main/kotlin/      # Código fonte
│   └── build.gradle.kts      # Configuração do build
├── MegaFlix/                 # Plugin MegaFlix (saimuelrepo-main)
│   ├── src/main/kotlin/      # Código fonte
│   └── build.gradle.kts      # Configuração do build
├── NetCine/                  # Plugin NetCine (saimuelrepo-main)
│   ├── src/main/kotlin/      # Código fonte
│   └── build.gradle.kts      # Configuração do build
├── .github/workflows/        # GitHub Actions
├── plugins.json              # Metadados dos plugins
└── README.md                 # Este arquivo
```

## 🔄 CI/CD Pipeline

### Workflow Automático
1. **Build**: Compila plugins automaticamente no push
2. **Test**: Verifica compatibilidade e sintaxe
3. **Deploy**: Atualiza CloudstreamRepo automaticamente
4. **Release**: Cria releases com artifacts

### Scripts Utilitários
- `auto-update-repo.ps1` - Atualização automática do CloudstreamRepo
- `update-cloudstream-repo.bat` - Script manual para Windows

## 📋 Changelog

### v8 (2025-01-08)
- ✅ **MaxSeries**: Corrigida compatibilidade com CloudStream v9.0
- ✅ **Fix**: Migração de `ExtractorLink` para `newExtractorLink`
- ✅ **Build**: Pipeline de CI/CD automatizado

### v7 (Anterior)
- ❌ **MaxSeries**: Incompatível com CloudStream v9.0
- ✅ **AnimesOnlineCC**: Funcionando normalmente

## 🐛 Problemas Conhecidos

### Resolvidos ✅
- ~~Erro de compilação: "No parameter with name 'referer' found"~~
- ~~Incompatibilidade com CloudStream v9.0~~

### Em Monitoramento 🔍
- Performance de extração de links
- Compatibilidade com diferentes hosts de vídeo

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## 📞 Suporte

- **Issues**: [GitHub Issues](https://github.com/franciscoalro/TestPlugins/issues)
- **Discussões**: [GitHub Discussions](https://github.com/franciscoalro/TestPlugins/discussions)
- **CloudStream**: [Documentação Oficial](https://recloudstream.github.io/cloudstream/)

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 🔗 Links Úteis

- **CloudstreamRepo**: https://github.com/franciscoalro/CloudstreamRepo
- **Plugin JSON**: https://raw.githubusercontent.com/franciscoalro/CloudstreamRepo/main/plugins.json
- **CloudStream App**: https://github.com/recloudstream/cloudstream
- **Documentação**: https://recloudstream.github.io/cloudstream/

---

**Mantido por**: [@franciscoalro](https://github.com/franciscoalro)  
**Última atualização**: Janeiro 2025
