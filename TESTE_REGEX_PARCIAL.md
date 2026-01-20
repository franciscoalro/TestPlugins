# 🧪 TESTE: Regex Detecta URLs Parciais?

## 🎯 SUA PERGUNTA

> "Se tiver alguma parte do regex ele detecta e isso?"

---

## 📊 REGEX ATUAL (v136)

```regex
https://s\w{2,4}\.\w+\.(store|sbs|cyou|space|cfd|shop)/v4/\w{1,3}/\w{6}/\S+\.(txt|woff2?)
```

---

## ❌ RESPOSTA: NÃO DETECTA PARCIAL

O regex atual é **COMPLETO** - precisa de **TODOS os componentes** para dar match.

### Teste 1: URL Completa
```kotlin
val regex = Regex("""https://s\w{2,4}\.\w+\.(store|sbs|cyou|space|cfd|shop)/v4/\w{1,3}/\w{6}/\S+\.(txt|woff2?)""")

// URL completa
regex.matches("https://spuc.alphastrahealth.store/v4/il/n3kh5r/index.txt")
// ✅ true
```

### Teste 2: URL Parcial (Falta arquivo)
```kotlin
// Falta o arquivo no final
regex.matches("https://spuc.alphastrahealth.store/v4/il/n3kh5r/")
// ❌ false (falta /arquivo.txt)
```

### Teste 3: URL Parcial (Falta video ID)
```kotlin
// Falta video ID
regex.matches("https://spuc.alphastrahealth.store/v4/il/")
// ❌ false (falta /n3kh5r/arquivo.txt)
```

### Teste 4: URL Parcial (Só domínio)
```kotlin
// Só domínio
regex.matches("https://spuc.alphastrahealth.store/")
// ❌ false (falta /v4/il/n3kh5r/arquivo.txt)
```

---

## 🔧 SOLUÇÃO: Regex com `find()` em vez de `matches()`

### Problema com `matches()`

```kotlin
// matches() exige URL COMPLETA
regex.matches("https://spuc.alphastrahealth.store/v4/il/n3kh5r/index.txt")
// ✅ true

regex.matches("parte da url: https://spuc.alphastrahealth.store/v4/il/n3kh5r/index.txt e mais texto")
// ❌ false (tem texto extra)
```

### Solução com `find()`

```kotlin
// find() procura o padrão DENTRO do texto
regex.find("parte da url: https://spuc.alphastrahealth.store/v4/il/n3kh5r/index.txt e mais texto")
// ✅ Match encontrado!

// Extrair a URL
val match = regex.find(texto)
val url = match?.value
// url = "https://spuc.alphastrahealth.store/v4/il/n3kh5r/index.txt"
```

---

## 🎯 COMO O WEBVIEW USA O REGEX

### Código Atual (v136)

```kotlin
val resolver = WebViewResolver(
    interceptUrl = Regex("""https://s\w{2,4}\.\w+\.(store|sbs|cyou|space|cfd|shop)/v4/\w{1,3}/\w{6}/\S+\.(txt|woff2?)"""),
    script = captureScript,
    timeout = 10_000L
)
```

### Como Funciona

```kotlin
// WebView intercepta TODAS as requisições HTTP
// Para cada requisição, testa:

val url = "https://spuc.alphastrahealth.store/v4/il/n3kh5r/index.txt"

if (regex.containsMatchIn(url)) {
    // ✅ Captura esta URL!
    return url
}
```

**`containsMatchIn()`** = Procura o padrão **DENTRO** da string (como `find()`)

---

## 🧪 TESTES PRÁTICOS

### Teste 1: URL Completa em Texto
```kotlin
val texto = """
    Carregando vídeo...
    URL: https://spuc.alphastrahealth.store/v4/il/n3kh5r/index.txt
    Aguarde...
"""

regex.containsMatchIn(texto)
// ✅ true (encontra a URL dentro do texto)

regex.find(texto)?.value
// "https://spuc.alphastrahealth.store/v4/il/n3kh5r/index.txt"
```

### Teste 2: Múltiplas URLs
```kotlin
val texto = """
    URL 1: https://spuc.alphastrahealth.store/v4/il/n3kh5r/index.txt
    URL 2: https://s6p9.fitnessessentials.cfd/v4/61/caojzl/index.txt
"""

regex.findAll(texto).map { it.value }.toList()
// [
//   "https://spuc.alphastrahealth.store/v4/il/n3kh5r/index.txt",
//   "https://s6p9.fitnessessentials.cfd/v4/61/caojzl/index.txt"
// ]
```

### Teste 3: URL Parcial (NÃO detecta)
```kotlin
val texto = "Domínio: https://spuc.alphastrahealth.store/v4/il/"

regex.containsMatchIn(texto)
// ❌ false (URL incompleta, falta /n3kh5r/arquivo.txt)
```

---

## ⚠️ PROBLEMA: URLs Parciais

### Cenário Problemático

Se o WebView capturar apenas parte da URL:

```kotlin
// WebView captura:
"https://spuc.alphastrahealth.store/v4/il/"

// Regex não detecta:
regex.containsMatchIn("https://spuc.alphastrahealth.store/v4/il/")
// ❌ false
```

**Isso é um problema?**
- ❌ NÃO! WebView sempre captura URL completa
- WebView intercepta requisições HTTP reais
- Requisições HTTP sempre têm URL completa

---

## 🎯 REGEX FLEXÍVEL (Se Necessário)

### Opção 1: Tornar Arquivo Opcional

```regex
https://s\w{2,4}\.\w+\.(store|sbs|cyou|space|cfd|shop)/v4/\w{1,3}/\w{6}(/\S+\.(txt|woff2?))?
```

**Mudança:** `(/\S+\.(txt|woff2?))?` = Arquivo é opcional

**Captura:**
```
✅ https://spuc.alphastrahealth.store/v4/il/n3kh5r/index.txt
✅ https://spuc.alphastrahealth.store/v4/il/n3kh5r/
```

---

### Opção 2: Tornar Tudo Opcional Após /v4/

```regex
https://s\w{2,4}\.\w+\.(store|sbs|cyou|space|cfd|shop)/v4/.*\.(txt|woff2?)
```

**Mudança:** `.*` = Qualquer coisa entre /v4/ e .txt

**Captura:**
```
✅ https://spuc.alphastrahealth.store/v4/il/n3kh5r/index.txt
✅ https://spuc.alphastrahealth.store/v4/qualquer/coisa/aqui/arquivo.txt
```

**Problema:** Muito permissivo, pode capturar URLs inválidas

---

### Opção 3: Regex Progressivo (Recomendado)

```kotlin
// Tenta do mais específico ao mais genérico
val regexes = listOf(
    // Regex completo (preferido)
    Regex("""https://s\w{2,4}\.\w+\.(store|sbs|cyou|space|cfd|shop)/v4/\w{1,3}/\w{6}/\S+\.(txt|woff2?)"""),
    
    // Regex sem arquivo (fallback)
    Regex("""https://s\w{2,4}\.\w+\.(store|sbs|cyou|space|cfd|shop)/v4/\w{1,3}/\w{6}/?"""),
    
    // Regex só domínio (último recurso)
    Regex("""https://s\w{2,4}\.\w+\.(store|sbs|cyou|space|cfd|shop)/v4/""")
)

// Testa cada regex
for (regex in regexes) {
    val match = regex.find(url)
    if (match != null) {
        return match.value
    }
}
```

---

## 🎯 RECOMENDAÇÃO

### Para WebView (Atual v136)

**Manter regex completo:**
```regex
https://s\w{2,4}\.\w+\.(store|sbs|cyou|space|cfd|shop)/v4/\w{1,3}/\w{6}/\S+\.(txt|woff2?)
```

**Por quê?**
- ✅ WebView sempre captura URL completa
- ✅ Mais preciso (evita falsos positivos)
- ✅ Mais rápido (menos backtracking)
- ✅ Não precisa de flexibilidade

---

### Se Precisar de Flexibilidade

**Usar regex com arquivo opcional:**
```regex
https://s\w{2,4}\.\w+\.(store|sbs|cyou|space|cfd|shop)/v4/\w{1,3}/\w{6}(/\S+\.(txt|woff2?))?
```

**Quando usar:**
- Se WebView capturar URLs parciais
- Se precisar detectar diretórios
- Se precisar de mais flexibilidade

---

## 🧪 TESTE FINAL

### Código de Teste

```kotlin
fun testRegex() {
    val regex = Regex("""https://s\w{2,4}\.\w+\.(store|sbs|cyou|space|cfd|shop)/v4/\w{1,3}/\w{6}/\S+\.(txt|woff2?)""")
    
    // URLs completas
    println(regex.containsMatchIn("https://spuc.alphastrahealth.store/v4/il/n3kh5r/index.txt"))
    // ✅ true
    
    println(regex.containsMatchIn("https://s6p9.fitnessessentials.cfd/v4/61/caojzl/index.txt"))
    // ✅ true
    
    // URLs parciais
    println(regex.containsMatchIn("https://spuc.alphastrahealth.store/v4/il/n3kh5r/"))
    // ❌ false
    
    println(regex.containsMatchIn("https://spuc.alphastrahealth.store/v4/il/"))
    // ❌ false
    
    println(regex.containsMatchIn("https://spuc.alphastrahealth.store/"))
    // ❌ false
    
    // URL em texto
    val texto = "Carregando: https://spuc.alphastrahealth.store/v4/il/n3kh5r/index.txt aguarde"
    println(regex.containsMatchIn(texto))
    // ✅ true
    
    println(regex.find(texto)?.value)
    // "https://spuc.alphastrahealth.store/v4/il/n3kh5r/index.txt"
}
```

---

## 🎯 CONCLUSÃO

```
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║         ❌ REGEX NÃO DETECTA PARCIAL ❌                        ║
║                                                                ║
║  Pergunta:                                                    ║
║  "Se tiver alguma parte do regex ele detecta?"               ║
║                                                                ║
║  Resposta:                                                    ║
║  ❌ NÃO - Regex exige URL COMPLETA                            ║
║  ✅ Mas WebView sempre captura URL completa                   ║
║  ✅ Então não é problema                                      ║
║                                                                ║
║  Como Funciona:                                               ║
║  🔍 WebView intercepta requisições HTTP                       ║
║  🔍 Requisições HTTP têm URL completa                         ║
║  🔍 Regex testa URL completa                                  ║
║  ✅ Match = Captura URL                                       ║
║                                                                ║
║  Se Precisar de Flexibilidade:                                ║
║  🔧 Tornar arquivo opcional: (/\S+\.(txt|woff2?))?            ║
║  🔧 Usar regex progressivo (específico → genérico)            ║
║                                                                ║
║  Recomendação:                                                ║
║  ✅ Manter regex completo (v136)                              ║
║  ✅ WebView sempre captura URL completa                       ║
║  ✅ Mais preciso e rápido                                     ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
```

---

**Resumo:** O regex **NÃO detecta URLs parciais**, mas isso **não é problema** porque o WebView sempre captura URLs completas das requisições HTTP.

---

**Versão:** v136  
**Data:** 20 de Janeiro de 2026  
**Status:** ✅ TESTE COMPLETO
