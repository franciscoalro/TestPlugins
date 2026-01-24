# 🚀 MaxSeries v159 - Correção Crítica de Extração

## 📅 Data: 22/01/2026 22:15

---

## 🔧 FIX CRÍTICO: WebView "Promise Trap" 🪤

### **O Problema (v156/158)**
O script de interceptação estava retornando uma **Promise** JavaScript para o CloudStream.
O interpretador do WebView recebia o objeto Promise instantaneamente e considerava a execução "Concluída" (`onPageFinished`), fechando o navegador interno **antes** de encontrar o link do vídeo.
- **Sintoma:** Logs com "Todas as estratégias falharam" em menos de 300ms.
- **Resultado:** Vídeos não reproduziam.

### **A Solução (v159)**
Modificado o script `MegaEmbedExtractorV8.kt` para:
1.  **Não retornar nada** (mantendo o WebView aberto).
2.  **Navigation/Fetch Trap:** Ao encontrar o link, o script força uma navegação (`window.location.href`) E um fetch (`fetch(url)`) para o link do vídeo.
3.  Isso obriga o interceptor (`shouldInterceptRequest`) do CloudStream a "ver" o link e capturá-lo.

---

## 📊 O QUE ESPERAR

- ✅ **Extração mais lenta, mas precisa:** O player pode demorar ~3-5 segundos para iniciar (tempo real de carregamento do MegaEmbed).
- ✅ **Sucesso:** A falha instantânea deve desaparecer.

---

## 🧪 COMO ATUALIZAR

1. **Repositório:** Atualize `franciscoalro/TestPlugins` (v159 deve aparecer).
2. **Update:** Atualize o plugin MaxSeries.
3. **Teste:** Abra **Sandokan** (Série) ou qualquer filme.

---

## 📝 ARQUIVOS MODIFICADOS

- `MegaEmbedExtractorV8.kt`: Script JS totalmente reescrito (Trap Mode).
- `build.gradle.kts`: Versão 159.
