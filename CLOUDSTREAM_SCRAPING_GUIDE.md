# 📚 Guia Completo de Scraping para CloudStream

> Documentação oficial adaptada e complementada para desenvolvimento de providers CloudStream

---

## 📖 Índice

1. [Introdução ao Scraping](#1-introdução-ao-scraping)
2. [Fazendo Requisições HTTP](#2-fazendo-requisições-http)
3. [Seletores CSS](#3-seletores-css)
4. [Expressões Regulares (Regex)](#4-expressões-regulares-regex)
5. [Trabalhando com APIs e JSON](#5-trabalhando-com-apis-e-json)
6. [Bypass de Detecção de DevTools](#6-bypass-de-detecção-de-devtools)
7. [Disfarçando seu Scraper](#7-disfarçando-seu-scraper)
8. [Headers Personalizados](#8-headers-personalizados)
9. [Tratamento de Respostas](#9-tratamento-de-respostas)
10. [Boas Práticas para CloudStream](#10-boas-práticas-para-cloudstream)

---

## 1. Introdução ao Scraping

**Scraping** é o processo de baixar uma página web e extrair as informações desejadas dela. É a base para criar providers no CloudStream.

### Bibliotecas Recomendadas

| Linguagem | Biblioteca | Uso |
|-----------|------------|-----|
| Kotlin | [NiceHttp](https://github.com/Blatzar/NiceHttp) | Wrapper OkHttp para Android (recomendado) |
| Kotlin | OkHttp | Nível empresarial |
| Kotlin | khttp | Facilidade de uso |
| Python | requests | Simples e direto |
| Python | httpx | Mais recursos, melhor bypass |

---

## 2. Fazendo Requisições HTTP

### Python - Exemplo Básico

```python
import requests

url = "https://exemplo.com/pagina"
response = requests.get(url)
print(response.text)  # Imprime o HTML da página
```

### Kotlin - Exemplo Básico

**build.gradle:**
```gradle
repositories {
    mavenCentral()
    jcenter()
    maven { url 'https://jitpack.io' }
}

dependencies {
    compile group: 'khttp', name: 'khttp', version: '1.0.0'
}
```

**main.kt:**
```kotlin
fun main() {
    val url = "https://exemplo.com/pagina"
    val response = khttp.get(url)
    println(response.text)
}
```

### CloudStream - Usando app.get()

No CloudStream, usamos o objeto `app` para fazer requisições:

```kotlin
// GET simples
val document = app.get(url).document

// GET com headers
val response = app.get(
    url = "https://exemplo.com",
    headers = mapOf(
        "User-Agent" to "Mozilla/5.0...",
        "Referer" to "https://exemplo.com"
    )
).document

// POST com dados
val response = app.post(
    url = "https://exemplo.com/api",
    data = mapOf("key" to "value")
)
```

---

## 3. Seletores CSS

Seletores CSS são uma forma de navegar pelo HTML como um navegador e selecionar elementos específicos.

### Como Encontrar Seletores

1. Abra as **DevTools** do navegador (`Ctrl + Shift + I` ou `F12`)
2. Use o **seletor de elementos** (`Ctrl + Shift + C`)
3. Clique no elemento desejado
4. Analise a estrutura HTML

### Sintaxe de Seletores CSS

| Seletor | Descrição | Exemplo |
|---------|-----------|---------|
| `tag` | Seleciona por tag | `p`, `div`, `a` |
| `.classe` | Seleciona por classe | `.titulo`, `.item` |
| `#id` | Seleciona por ID | `#header`, `#main` |
| `tag.classe` | Tag com classe | `div.container` |
| `tag[attr]` | Tag com atributo | `a[href]` |
| `tag[attr="valor"]` | Atributo com valor | `img[src*="poster"]` |
| `pai > filho` | Filho direto | `ul > li` |
| `pai filho` | Descendente | `div p` |

### Testando Seletores no Console

```javascript
// No console do navegador
document.querySelectorAll("p.f4.mt-3");
// Retorna: NodeList [p.f4.mt-3]
```

### Python com BeautifulSoup

```python
import requests
from bs4 import BeautifulSoup

url = "https://exemplo.com"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'lxml')

# Seletor CSS
element = soup.select("p.f4.mt-3")
print(element[0].text.strip())

# Múltiplos elementos
items = soup.select("div.item")
for item in items:
    titulo = item.select_one("h3").text
    link = item.select_one("a")["href"]
    print(f"{titulo}: {link}")
```

### Kotlin com Jsoup

**build.gradle:**
```gradle
dependencies {
    implementation "org.jsoup:jsoup:1.11.3"
}
```

**Código:**
```kotlin
import org.jsoup.Jsoup

fun main() {
    val url = "https://exemplo.com"
    val response = khttp.get(url)
    val soup = Jsoup.parse(response.text)
    
    // Seletor CSS
    val element = soup.select("p.f4.mt-3")
    println(element.text().trim())
    
    // Múltiplos elementos
    val items = soup.select("div.item")
    items.forEach { item ->
        val titulo = item.selectFirst("h3")?.text()
        val link = item.selectFirst("a")?.attr("href")
        println("$titulo: $link")
    }
}
```

### CloudStream - Seletores Comuns

```kotlin
// Dentro de um provider CloudStream
override suspend fun getMainPage(page: Int, request: MainPageRequest): HomePageResponse {
    val document = app.get(request.data + page).document
    
    val items = document.select("div.item").mapNotNull { item ->
        val title = item.selectFirst("h3")?.text() ?: return@mapNotNull null
        val href = fixUrl(item.selectFirst("a")?.attr("href") ?: return@mapNotNull null)
        val poster = item.selectFirst("img")?.attr("src")
        
        newMovieSearchResponse(title, href, TvType.Movie) {
            this.posterUrl = poster
        }
    }
    
    return newHomePageResponse(request.name, items)
}
```

> ⚠️ **NOTA IMPORTANTE**: Você pode não obter os mesmos resultados ao fazer scraping via código. Classes e elementos às vezes são criados por JavaScript no site.

---

## 4. Expressões Regulares (Regex)

Regex é como um "Ctrl+F turbinado" - você pode buscar por qualquer padrão.

### Ferramenta Recomendada

Use [regex101.com](https://regex101.com) (flavor Python) para testar suas expressões.

### Tokens Importantes

| Token | Descrição |
|-------|-----------|
| `.*?` | Qualquer caractere, qualquer quantidade (não-guloso) |
| `.*` | Qualquer caractere, qualquer quantidade (guloso) |
| `\s*` | Espaços em branco, qualquer quantidade |
| `\d+` | Dígitos, um ou mais |
| `(...)` | Grupo de captura |
| `(?:...)` | Grupo sem captura |
| `[abc]` | Qualquer caractere dentro dos colchetes |
| `^` | Início da linha |
| `$` | Fim da linha |

### Exemplo Prático

**HTML:**
```html
<p class="f4 mt-3">Descrição do projeto</p>
```

**Regex:**
```regex
<p class="f4 mt-3">\s*(.*)?\s*<
```

**Explicação:**
- `<p class="f4 mt-3">` - texto exato
- `\s*` - espaços opcionais
- `(.*)?` - captura qualquer texto (grupo 1)
- `\s*` - espaços opcionais
- `<` - início da próxima tag

### Python

```python
import requests
import re

url = "https://exemplo.com"
response = requests.get(url)

# r"" = raw string (melhor para regex)
description_regex = r"<p class=\"f4 mt-3\">\s*(.*)?\s*<"
description = re.search(description_regex, response.text).groups()[0]
print(description)
```

### Kotlin

```kotlin
fun main() {
    val url = "https://exemplo.com"
    val response = khttp.get(url)
    
    // Triple quotes para strings com aspas
    val descriptionRegex = Regex("""<p class="f4 mt-3">\s*(.*)?\s*<""")
    val description = descriptionRegex.find(response.text)?.groups?.get(1)?.value
    println(description)
}
```

### CloudStream - Regex Comuns

```kotlin
// Extrair ID de vídeo
val videoId = Regex("""video/(\d+)""").find(url)?.groupValues?.get(1)

// Extrair URL de stream
val streamUrl = Regex("""file:\s*["']([^"']+)["']""").find(script)?.groupValues?.get(1)

// Extrair ano
val year = Regex("""\b(19|20)\d{2}\b""").find(text)?.value?.toIntOrNull()

// Extrair episódio e temporada
val (season, episode) = Regex("""S(\d+)E(\d+)""").find(title)?.destructured ?: return null
```

---

## 5. Trabalhando com APIs e JSON

Usar a API de um site é sempre melhor que fazer scraping do HTML. Às vezes é a única opção quando o conteúdo é carregado via JavaScript.

### Python - Parsing JSON

```python
import requests

url = "https://api.exemplo.com/dados"
json_data = requests.get(url).json()

# Acessar dados
nome = json_data["name"]
items = json_data["items"]
```

### Kotlin - Parsing JSON com Jackson

**build.gradle:**
```gradle
dependencies {
    implementation "com.fasterxml.jackson.module:jackson-module-kotlin:2.11.3"
}
```

**Definindo a estrutura (Data Class):**
```kotlin
import com.fasterxml.jackson.annotation.JsonProperty

data class Planet(
    @JsonProperty("name") val name: String,
    @JsonProperty("rotation_period") val rotationPeriod: String,
    @JsonProperty("orbital_period") val orbitalPeriod: String,
    @JsonProperty("diameter") val diameter: String,
    @JsonProperty("climate") val climate: String,
    @JsonProperty("gravity") val gravity: String,
    @JsonProperty("terrain") val terrain: String,
    @JsonProperty("surface_water") val surfaceWater: String,
    @JsonProperty("population") val population: String,
    @JsonProperty("residents") val residents: List<String>,
    @JsonProperty("films") val films: List<String>,
    @JsonProperty("created") val created: String,
    @JsonProperty("edited") val edited: String,
    @JsonProperty("url") val url: String
)
```

**Parsing:**
```kotlin
import com.fasterxml.jackson.databind.DeserializationFeature
import com.fasterxml.jackson.module.kotlin.KotlinModule
import com.fasterxml.jackson.databind.json.JsonMapper
import com.fasterxml.jackson.module.kotlin.readValue

val mapper: JsonMapper = JsonMapper.builder()
    .addModule(KotlinModule())
    .configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false)
    .build()

val jsonString = khttp.get("https://api.exemplo.com/dados").text
val planet = mapper.readValue<Planet>(jsonString)
println(planet.name)
```

### Tipos Nullable

Para JSON que pode ou não conter certas chaves:

```kotlin
data class Example(
    @JsonProperty("cat") val cat: String,      // Sempre presente
    @JsonProperty("dog") val dog: String?,     // Pode estar ausente
    @JsonProperty("fish") val fish: String?    // Pode estar ausente
)
```

### CloudStream - Parsing JSON

```kotlin
// Usando o parser interno do CloudStream
data class ApiResponse(
    @JsonProperty("data") val data: List<Item>
)

data class Item(
    @JsonProperty("title") val title: String,
    @JsonProperty("url") val url: String,
    @JsonProperty("poster") val poster: String?
)

// No provider
val response = app.get("https://api.exemplo.com/search?q=$query").text
val parsed = parseJson<ApiResponse>(response)

parsed.data.map { item ->
    newMovieSearchResponse(item.title, item.url, TvType.Movie) {
        this.posterUrl = item.poster
    }
}
```

### Ferramentas para Gerar Data Classes

- [json2kt](https://json2kt.com) - Gera código Kotlin
- [quicktype](https://quicktype.io) - Suporta múltiplas linguagens

---

## 6. Bypass de Detecção de DevTools

Muitos sites detectam quando as DevTools estão abertas para impedir scraping.

### Métodos de Detecção

| Método | Descrição | Bypass |
|--------|-----------|--------|
| `debugger` em loop | Pausa a execução infinitamente | Desabilitar debugger ou clicar com botão direito na linha e desabilitar |
| `console.log()` com `.toString()` customizado | Detecta quando console está aberto | Difícil de bypassar via JS |
| Loop `while(true)` | Congela a página | Requer modificação do navegador |

### Solução: Web Sniffer

A forma mais fácil de ver o tráfego de rede sem ser detectado é usar uma **extensão de Web Sniffer**.

### Firefox Modificado (Avançado)

Para casos extremos, existe uma versão modificada do Firefox com bypasses:

**about:config:**
- `devtools.console.bypass` - Desabilita o console (invalida método 2)
- `devtools.debugger.bypass` - Desabilita completamente o debugger (bypassa método 3)

---

## 7. Disfarçando seu Scraper

### Por que Sites Bloqueiam Scrapers?

1. **Bloqueio de anúncios** - Afeta receita do site
2. **Sobrecarga de servidores** - Muitas requisições
3. **Roubo de conteúdo** - Redistribuição não autorizada
4. **Exploits** - Scrapers podem encontrar vulnerabilidades

### Técnicas de Disfarce

1. **User-Agent realista** - Simule um navegador real
2. **Headers completos** - Inclua todos os headers que um navegador enviaria
3. **Cookies** - Mantenha sessão como um usuário normal
4. **Rate limiting** - Não faça muitas requisições por segundo
5. **Rotação de IP** - Use proxies se necessário

---

## 8. Headers Personalizados

### Headers Importantes

| Header | Propósito | Valor Recomendado |
|--------|-----------|-------------------|
| `User-Agent` | Identifica o cliente | User-Agent do seu navegador |
| `Referer` | Site de origem | URL da página anterior |
| `X-Requested-With` | Tipo de requisição (AJAX) | `XMLHttpRequest` |
| `Cookie` | Cookies de sessão | Cookies do navegador |
| `Authorization` | Tokens de autenticação | Token válido |
| `Accept` | Tipos de conteúdo aceitos | `text/html,application/json` |
| `Accept-Language` | Idioma preferido | `pt-BR,pt;q=0.9,en;q=0.8` |

### Exemplo Completo

```kotlin
val headers = mapOf(
    "User-Agent" to "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer" to "https://www.maxseries.one/",
    "Accept" to "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language" to "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding" to "gzip, deflate, br",
    "Connection" to "keep-alive",
    "Upgrade-Insecure-Requests" to "1"
)

val response = app.get(url, headers = headers).document
```

### Diferença entre Bibliotecas

```python
import requests, httpx

# requests pode falhar
requests.get("http://site.com/", headers={"User-Agent": "custom/1"})
# <Response [403]>

# httpx pode funcionar
httpx.get("http://site.com/", headers={"User-Agent": "custom/1"})
# <Response [200 OK]>
```

A diferença está nos mecanismos internos de cada biblioteca.

---

## 9. Tratamento de Respostas

### Classe de Sessão Customizada

Você pode criar uma sessão que automaticamente trata erros e bypasses:

```python
import httpx

class ScraperSession(httpx.Client):
    def request(self, *args, **kwargs):
        response = super().request(*args, **kwargs)
        
        # Verificar erros
        if response.status_code >= 400:
            # Tentar bypass de Cloudflare
            if self.has_cloudflare(response):
                cookie = self.bypass_cloudflare(response)
                self.cookies.update(cookie)
                return self.request(*args, **kwargs)
        
        # Verificar CAPTCHA
        if self.has_captcha(response):
            token = self.solve_captcha(response)
            setattr(response, 'captcha_token', token)
        
        return response
    
    def has_cloudflare(self, response):
        return "cloudflare" in response.text.lower()
    
    def bypass_cloudflare(self, response):
        # Implementar bypass
        pass
    
    def has_captcha(self, response):
        return "captcha" in response.text.lower()
    
    def solve_captcha(self, response):
        # Implementar solver
        pass
```

### Uso

```python
client = ScraperSession()
response = client.get("https://site-protegido.com")

# Se teve CAPTCHA, o token está disponível
if hasattr(response, 'captcha_token'):
    print(f"Token: {response.captcha_token}")
```

---

## 10. Boas Práticas para CloudStream

### Estrutura de um Provider

```kotlin
class MeuProvider : MainAPI() {
    override var mainUrl = "https://meusite.com"
    override var name = "MeuProvider"
    override val hasMainPage = true
    override var lang = "pt"
    override val hasDownloadSupport = true
    override val supportedTypes = setOf(TvType.Movie, TvType.TvSeries)

    override val mainPage = mainPageOf(
        "$mainUrl/filmes" to "Filmes",
        "$mainUrl/series" to "Séries"
    )

    // Implementar métodos...
}
```

### Checklist de Desenvolvimento

- [ ] Analisar estrutura HTML real do site
- [ ] Identificar seletores CSS corretos
- [ ] Testar seletores no console do navegador
- [ ] Verificar se conteúdo é carregado via JavaScript
- [ ] Implementar headers apropriados
- [ ] Tratar erros e respostas vazias
- [ ] Adicionar logs para debug
- [ ] Testar em diferentes páginas do site

### Dicas de Debug

```kotlin
// Adicionar logs
Log.d("MeuProvider", "🔍 Carregando: $url")
Log.d("MeuProvider", "✅ Encontrados ${items.size} items")
Log.e("MeuProvider", "❌ Erro: ${e.message}")

// Verificar HTML retornado
val html = app.get(url).text
Log.d("MeuProvider", "HTML (primeiros 500 chars): ${html.take(500)}")
```

### Tratamento de Erros

```kotlin
override suspend fun load(url: String): LoadResponse? {
    return try {
        val document = app.get(url).document
        
        val title = document.selectFirst("h1")?.text()
        if (title.isNullOrBlank()) {
            Log.e("MeuProvider", "Título não encontrado em: $url")
            return null
        }
        
        // ... resto do código
        
    } catch (e: Exception) {
        Log.e("MeuProvider", "Erro ao carregar $url: ${e.message}")
        null
    }
}
```

---

## 📚 Recursos Adicionais

### Documentação Oficial
- [CloudStream Docs](https://recloudstream.github.io/devs/)
- [Jsoup Documentation](https://jsoup.org/cookbook/)
- [BeautifulSoup Docs](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)

### Ferramentas
- [regex101.com](https://regex101.com) - Testar regex
- [json2kt.com](https://json2kt.com) - Gerar data classes
- [quicktype.io](https://quicktype.io) - Converter JSON para código

### Extensões Úteis
- Web Sniffer - Ver tráfego de rede
- JSON Viewer - Formatar JSON no navegador
- XPath Helper - Testar seletores XPath

---

## 🎯 Resumo Rápido

| Tarefa | Ferramenta/Método |
|--------|-------------------|
| Fazer requisições | `app.get()`, `app.post()` |
| Parsear HTML | Jsoup + seletores CSS |
| Extrair padrões | Regex |
| Parsear JSON | Jackson + data classes |
| Debug | `Log.d()`, `Log.e()` |
| Testar seletores | Console do navegador |
| Bypass de proteções | Headers customizados, cookies |

---

> 📝 **Nota**: Este guia foi adaptado da documentação oficial do CloudStream e complementado com exemplos práticos para desenvolvimento de providers.

**Última atualização**: Janeiro 2026