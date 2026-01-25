# 🤝 Contribuindo para BRCloudstream

Obrigado por considerar contribuir para o BRCloudstream! Este documento fornece diretrizes para contribuições.

---

## 📋 Código de Conduta

Este projeto segue um código de conduta. Ao participar, você concorda em manter um ambiente respeitoso e inclusivo.

---

## 🚀 Como Contribuir

### 1. Reportar Bugs

Se encontrou um bug:

1. Verifique se já não existe uma [issue](https://github.com/franciscoalro/brcloudstream/issues) sobre o problema
2. Se não existir, [crie uma nova issue](https://github.com/franciscoalro/brcloudstream/issues/new)
3. Inclua:
   - Descrição clara do problema
   - Passos para reproduzir
   - Comportamento esperado vs atual
   - Screenshots (se aplicável)
   - Versão do Cloudstream
   - Provider afetado

### 2. Sugerir Melhorias

Para sugerir novas funcionalidades:

1. [Abra uma issue](https://github.com/franciscoalro/brcloudstream/issues/new) com o label "enhancement"
2. Descreva:
   - O que você gostaria de ver
   - Por que seria útil
   - Como deveria funcionar

### 3. Contribuir com Código

#### Setup do Ambiente

```bash
# Clone o repositório
git clone https://github.com/franciscoalro/brcloudstream.git
cd brcloudstream

# Instale dependências
./gradlew build

# Teste um provider
./gradlew MaxSeries:make
```

#### Processo de Contribuição

1. **Fork** o repositório
2. **Clone** seu fork
   ```bash
   git clone https://github.com/SEU-USUARIO/brcloudstream.git
   ```
3. **Crie uma branch** para sua feature
   ```bash
   git checkout -b feature/minha-feature
   ```
4. **Faça suas alterações**
5. **Teste** suas mudanças
   ```bash
   ./gradlew [Provider]:make
   ```
6. **Commit** suas mudanças
   ```bash
   git commit -m "feat: adiciona nova funcionalidade"
   ```
7. **Push** para seu fork
   ```bash
   git push origin feature/minha-feature
   ```
8. **Abra um Pull Request**

---

## 📝 Padrões de Código

### Commits

Usamos [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: adiciona novo extractor
fix: corrige bug no parser
docs: atualiza README
style: formata código
refactor: refatora função X
test: adiciona testes
chore: atualiza dependências
```

### Código Kotlin

```kotlin
// Use nomes descritivos
fun extractVideoUrl(html: String): String? {
    // Comentários quando necessário
    val pattern = Regex("video_url\":\"([^\"]+)")
    return pattern.find(html)?.groupValues?.get(1)
}

// Trate erros apropriadamente
try {
    val result = riskyOperation()
    Log.d(TAG, "✅ Sucesso: $result")
} catch (e: Exception) {
    Log.e(TAG, "❌ Erro: ${e.message}")
}
```

---

## 🧪 Testes

Antes de submeter um PR:

1. **Build** deve passar
   ```bash
   ./gradlew build
   ```

2. **Teste manual** no Cloudstream
   - Instale o provider
   - Teste busca
   - Teste reprodução de vídeo
   - Verifique logs

3. **Documente** mudanças no PR

---

## 📚 Documentação

Ao adicionar funcionalidades:

1. Atualize o README.md se necessário
2. Adicione comentários no código
3. Crie/atualize documentação técnica
4. Inclua exemplos de uso

---

## 🎯 Áreas para Contribuir

### Prioridade Alta
- 🐛 Correção de bugs
- 🎬 Novos extractors
- 📱 Melhorias de performance
- 🔒 Correções de segurança

### Prioridade Média
- ✨ Novas funcionalidades
- 📝 Melhorias na documentação
- 🧪 Testes automatizados
- 🎨 Melhorias de UI/UX

### Prioridade Baixa
- 🔧 Refatoração de código
- 📊 Otimizações
- 🌐 Traduções

---

## 🔍 Review Process

1. **Automated checks** devem passar
2. **Code review** por mantenedores
3. **Testes** devem ser incluídos
4. **Documentação** deve estar atualizada
5. **Aprovação** de pelo menos 1 mantenedor

---

## 📦 Adicionando Novo Provider

### Estrutura Básica

```kotlin
class MeuProvider : MainAPI() {
    override var mainUrl = "https://exemplo.com"
    override var name = "Meu Provider"
    override val hasMainPage = true
    override val hasQuickSearch = true
    override var lang = "pt-BR"
    override val supportedTypes = setOf(TvType.Movie, TvType.TvSeries)
    
    // Implementar métodos necessários
    override suspend fun getMainPage(page: Int, request: MainPageRequest): HomePageResponse {
        // ...
    }
    
    override suspend fun search(query: String): List<SearchResponse> {
        // ...
    }
    
    override suspend fun load(url: String): LoadResponse? {
        // ...
    }
    
    override suspend fun loadLinks(
        data: String,
        isCasting: Boolean,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        // ...
    }
}
```

### Checklist

- [ ] Provider compila sem erros
- [ ] Busca funciona
- [ ] Listagem de conteúdo funciona
- [ ] Reprodução de vídeo funciona
- [ ] Logs informativos adicionados
- [ ] Documentação incluída
- [ ] Testado no Cloudstream

---

## 🎓 Recursos Úteis

### Cloudstream
- [Documentação Oficial](https://recloudstream.github.io/csdocs/)
- [Exemplos de Providers](https://github.com/recloudstream/cloudstream-extensions)

### Kotlin
- [Kotlin Docs](https://kotlinlang.org/docs/home.html)
- [Kotlin Style Guide](https://kotlinlang.org/docs/coding-conventions.html)

### Gradle
- [Gradle Docs](https://docs.gradle.org/)

---

## 💬 Comunicação

- **Issues:** Para bugs e sugestões
- **Pull Requests:** Para contribuições de código
- **Discussions:** Para perguntas gerais

---

## 🏆 Reconhecimento

Contribuidores serão listados no README.md e nos release notes.

---

## ❓ Dúvidas?

Se tiver dúvidas sobre como contribuir:

1. Leia a documentação
2. Procure em issues existentes
3. Abra uma nova issue com sua dúvida

---

**Obrigado por contribuir! 🎉**

---

*Última atualização: 26 Janeiro 2026*
