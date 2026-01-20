# 🚀 MaxSeries v133 - Quick Start

**Versão Atual:** v133.0  
**Data:** 20 de Janeiro de 2026  
**Status:** ✅ Produção

---

## 📦 INSTALAÇÃO

### Método 1: CloudStream (Recomendado)

```
1. Abrir CloudStream
2. Settings → Extensions
3. Atualizar MaxSeries para v133
```

### Método 2: Download Direto

```
1. Download: https://github.com/franciscoalro/TestPlugins/releases/download/v133.0/MaxSeries.cs3
2. Instalar no CloudStream
```

---

## ✨ FUNCIONALIDADES

### v133 (Atual)
- ✅ 12 CDNs conhecidos
- ✅ 4 variações de arquivo
- ✅ Extração automática de dados (regex template)
- ✅ Player interno e externo funcionais
- ✅ ~95% taxa de sucesso
- ✅ Sistema auto-adaptável

---

## 🎯 USO

### Buscar Série
```
1. Abrir CloudStream
2. Buscar: "Nome da Série"
3. Selecionar resultado
```

### Reproduzir Episódio
```
1. Escolher episódio
2. Clicar em Play
3. Vídeo inicia em ~2-3s
```

---

## 📊 ESPECIFICAÇÕES TÉCNICAS

### CDNs Suportados (12)
1. valenium.shop
2. veritasholdings.cyou
3. marvellaholdings.sbs
4. travianastudios.space
5. rivonaengineering.sbs
6. alphastrahealth.store
7. wanderpeakevents.store
8. stellarifyventures.sbs
9. lyonic.cyou
10. mindspireleadership.space
11. evercresthospitality.space
12. (+ descoberta automática)

### Variações de Arquivo (4)
1. index.txt (~40%)
2. index-f1-v1-a1.txt (~30%)
3. cf-master.txt (~20%)
4. cf-master.{timestamp}.txt (~10%)

### Performance
- Taxa de sucesso: ~95%
- Velocidade: ~3s (primeira vez) / ~1s (cache)
- Tentativas: 48 (12 CDNs × 4 variações)

---

## 🔧 TROUBLESHOOTING

### Vídeo Não Reproduz

**Verificar:**
```bash
adb logcat | grep "MegaEmbedV7"
```

**Logs esperados:**
```
D/MegaEmbedV7: ✅ Padrão funcionou: ...
```

**Se falhar:**
```
D/MegaEmbedV7: ⚠️ Padrões falharam, usando WebView...
D/MegaEmbedV7: ✅ WebView descobriu: ...
```

---

## 📝 CHANGELOG

### v133 (20 Jan 2026)
- ✅ Regex template URL
- ✅ Extração automática de dados
- ✅ Detecção de novos CDNs

### v132 (20 Jan 2026)
- ✅ 6 novos CDNs
- ✅ 4ª variação: index-f1-v1-a1.txt

### v131 (20 Jan 2026)
- ✅ HOTFIX: Player interno funcional

### v130 (19 Jan 2026)
- ✅ Timestamp dinâmico
- ✅ 3 variações de arquivo

---

## 🔗 LINKS

- **Releases:** https://github.com/franciscoalro/TestPlugins/releases
- **Repositório:** https://github.com/franciscoalro/TestPlugins
- **Documentação:** [STATUS_FINAL_V128_V133.md](STATUS_FINAL_V128_V133.md)

---

**Desenvolvido por:** franciscoalro  
**Versão:** v133.0  
**Status:** ✅ Produção
