# MaxSeries v145 - Multi-Regex: 8 Padrões de CDN

## 🎯 Estratégia: Múltiplos Regex

### Problema v144
- Regex único não estava capturando links
- Subdomínios dinâmicos não eram detectados

### Solução v145
**8 regex diferentes baseados em CDNs descobertos:**

1. **Valenium (is9)**: `https?://[a-z0-9]+\.valenium\.shop/v4/is9/[a-z0-9]{6}/...`
2. **Veritasholdings (ic)**: `https?://[a-z0-9]+\.veritasholdings\.cyou/v4/ic/[a-z0-9]{6}/...`
3. **Marvellaholdings (x6b)**: `https?://[a-z0-9]+\.marvellaholdings\.sbs/v4/x6b/[a-z0-9]{6}/...`
4. **Travianastudios (5c)**: `https?://[a-z0-9]+\.travianastudios\.space/v4/5c/[a-z0-9]{6}/...`
5. **Genérico /v4/ com cluster**: `https?://[a-z0-9]+\.[a-z]+\.[a-z]{2,}/v4/[a-z0-9]{2,3}/[a-z0-9]{6}/...`
6. **Fallback /v4/**: `https?://[^/]+/v4/[^"'<>\s]+`
7. **index.txt ou cf-master.txt**: `https?://[^/]+/.*/(index|cf-master)\.txt`
8. **Arquivos .woff/.woff2**: `https?://[^/]+/v4/.*/.*\.woff2?`

## 📋 Lógica de Funcionamento

```kotlin
// Tenta cada regex em sequência
for (regex in CDN_PATTERNS) {
    try {
        val resolver = WebViewResolver(interceptUrl = regex, ...)
        val captured = app.get(url, interceptor = resolver).url
        
        if (captured válido) {
            return // Sucesso!
        }
    } catch {
        continue // Próximo regex
    }
}
```

## 🔍 CDNs Conhecidos

```
valenium.shop          → is9  (soq6, soq7, soq8, srcf)
veritasholdings.cyou   → ic   (srcf)
marvellaholdings.sbs   → x6b  (stzm)
travianastudios.space  → 5c   (se9d)
```

## 🔄 Normalização de URL

```kotlin
// Converte diferentes formatos para index.txt
.woff/.woff2  → /index.txt
/v4/xxx/yyy   → /v4/xxx/yyy/index.txt
cf-master.txt → mantém
index.txt     → mantém
```

## 📊 Vantagens

✅ **Cobertura completa**: 8 padrões diferentes  
✅ **Específico primeiro**: Tenta CDNs conhecidos antes  
✅ **Fallback genérico**: Regex amplo se específicos falharem  
✅ **Logs detalhados**: Mostra qual regex funcionou  
✅ **Cache inteligente**: Salva URL que funcionou  

## 🧪 Como Testar

```bash
adb logcat | findstr "MegaEmbedV7"
```

**Procurar por:**
```
🔍 Tentando regex 1/8
🔍 Tentando regex 2/8
...
✅ SUCESSO com regex X: https://...
```

## 📦 Instalação

```
https://github.com/franciscoalro/TestPlugins/releases/download/v145/MaxSeries.cs3
```

---
**Data**: 2026-01-20  
**Build**: SUCCESSFUL  
**Tamanho**: ~170KB
