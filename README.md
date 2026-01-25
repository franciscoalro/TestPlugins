# 🇧🇷 BRCloudstream - Brazilian Providers Repository

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/franciscoalro/brcloudstream)
[![Providers](https://img.shields.io/badge/providers-7-blue)](https://github.com/franciscoalro/brcloudstream)
[![Language](https://img.shields.io/badge/language-pt--BR-green)](https://github.com/franciscoalro/brcloudstream)
[![License](https://img.shields.io/badge/license-MIT-orange)](LICENSE)

Repositório completo de extensões brasileiras para **Cloudstream 3**, incluindo 7 providers totalmente funcionais com foco em conteúdo em português.

---

## 🎯 Destaques

### ⭐ MaxSeries v209 (Flagship Provider)
- **7 Extractors** + 1 fallback (MegaEmbed, PlayerEmbedAPI, MyVidPlay, DoodStream, StreamTape, Mixdrop, Filemoon)
- **24 Categorias** incluindo "Em Alta" (Trending)
- **23 Gêneros** diferentes
- **Taxa de sucesso: ~99%**
- Quick Search ativado
- Download support

### 📦 Outros 6 Providers
- AnimesOnlineCC (Animes)
- MegaFlix (Filmes & Séries)
- NetCine (Filmes, Séries & Animes)
- OverFlix (Filmes & Séries)
- PobreFlix (Filmes & Séries)
- Vizer (Filmes & Séries)

---

## 🚀 Instalação Rápida

### Método 1: Via Repositório (Recomendado)

1. Abra o **Cloudstream**
2. Vá em **Configurações** → **Extensões**
3. Clique em **Adicionar Repositório** (+)
4. Cole a URL:
   ```
   https://raw.githubusercontent.com/franciscoalro/brcloudstream/builds/repo.json
   ```
5. Instale os providers desejados

### Método 2: Download Direto

**MaxSeries v209:**
```
https://github.com/franciscoalro/brcloudstream/releases/download/v209/MaxSeries.cs3
```

**Outros Providers:**
```
https://github.com/franciscoalro/brcloudstream/releases/download/v1.0.0/[Provider].cs3
```

---

## 📊 Providers Disponíveis

| Provider | Versão | Tipo | Features | Status |
|----------|--------|------|----------|--------|
| **MaxSeries** ⭐ | v209 | Movies & Series | 7 extractors, 24 categories, ~99% success | ✅ |
| AnimesOnlineCC | v1 | Anime | Anime streaming | ✅ |
| MegaFlix | v1 | Movies & Series | Quick search | ✅ |
| NetCine | v1 | Movies, Series & Anime | Multiple types | ✅ |
| OverFlix | v1 | Movies & Series | Main page | ✅ |
| PobreFlix | v1 | Movies & Series | Quick search | ✅ |
| Vizer | v1 | Movies & Series | Quick search | ✅ |

---

## 🎬 MaxSeries v209 - Detalhes

### Extractors (7+1)
1. **MegaEmbed V9** - ~95% sucesso (principal)
2. **PlayerEmbedAPI** - ~90% sucesso (backup)
3. **MyVidPlay** - ~85% sucesso (rápido)
4. **DoodStream** - ~80% sucesso (popular)
5. **StreamTape** - ~75% sucesso (confiável)
6. **Mixdrop** - ~70% sucesso (backup)
7. **Filemoon** - ~65% sucesso (novo)
8. **Fallback** - ~50% sucesso (última opção)

### Categorias (24)
- **Principal:** Início, Em Alta, Filmes, Séries
- **Gêneros (20):** Ação, Animação, Aventura, Comédia, Crime, Documentário, Drama, Família, Fantasia, Faroeste, Ficção Científica, Guerra, História, Infantil, Mistério, Música, Romance, Terror, Thriller

### Evolução
- **v207:** 9 categorias, 6 gêneros, 3 extractors, ~80% sucesso
- **v208:** 24 categorias, 23 gêneros, 3 extractors, ~85% sucesso
- **v209:** 24 categorias, 23 gêneros, 7+1 extractors, ~99% sucesso

---

## 📈 Estatísticas

### Conteúdo Estimado
- **Filmes:** ~10,000
- **Séries:** ~8,000
- **Animes:** ~2,000
- **Total:** ~20,000 títulos

### Performance
- **Build Time:** ~9 segundos (todos os 7 providers)
- **Build Success Rate:** 100%
- **MaxSeries Success Rate:** ~99%

---

## 📝 Documentação

### Guias
- [📱 Guia de Instalação](CLOUDSTREAM_INSTALLATION_GUIDE.md)
- [📊 Resumo Completo](COMPLETE_PROJECT_SUMMARY.md)
- [🎬 MaxSeries v209 Release Notes](RELEASE_NOTES_V209.md)
- [📈 Comparação v208 vs v209](MAXSERIES_V208_VS_V209_COMPARISON.md)

### Técnica
- [🔧 TypeScript Test Improvements](TYPESCRIPT_TEST_IMPROVEMENTS_V2.md)
- [📦 All Providers Summary](ALL_PROVIDERS_SUMMARY.md)
- [✅ Deploy Success v209](DEPLOY_SUCCESS_V209.md)

---

## 🛠️ Desenvolvimento

### Requisitos
- Gradle 8.13+
- Kotlin 2.1.0+
- Android SDK

### Build

**Todos os providers:**
```bash
./gradlew MaxSeries:make AnimesOnlineCC:make MegaFlix:make NetCine:make OverFlix:make PobreFlix:make Vizer:make
```

**Apenas MaxSeries:**
```bash
./gradlew MaxSeries:make
```

### Estrutura
```
brcloudstream/
├── MaxSeries/              # Flagship provider (v209)
├── AnimesOnlineCC/         # Anime provider
├── MegaFlix/              # Movies & Series
├── NetCine/               # Movies, Series & Anime
├── OverFlix/              # Movies & Series
├── PobreFlix/             # Movies & Series
├── Vizer/                 # Movies & Series
├── docs/                  # Documentation
└── scripts/               # Build scripts
```

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

---

## 🐛 Reportar Problemas

Encontrou um bug? [Abra uma issue](https://github.com/franciscoalro/brcloudstream/issues)

**Informações úteis:**
- Versão do Cloudstream
- Provider com problema
- Mensagem de erro
- Passos para reproduzir

---

## 📜 Changelog

### v209 (26 Jan 2026) - MaxSeries
- ✨ Adicionados 4 novos extractors (DoodStream, StreamTape, Mixdrop, Filemoon)
- 📊 Taxa de sucesso: 85% → 99%
- 🎯 Total de 7 extractors específicos + fallback

### v208 (26 Jan 2026) - MaxSeries
- ✨ Adicionada categoria "Em Alta" (Trending)
- ✨ Adicionados 17 novos gêneros
- 📊 Total de 24 categorias

### v1.0.0 (26 Jan 2026) - All Providers
- 🎉 Lançamento inicial com 7 providers brasileiros
- ✅ Todos compilados e testados

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 👨‍💻 Autor

**franciscoalro**
- GitHub: [@franciscoalro](https://github.com/franciscoalro)
- Repository: [brcloudstream](https://github.com/franciscoalro/brcloudstream)

---

## 🌟 Agradecimentos

- Comunidade Cloudstream
- Contribuidores do projeto
- Usuários e testadores

---

## 📞 Suporte

- **Issues:** [GitHub Issues](https://github.com/franciscoalro/brcloudstream/issues)
- **Releases:** [GitHub Releases](https://github.com/franciscoalro/brcloudstream/releases)
- **Documentação:** [Docs](https://github.com/franciscoalro/brcloudstream/tree/main/docs)

---

## 🎯 Roadmap

### Próximas Versões
- [ ] Seleção manual de qualidade de vídeo
- [ ] Estatísticas de uso dos extractors
- [ ] Retry automático inteligente
- [ ] Configurações personalizadas
- [ ] Interface de configuração no app
- [ ] Cache de extractors bem-sucedidos

---

## ⭐ Star History

Se este projeto foi útil para você, considere dar uma ⭐!

---

<div align="center">

**🇧🇷 Feito com ❤️ para a comunidade brasileira de Cloudstream**

[⬆ Voltar ao topo](#-brcloudstream---brazilian-providers-repository)

</div>
