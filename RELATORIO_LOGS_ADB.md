# RELATÓRIO DE LOGS: CloudStream MaxSeries

## Data: 22/01/2026 20:21

## STATUS ATUAL

### Dispositivo Conectado:
```
Y9YP4XI7799P9LZT - device
```

### Versão Instalada no CloudStream:
```
❌ v129 (ANTIGA!)
```

**PROBLEMA IDENTIFICADO**: CloudStream está usando MaxSeries v129, NÃO v156!

---

## LOGS CAPTURADOS

```
01-22 20:21:50.769 MaxSeriesProvider: data-source encontrado: https://megaembed.link/#xez5rx
01-22 20:21:50.772 MaxSeriesProvider: Total sources extraídas (v73): 2
01-22 20:21:50.773 MaxSeriesProvider: Sources encontradas: 2
01-22 20:21:50.773 MaxSeriesProvider: Sources ordenadas por prioridade (v129 - Apenas MegaEmbed)
01-22 20:21:50.773 MaxSeriesProvider: Source não suportado (apenas MegaEmbed)
```

**Evidência**: Log mostra `"v129 - Apenas MegaEmbed"` 

---

## AÇÃO NECESSÁRIA

### CloudStream precisa atualizar para v156!

**Passos:**

1. Abrir CloudStream3
2. Settings → Extensions → Repositories
3. **Atualizar repositório** (pull down to refresh)
4. Procurar "MaxSeries"
5. Deve aparecer: **"v156 disponível para atualização"**
6. Clicar em **"Update"** ou **"Install"**
7. Aguardar download (182 KB)
8. Plugin será atualizado para v156

---

## VERIFICAR ATUALIZAÇÃO

Após atualizar, verificar versão:
```
Settings → Extensions → MaxSeries → Version: 156
```

Ou pelos logs (rode novamente):
```
# Deve aparecer:
MaxSeriesProvider: v156
# OU
MegaEmbedV8: === MEGAEMBED V8 v156 FETCH/XHR INTERCEPTION ===
```

---

## POR QUE v129 ESTÁ INSTALADA?

Possíveis razões:
1. ❌ CloudStream não atualizou repositório ainda
2. ❌ Cache do CloudStream não foi limpo
3. ❌ Plugin não foi desinstalado antes de instalar v156
4. ❌ JSONs ainda não foram detectados pelo app

---

## SOLUÇÃO RÁPIDA

### Opção 1: Forçar Atualização
```
1. Settings → Extensions
2. MaxSeries → Uninstall (desinstalar)
3. Repositories → Update Repository
4. MaxSeries → Install (instalar v156)
```

### Opção 2: Limpar Cache
```
1. Settings → Storage
2. Clear Extension Data
3. Repositories → Update Repository
4. MaxSeries → Update to v156
```

### Opção 3: Reinstalar CloudStream (extremo)
```
1. Backup configurações
2. Desinstalar CloudStream
3. Reinstalar
4. Adicionar repositório
5. Instalar MaxSeries v156
```

---

## URL DA RELEASE v156

```
https://github.com/franciscoalro/TestPlugins/releases/tag/v156
```

**Arquivo disponível:**
```
✅ https://github.com/franciscoalro/TestPlugins/releases/download/v156/MaxSeries.cs3
   (182 KB - Online)
```

---

## PRÓXIMOS PASSOS

1. ✅ Desinstalar v129
2. ✅ Atualizar repositório
3. ✅ Instalar v156
4. ✅ Testar vídeo
5. ✅ Verificar logs novamente

**Quando v156 estiver instalada, os logs mostrarão:**
```
MegaEmbedV8: === MEGAEMBED V8 v156 FETCH/XHR INTERCEPTION ===
MegaEmbedV8: Input: https://megaembed.link/api/v1/info#xez5rx
MegaEmbedV8: 🌐 Iniciando WebView com FETCH/XHR INTERCEPTION...
```

---

**Data**: 22/01/2026 20:22  
**Device**: Y9YP4XI7799P9LZT  
**Status**: v129 instalada (precisa atualizar para v156)
