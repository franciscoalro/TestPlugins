# 🚀 Quick Reference - Testes MaxSeries v216

## ⚡ Comandos Rápidos

```powershell
# Rodar todos os testes
.\test-extractors-v216.ps1

# Gerar relatório
.\generate-test-report.ps1

# Gradle direto
.\gradlew.bat MaxSeries:test

# Com logs
.\gradlew.bat MaxSeries:test --info

# Teste específico
.\gradlew.bat MaxSeries:test --tests "ExtractorTests"
```

---

## 📊 Estrutura

```
27 testes totais
├── ExtractorTests (15)      # Testa cada extractor
├── FallbackChainTests (4)   # Testa fallback
└── PerformanceTests (8)     # Benchmark
```

---

## 🎯 Extractors

| Nome | Taxa | Velocidade |
|------|------|------------|
| MyVidPlay | 85% | ⚡ 1-2s |
| MegaEmbed | 95% | ✅ 2-5s |
| PlayerEmbed | 98% | ⏱️ 3-60s |
| DoodStream | 80% | ✅ 2-4s |
| StreamTape | 75% | ✅ 2-4s |
| Mixdrop | 70% | ⚠️ 3-6s |
| Filemoon | 65% | ⚠️ 3-6s |

---

## 📁 Arquivos

```
MaxSeries/src/test/kotlin/...
├── ExtractorTests.kt
├── FallbackChainTests.kt
└── PerformanceTests.kt

Scripts:
├── test-extractors-v216.ps1
└── generate-test-report.ps1

CI/CD:
└── .github/workflows/test.yml

Docs:
├── TESTING_GUIDE_V216.md
├── TEST_SUITE_SUMMARY.md
└── TEST_QUICK_REFERENCE.md
```

---

## 🐛 Troubleshooting

| Problema | Solução |
|----------|---------|
| Testes falhando | Ajustar URLs em `ExtractorTests.kt` |
| Timeout | Aumentar `TIMEOUT_MS` |
| PlayerEmbed falha | Esperado (precisa click manual) |
| Gradle erro | Usar `.\gradlew.bat` no Windows |

---

## ✅ Checklist

- [ ] Rodar `.\test-extractors-v216.ps1`
- [ ] Ajustar URLs de teste se necessário
- [ ] Gerar relatório com `.\generate-test-report.ps1`
- [ ] Verificar CI/CD no GitHub Actions
- [ ] Ler `TESTING_GUIDE_V216.md` para detalhes

---

**Skills:** testing-patterns + systematic-debugging + performance-profiling
