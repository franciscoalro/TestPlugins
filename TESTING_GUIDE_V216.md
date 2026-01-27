# 🧪 Guia de Testes - MaxSeries v216

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Estrutura dos Testes](#estrutura-dos-testes)
3. [Como Rodar](#como-rodar)
4. [Tipos de Testes](#tipos-de-testes)
5. [Interpretando Resultados](#interpretando-resultados)
6. [CI/CD](#cicd)
7. [Troubleshooting](#troubleshooting)

---

## 🎯 Visão Geral

Suite de testes automatizados para validar os **7 extractors** do MaxSeries v216.

### Skills Aplicados
- ✅ **testing-patterns** - Estrutura AAA, pirâmide de testes
- ✅ **systematic-debugging** - Debug estruturado, root cause analysis
- ✅ **performance-profiling** - Benchmark e otimização

### Cobertura
- **7 Extractors** testados individualmente
- **Fallback chain** validado
- **Performance** medida e otimizada
- **Cache** testado

---

## 📁 Estrutura dos Testes

```
MaxSeries/
├── src/
│   ├── main/kotlin/...
│   └── test/kotlin/com/franciscoalro/maxseries/
│       ├── ExtractorTests.kt          # Testes individuais
│       ├── FallbackChainTests.kt      # Testes de fallback
│       └── PerformanceTests.kt        # Benchmark
├── build/
│   ├── reports/tests/                 # Relatórios HTML
│   └── test-results/                  # Resultados XML
└── test-results/
    └── extractor-report-v216.md       # Relatório customizado
```

---

## 🚀 Como Rodar

### Método 1: Script PowerShell (Recomendado)

```powershell
# Rodar todos os testes
.\test-extractors-v216.ps1

# Escolher teste específico
# 1. ExtractorTests
# 2. FallbackChainTests
# 3. PerformanceTests
# 4. ALL
```

### Método 2: Gradle Direto

```bash
# Todos os testes
./gradlew MaxSeries:test

# Teste específico
./gradlew MaxSeries:test --tests "ExtractorTests"
./gradlew MaxSeries:test --tests "FallbackChainTests"
./gradlew MaxSeries:test --tests "PerformanceTests"

# Com logs detalhados
./gradlew MaxSeries:test --info
```

### Método 3: Gerar Relatório

```powershell
# Gera relatório Markdown completo
.\generate-test-report.ps1
```

---

## 🧪 Tipos de Testes

### 1. ExtractorTests

**O que testa:**
- ✅ Cada extractor extrai URL válida
- ✅ Timeout respeitado (<5s)
- ✅ Tratamento de erros
- ✅ Cache funciona

**Exemplo:**
```kotlin
@Test
fun `MegaEmbed should extract video URL within 5 seconds`() {
    // Arrange
    val extractor = MegaEmbedExtractorV9()
    
    // Act
    val duration = measureTimeMillis {
        extractor.getUrl(url, referer, {}, callback)
    }
    
    // Assert
    assertTrue(duration < 5000L)
    assertTrue(links.isNotEmpty())
}
```

### 2. FallbackChainTests

**O que testa:**
- ✅ Ordem de priorização correta
- ✅ Fallback automático funciona
- ✅ Pelo menos 1 extractor sempre funciona
- ✅ Tratamento de falhas em cascata

**Exemplo:**
```kotlin
@Test
fun `Should try all extractors in priority order`() {
    val extractors = listOf(
        "MyVidPlay",      // #1 - Mais rápido
        "MegaEmbed",      // #2 - Mais confiável
        "PlayerEmbedAPI", // #3 - Manual
        // ...
    )
    // Valida ordem e fallback
}
```

### 3. PerformanceTests

**O que testa:**
- ⚡ Velocidade de cada extractor
- 📊 Benchmark comparativo
- 💾 Eficiência do cache (90% melhoria)
- ⏱️ Timeouts e retry logic

**Exemplo:**
```kotlin
@Test
fun `Cache should improve performance by 90 percent`() {
    // Primeira chamada: ~2s
    // Segunda chamada (cache): ~0.2s
    // Melhoria: 90%
}
```

---

## 📊 Interpretando Resultados

### Console Output

```
🧪 MaxSeries v216 - Test Suite
================================

▶️  Rodando TODOS os testes...

ExtractorTests > MegaEmbed should extract video URL ✅ PASSED (2.3s)
ExtractorTests > MyVidPlay should extract MP4 URL ✅ PASSED (1.1s)
FallbackChainTests > Should try all extractors ✅ PASSED (0.5s)
PerformanceTests > Cache should improve performance ✅ PASSED (0.3s)

================================
✅ TESTES PASSARAM!
⏱️  Tempo: 15.2s
```

### Relatório HTML

Abra: `MaxSeries/build/reports/tests/test/index.html`

**Contém:**
- 📊 Gráficos de sucesso/falha
- ⏱️ Tempo de execução
- 📝 Stack traces de erros
- 📈 Histórico de testes

### Relatório Markdown

Abra: `test-results/extractor-report-v216.md`

**Contém:**
- 📈 Taxa de sucesso geral
- 🎯 Status de cada extractor
- 📊 Benchmark de performance
- ✅ Conclusões e recomendações

---

## 🔄 CI/CD

### GitHub Actions

Os testes rodam automaticamente em:
- ✅ Push para `main` ou `builds`
- ✅ Pull Requests
- ✅ Manualmente via workflow_dispatch

**Ver resultados:**
1. Vá em **Actions** no GitHub
2. Clique no workflow **Run Tests**
3. Veja o summary com resultados

**Arquivo:** `.github/workflows/test.yml`

---

## 🐛 Troubleshooting

### Problema: Testes falhando

**Solução 1: URLs de teste inválidas**
```kotlin
// Edite ExtractorTests.kt
private const val TEST_MEGAEMBED_URL = "https://megaembed.cc/embed/REAL_ID"
```

**Solução 2: Timeout muito curto**
```kotlin
// Aumente o timeout
private const val TIMEOUT_MS = 10000L // 10s
```

### Problema: Gradle não encontrado

```powershell
# Windows
.\gradlew.bat MaxSeries:test

# Linux/Mac
./gradlew MaxSeries:test
```

### Problema: Testes lentos

**Causa:** Extractors reais fazem requests HTTP

**Solução:** Usar mocks (futuro)
```kotlin
// TODO: Implementar mocks para testes unitários
val mockExtractor = mockk<MegaEmbedExtractorV9>()
```

### Problema: PlayerEmbedAPI sempre falha

**Esperado!** PlayerEmbedAPI Manual precisa de click do usuário.

**Solução:** Pular esse teste ou usar timeout menor:
```kotlin
@Ignore("Requires manual click")
@Test
fun `PlayerEmbedAPI Manual should wait for user click`() {
    // ...
}
```

---

## 📈 Métricas de Sucesso

### Taxa de Sucesso Esperada

| Extractor | Taxa | Velocidade |
|-----------|------|------------|
| MyVidPlay | 85% | ⚡ 1-2s |
| MegaEmbed V9 | 95% | ✅ 2-5s |
| PlayerEmbedAPI | 98% | ⏱️ 3-60s |
| DoodStream | 80% | ✅ 2-4s |
| StreamTape | 75% | ✅ 2-4s |
| Mixdrop | 70% | ⚠️ 3-6s |
| Filemoon | 65% | ⚠️ 3-6s |

### Benchmark Alvo

- **Fastest:** MyVidPlay (<2s)
- **Most Reliable:** MegaEmbed (95%)
- **Best UX:** PlayerEmbedAPI Manual (98% após click)

---

## 🎯 Próximos Passos

### Curto Prazo
- [ ] Adicionar mocks para testes unitários
- [ ] Implementar testes E2E com ADB
- [ ] Criar testes de regressão automáticos

### Médio Prazo
- [ ] Integrar com Cloudstream real
- [ ] Monitoring de taxa de sucesso em produção
- [ ] Dashboard de métricas

### Longo Prazo
- [ ] Testes de carga (stress testing)
- [ ] Testes de segurança
- [ ] Testes de acessibilidade

---

## 📚 Referências

### Skills Aplicados
- [testing-patterns](.agent/skills/testing-patterns/SKILL.md)
- [systematic-debugging](.agent/skills/systematic-debugging/SKILL.md)
- [performance-profiling](.agent/skills/performance-profiling/SKILL.md)

### Documentação
- [README.md](README.md)
- [RESUMO_V216.md](RESUMO_V216.md)
- [release-notes-v216.md](release-notes-v216.md)

---

**Desenvolvido por:** franciscoalro  
**Data:** 26 de Janeiro de 2026  
**Versão:** 216  
**Skills:** testing-patterns + systematic-debugging + performance-profiling
