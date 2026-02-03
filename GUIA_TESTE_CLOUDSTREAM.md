# 📱 GUIA DE TESTE - CLOUDSTREAM 4.6.0

**Data:** 2026-02-01 21:59  
**Status:** Pronto para teste

---

## 🎯 TESTE RÁPIDO

### Passo 1: Limpar Cache (Recomendado)

No Cloudstream:
1. Settings → Extensions
2. Se houver repositório antigo, **remover**
3. Settings → Clear Cache (se disponível)

### Passo 2: Adicionar Repositório

**URL:**
```
https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/builds/repo.json
```

1. Settings → Extensions
2. Clicar em "+" ou "Add Repository"
3. Colar a URL acima
4. Confirmar

### Passo 3: Baixar Plugin

1. Procurar "MaxSeries" na lista
2. Clicar em "Download" ou "Install"
3. **Aguardar download completar**

### ✅ Resultado Esperado

- ✅ Download completa sem erro 404
- ✅ Plugin aparece como instalado
- ✅ Versão mostrada: v256

### ❌ Se Ainda Falhar

**Possíveis causas:**

1. **Cache do Cloudstream**
   - Fechar app completamente
   - Limpar cache do Android
   - Reabrir e tentar novamente

2. **Cache do GitHub**
   - Aguardar 1-2 minutos
   - GitHub pode estar servindo cache antigo

3. **Problema de rede**
   - Verificar conexão
   - Tentar com WiFi diferente

---

## 🔍 VERIFICAÇÃO MANUAL

### Testar URL Diretamente

No navegador do celular, abrir:
```
https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/builds/MaxSeries.cs3
```

**Resultado esperado:**
- ✅ Download do arquivo inicia (653 KB)
- ❌ Se mostrar erro 404 → GitHub ainda em cache

---

## 📊 INFORMAÇÕES ÚTEIS

### Plugins Disponíveis (11 total)

1. MaxSeries v256 (653 KB)
2. AnimesOnlineCC v2 (27 KB)
3. Doramas v1 (27 KB)
4. NovelasFlix v1 (30 KB)
5. DonghuaNoSekai v1 (33 KB)
6. EmbedCanais v1 (20 KB)
7. MegaFlix v1 (21 KB)
8. NetCine v1 (28 KB)
9. OverFlix v1 (39 KB)
10. PobreFlix v1 (34 KB)
11. Vizer v1 (41 KB)

### Repositório Verificado

- ✅ Todos os 11 plugins no GitHub
- ✅ Todas as URLs retornam 200 OK
- ✅ Tamanhos de arquivo corretos

---

## 🚨 TROUBLESHOOTING

### Erro: "Failed to download"

**Solução:**
1. Verificar conexão internet
2. Limpar cache do Cloudstream
3. Remover e adicionar repositório novamente

### Erro: "Invalid repository"

**Solução:**
1. Verificar URL (copiar exatamente)
2. Verificar se tem espaços extras
3. Tentar adicionar manualmente

### Plugin baixa mas não instala

**Solução:**
1. Verificar permissões do app
2. Verificar espaço disponível
3. Reinstalar Cloudstream

---

## 📝 REPORTE DE TESTE

Após testar, informe:

1. ✅ Download completou?
2. ✅ Plugin instalou?
3. ✅ Plugin funciona?
4. ❌ Algum erro? (screenshot se possível)

---

**Boa sorte com o teste!** 🚀
