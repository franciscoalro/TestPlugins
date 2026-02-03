# GUIA DE TESTE - CloudStream

## 🎯 Objetivo
Testar a implementação PlayerEmbedAPI ultra-rápida no CloudStream

---

## 📋 Pré-requisitos

### 1. Ambiente de Desenvolvimento
- [ ] Android Studio instalado
- [ ] SDK Android configurado
- [ ] JDK 11 ou superior
- [ ] Git instalado

### 2. Projeto CloudStream
- [ ] Repositório CloudStream clonado
- [ ] Branch de desenvolvimento configurada

---

## 🔧 Opção 1: Integrar no Projeto Existente

### Passo 1: Baixar Arquivos

**Do Release GitHub:**
```
https://github.com/franciscoalro/TestPlugins/releases/tag/v2.1.0
```

Arquivos necessários:
- `MaxSeriesProvider_Final.kt`
- `PlayerEmbedAPIExtractor_Final.kt`

### Passo 2: Copiar Arquivos

```
cloudstream-extensions/
├── MaxSeries/
│   └── src/
│       └── main/
│           └── kotlin/
│               └── com/
│                   └── franciscoalro/
│                       └── maxseries/
│                           ├── MaxSeriesProvider.kt  <- SUBSTITUIR
│                           └── extractors/
│                               └── PlayerEmbedAPIExtractor.kt  <- NOVO
```

### Passo 3: Modificar MaxSeriesProvider.kt

Se já tiver um provider existente, adicione apenas o extrator:

```kotlin
// Adicionar import
import com.franciscoalro.maxseries.extractors.PlayerEmbedAPIExtractor

// Dentro da classe MaxSeriesProvider
class MaxSeriesProvider : MainAPI() {
    
    // Instanciar extrator
    private val playerEmbedExtractor = PlayerEmbedAPIExtractor()
    
    override suspend fun loadLinks(
        data: String,
        isCasting: Boolean,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        
        // ... código existente ...
        
        for (playerUrl in playerUrls) {
            when {
                // PlayerEmbedAPI - NOVO!
                playerUrl.contains("playerembedapi") -> {
                    if (playerEmbedExtractor.extract(playerUrl, callback)) {
                        found++
                        continue
                    }
                }
                
                // Outros players...
            }
        }
        
        return found > 0
    }
}
```

### Passo 4: Buildar

```bash
# Limpar build anterior
./gradlew :MaxSeries:clean

# Buildar
./gradlew :MaxSeries:build

# Gerar .cs3
./gradlew :MaxSeries:generateCS3
```

Arquivo gerado:
```
MaxSeries/build/MaxSeries.cs3
```

---

## 📱 Opção 2: Instalar Diretamente no Celular

### Passo 1: Obter arquivo .cs3

**Opção A:** Buildar do código fonte (acima)

**Opção B:** Usar release existente
```
https://github.com/franciscoalro/TestPlugins/releases
```

### Passo 2: Transferir para celular

```bash
# ADB
adb push MaxSeries.cs3 /sdcard/Download/

# Ou transferir manualmente (USB, email, etc)
```

### Passo 3: Instalar no CloudStream

1. Abrir CloudStream
2. Ir em: Configurações → Extensões
3. Clique no botão "+" ou "Instalar"
4. Selecionar arquivo `MaxSeries.cs3`
5. Aguardar instalação

### Passo 4: Testar

1. Voltar à tela inicial do CloudStream
2. Buscar série/filme no MaxSeries
3. Selecionar episódio
4. Clicar em "Assistir"
5. Verificar se carrega o vídeo

---

## 🔍 Verificação de Logs

### Ativar Logs ADB

```bash
# Conectar celular
adb devices

# Ver logs
adb logcat -s MaxSeries:D PlayerEmbedAPI:D *:S
```

### Logs Esperados

**Sucesso (HTTP Rápido):**
```
D/MaxSeries: [PlayerEmbedAPI] Iniciando extração: https://playerembedapi.link/?v=xxx
D/MaxSeries: [PlayerEmbedAPI] Dados extraídos: slug=rZeP5UzqD, md5_id=29077990
D/MaxSeries: [PlayerEmbedAPI] ✅ Extração rápida em 257ms
```

**Sucesso (WebView):**
```
D/MaxSeries: [PlayerEmbedAPI] HTTP rápido falhou, usando WebView...
D/MaxSeries: [PlayerEmbedAPI] ✅ WebView sucesso
```

**Erro:**
```
E/MaxSeries: [PlayerEmbedAPI] Erro: timeout
```

---

## 📊 Testes de Performance

### Teste 1: Tempo de Extração

```
Reproduzir 5 vídeos diferentes
Medir tempo entre "clicar" e "iniciar"
```

**Resultado esperado:**
- 4/5 vídeos: < 500ms (HTTP rápido)
- 1/5 vídeos: ~10-15s (WebView fallback)

### Teste 2: Qualidade de Vídeo

```
Verificar se múltiplas qualidades são detectadas
(360p, 480p, 720p, 1080p)
```

### Teste 3: Estabilidade

```
Reproduzir vídeo por 5 minutos
Verificar se há travamentos
```

---

## 🐛 Troubleshooting

### Problema: Timeout HTTP

**Sintoma:**
```
E/MaxSeries: [PlayerEmbedAPI] Erro: timeout
```

**Solução:**
```kotlin
// Aumentar timeout no PlayerEmbedAPIExtractor.kt
private val HTTP_TIMEOUT = 10000L  // 10 segundos (era 5s)
```

### Problema: WebView não encontra vídeo

**Sintoma:**
```
D/MaxSeries: [PlayerEmbedAPI] HTTP rápido falhou, usando WebView...
E/MaxSeries: [PlayerEmbedAPI] ❌ WebView não encontrou vídeo
```

**Solução:**
1. Verificar se PlayerEmbedAPI mudou estrutura
2. Atualizar regex no código
3. Aumentar tempo de espera do WebView

### Problema: URL CDN retorna 403

**Sintoma:**
```
HTTP 403 Forbidden
```

**Solução:**
```kotlin
// Verificar headers no código
headers = mapOf(
    "Referer" to "https://playerembedapi.link/",
    "Origin" to "https://playerembedapi.link",
    "User-Agent" to "Mozilla/5.0..."
)
```

---

## ✅ Checklist de Teste

- [ ] Build completa sem erros
- [ ] Arquivo .cs3 gerado
- [ ] Instalação no CloudStream bem-sucedida
- [ ] Busca de conteúdo funciona
- [ ] PlayerEmbedAPI detectado
- [ ] Vídeo inicia em < 5 segundos
- [ ] Qualidade ajustável
- [ ] Sem travamentos em 5 minutos
- [ ] Logs mostram extração bem-sucedida
- [ ] Fallback WebView funciona (se necessário)

---

## 📞 Suporte

### Debug Avançado

```bash
# Logs completos
adb logcat | grep -E "MaxSeries|PlayerEmbedAPI|CloudStream"

# Screenshot
date=$(date +%Y%m%d_%H%M%S)
adb shell screencap -p /sdcard/screenshot_$date.png
adb pull /sdcard/screenshot_$date.png
```

### Reportar Problemas

Incluir:
1. Versão do CloudStream
2. Versão do Android
3. Logs do ADB
4. URL do vídeo testado
5. Screenshot (se aplicável)

---

**Pronto para testar!** 🚀
