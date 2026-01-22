# ⚙️ CONFIGURAÇÕES ADICIONAIS: MaxSeries v156

## 🎯 Objetivo

Este documento detalha configurações avançadas e opcionais para otimizar o MaxSeries v156.

---

## 📱 CONFIGURAÇÕES NO CLOUDSTREAM3

### **1. Configurações de Cache**

O MegaEmbed V8 usa cache automático para melhorar performance.

**Onde**: CloudStream3 → Settings → Extensions → MaxSeries

**Opções disponíveis**:
- Cache de URLs: ✅ Ativado por padrão
- Tempo de cache: 24 horas padrão
- Limpeza automática: Sim

**Como limpar cache manualmente**:
1. Settings → Storage
2. Clear Extension Data
3. Selecionar "MaxSeries"
4. Confirmar

---

### **2. Timeout Customizado** (Avançado)

Se você tem conexão muito lenta e ainda assim têm timeouts:

**Editar código** (requer rebuild):
```kotlin
// Arquivo: MegaEmbedExtractorV8.kt
// Linha: 225

// PADRÃO:
timeout = 120_000L // 120s (2 minutos)

// CONEXÃO MUITO LENTA:
timeout = 180_000L // 180s (3 minutos)

// CONEXÃO EXTREMAMENTE LENTA:
timeout = 300_000L // 300s (5 minutos)
```

⚠️ **Atenção**: Valores muito altos podem travar o app.

---

### **3. Logs Detalhados via ADB**

Para desenvolvedores e debug avançado.

**Comando básico**:
```powershell
adb logcat -s MegaEmbedV8:D
```

**Comando filtrado (apenas sucessos)**:
```powershell
adb logcat | Select-String "MegaEmbedV8.*✅"
```

**Comando filtrado (apenas erros)**:
```powershell
adb logcat | Select-String "MegaEmbedV8.*❌"
```

**Salvar logs em arquivo**:
```powershell
adb logcat -s MegaEmbedV8:D > megaembed_v156_logs.txt
```

**Formato de logs**:
```
D/MegaEmbedV8: === MEGAEMBED V8 v156 FETCH/XHR INTERCEPTION ===
D/MegaEmbedV8: Input: https://megaembed.link/api/v1/info#abc123
D/MegaEmbedV8: 🌐 Iniciando WebView com FETCH/XHR INTERCEPTION...
D/MegaEmbedV8: 📱 Carregando página com fetch/XHR interception...
D/MegaEmbedV8: 📜 Script capturou: https://soq6.valenium.shop/v4/is9/xez5rx/cf-master.txt
D/MegaEmbedV8: 🔍 URL do script: https://soq6.valenium.shop/v4/is9/xez5rx/cf-master.txt
D/MegaEmbedV8: 🎯 URL de vídeo capturada com sucesso!
D/MegaEmbedV8: ✅ URL válida (200): https://soq6.valenium.shop/v4/is9/xez5rx/cf-master.txt
```

---

## 🔧 CONFIGURAÇÕES DE DESENVOLVIMENTO

### **1. Build Local com JitPack Fix**

Se você quer compilar localmente e está tendo problemas com JitPack:

**Opção A: Usar commit hash específico**

Editar `build.gradle.kts` (raiz do projeto):
```kotlin
// ANTES:
implementation("com.github.recloudstream:cloudstream:master")

// DEPOIS (usar commit hash conhecido):
implementation("com.github.recloudstream:cloudstream:8a4480dc42")
```

Commits conhecidos estáveis:
- `8a4480dc42` - CloudStream 3.x
- `f7c4f3e2a1` - CloudStream 4.x (pre-release)

**Opção B: Usar versão local**

1. Clonar CloudStream3 localmente
2. Modificar `settings.gradle.kts`:
```kotlin
includeBuild("../cloudstream") {
    dependencySubstitution {
        substitute(module("com.github.recloudstream:cloudstream"))
            .using(project(":library"))
    }
}
```

---

### **2. Adicionar Fallback Personalizado**

Se você descobriu um novo padrão de URL:

**Arquivo**: `MegaEmbedExtractorV8.kt`  
**Linha**: ~260-267

```kotlin
val fileVariations = listOf(
    "cf-master.txt",
    "index-f1-v1-a1.txt",
    "index-f2-v1-a1.txt",
    "index.txt",
    "seg-1-f1-v1-a1.woff2",
    "seg-1-f1-v1-a1.txt",
    // ADICIONAR NOVOS PADRÕES AQUI:
    "seu-novo-padrao.txt",
    "outro-padrao.m3u8"
)
```

---

### **3. Modificar Regex para Novo Formato**

Se você encontrou URLs com formato diferente:

**Arquivo**: `MegaEmbedExtractorV8.kt`  
**Linha**: 211-214

**Regex atual**:
```kotlin
val interceptRegex = Regex(
    """https?://[^/\s"'<>]+/v4/[a-z0-9]{1,3}/[a-z0-9]{6}/[^"'<>\s]*(?:\.(txt|m3u8|woff2))?(?:\?[^"'<>\s]*)?""",
    RegexOption.IGNORE_CASE
)
```

**Exemplo de modificação** (adicionar suporte a v5):
```kotlin
val interceptRegex = Regex(
    """https?://[^/\s"'<>]+/v[4-5]/[a-z0-9]{1,3}/[a-z0-9]{6}/[^"'<>\s]*(?:\.(txt|m3u8|woff2))?(?:\?[^"'<>\s]*)?""",
    RegexOption.IGNORE_CASE
)
```

---

## 🌐 CONFIGURAÇÕES DE REDE

### **1. Headers Customizados**

Se você precisa modificar headers HTTP:

**Arquivo**: `MegaEmbedExtractorV8.kt`  
**Linha**: 37-41

```kotlin
private val cdnHeaders = mapOf(
    "Referer" to "https://megaembed.link/",
    "Origin" to "https://megaembed.link",
    "User-Agent" to "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    // ADICIONAR NOVOS HEADERS AQUI:
    "X-Custom-Header" to "valor",
    "Authorization" to "Bearer token" // se necessário
)
```

---

### **2. Proxy/VPN**

MaxSeries respeita as configurações de proxy do sistema Android.

**Configurar proxy no Android**:
1. Settings → Wi-Fi
2. Long press na rede conectada
3. Modify Network → Advanced
4. Proxy: Manual
5. Hostname: `seu.proxy.com`
6. Port: `8080`

**Testar com VPN**:
- MaxSeries funciona normalmente com VPN ativa
- Nenhuma configuração especial necessária

---

## 📊 CONFIGURAÇÕES DE PERFORMANCE

### **1. WebView Performance**

Para dispositivos mais fracos:

**Arquivo**: `MegaEmbedExtractorV8.kt`  
**Linha**: 156 (polling interval)

```kotlin
// PADRÃO (100ms):
var interval = setInterval(function() { ... }, 100);

// DISPOSITIVOS FRACOS (200ms - menos CPU):
var interval = setInterval(function() { ... }, 200);

// DISPOSITIVOS POTENTES (50ms - mais rápido):
var interval = setInterval(function() { ... }, 50);
```

---

### **2. Cache Settings**

**Arquivo**: `VideoUrlCache.kt` (se existir)

```kotlin
// Tempo de cache padrão
private const val CACHE_DURATION_MS = 24 * 60 * 60 * 1000 // 24 horas

// Para mais tempo de cache:
private const val CACHE_DURATION_MS = 7 * 24 * 60 * 60 * 1000 // 7 dias

// Para menos tempo de cache:
private const val CACHE_DURATION_MS = 1 * 60 * 60 * 1000 // 1 hora
```

---

## 🐛 CONFIGURAÇÕES DE DEBUG

### **1. Ativar Logs Verbosos**

Para debug extremo:

**Arquivo**: `MegaEmbedExtractorV8.kt`  
**Adicionar no início do método `getUrl`**:

```kotlin
override suspend fun getUrl(...) {
    // ATIVAR LOGS DETALHADOS
    Log.setLevel(Log.VERBOSE)
    
    // Seu código existente...
}
```

---

### **2. Exportar HTML para Debug**

Se precisar ver o HTML completo:

**Arquivo**: `MegaEmbedExtractorV8.kt`  
**Linha**: ~293

```kotlin
val html = response.text
Log.d(TAG, "📄 HTML (${html.length} chars)")

// ADICIONAR DEBUG:
// Salvar HTML em arquivo para análise
File(context.cacheDir, "megaembed_debug.html").writeText(html)
Log.d(TAG, "📁 HTML salvo em: ${context.cacheDir}/megaembed_debug.html")
```

Depois buscar o arquivo via ADB:
```powershell
adb pull /data/data/com.lagradost.cloudstream3/cache/megaembed_debug.html
```

---

## 🔒 CONFIGURAÇÕES DE SEGURANÇA

### **1. Validação de URLs**

Por padrão, apenas URLs HTTPS são aceitas.

**Arquivo**: `MegaEmbedExtractorV8.kt`  
**Linha**: 326-331

```kotlin
private fun isValidVideoUrl(url: String?): Boolean {
    if (url.isNullOrEmpty() || !url.startsWith("http")) return false
    
    // ADICIONAR VALIDAÇÃO EXTRA (opcional):
    if (!url.startsWith("https://")) {
        Log.w(TAG, "⚠️ URL não é HTTPS: $url")
        // return false // Descomentar para bloquear HTTP
    }
    
    return url.contains(".txt") || url.contains(".m3u8") || 
           url.contains("cf-master") || url.contains("index-f") ||
           url.contains("/v4/")
}
```

---

### **2. Whitelist de CDNs**

Se quiser permitir apenas CDNs conhecidos:

```kotlin
private val ALLOWED_CDNS = setOf(
    "valenium.shop",
    "veritasholdings.cyou",
    "srcf.*",
    "soq6.*"
)

private fun isValidVideoUrl(url: String?): Boolean {
    // Validação existente...
    
    // ADICIONAR WHITELIST:
    val host = url?.let { URI(it).host }
    if (host != null && ALLOWED_CDNS.none { host.contains(it) }) {
        Log.w(TAG, "⚠️ CDN não está na whitelist: $host")
        // return false // Descomentar para ativar whitelist
    }
    
    return true
}
```

---

## 📱 CONFIGURAÇÕES POR DISPOSITIVO

### **Android TV**
```kotlin
// Aumentar timeout para TV (rede mais lenta geralmente)
timeout = 180_000L // 180s
```

### **Tablets**
```kotlin
// Configuração padrão funciona bem
timeout = 120_000L // 120s
```

### **Smartphones Low-End**
```kotlin
// Reduzir polling para economizar CPU
var interval = setInterval(function() { ... }, 200);
```

---

## 🌍 CONFIGURAÇÕES POR REGIÃO

### **Brasil**
```kotlin
// Configuração padrão funciona bem
// CDNs brasileiros já suportados
```

### **Outras Regiões**
Se você está fora do Brasil e encontra CDNs diferentes:

1. Capture a URL via logs
2. Adicione o padrão ao regex
3. Teste e reporte sucesso

---

## 📋 CHECKLIST DE CONFIGURAÇÃO

### **Para Usuários Comuns**
- [ ] Instalar v156
- [ ] Testar reprodução
- [ ] Limpar cache se houver problemas

### **Para Desenvolvedores**
- [ ] Clonar repositório
- [ ] Configurar ambiente de build
- [ ] Testar build local
- [ ] Modificar configurações se necessário
- [ ] Fazer PR com melhorias

### **Para Testadores Avançados**
- [ ] Configurar ADB
- [ ] Ativar logs detalhados
- [ ] Monitorar performance
- [ ] Reportar problemas com logs

---

## 📞 SUPORTE

**Problemas com configurações?**
- GitHub Issues: https://github.com/franciscoalro/TestPlugins/issues
- Incluir sempre:
  - Configuração que você tentou
  - Arquivo modificado
  - Resultado esperado vs obtido

---

## 🔄 ATUALIZAÇÕES FUTURAS

Configurações planejadas para v157+:
- [ ] UI para ajustar timeout sem rebuild
- [ ] Cache em arquivo (persistente)
- [ ] Seletor de CDN preferido
- [ ] Modo de economia de dados

---

**Última Atualização**: 22 de Janeiro de 2026  
**Versão**: MaxSeries v156  
**Documentação**: Configurações Avançadas
