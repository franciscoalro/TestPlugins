# 🎬 Teste PlayerEmbedAPI - FILME

## 🎯 Objetivo

Testar PlayerEmbedAPI com um **FILME** (não série) para reproduzir o erro 2004.

## 📋 Pré-requisitos

- ✅ MaxSeries v220 instalado
- ✅ ADB conectado (USB ou WiFi)
- ✅ Cloudstream aberto no celular

## 🎬 Filmes para Testar

Baseado nos logs anteriores, estes filmes foram carregados:

### Opção 1: Filme tt27425164
```
https://www.maxseries.pics/filmes/[buscar-pelo-titulo]
```

### Opção 2: Filme tt6604188
```
https://www.maxseries.pics/filmes/[buscar-pelo-titulo]
```

### Opção 3: Filme tt32020404
```
https://www.maxseries.pics/filmes/[buscar-pelo-titulo]
```

### Opção 4: Qualquer Filme
```
1. Abrir MaxSeries
2. Ir em "Filmes" ou "Em Alta"
3. Escolher qualquer FILME (não série)
```

## 📝 Passo a Passo

### 1. Preparar Captura de Logs

```powershell
# No PowerShell, executar:
cd C:\Users\KYTHOURS\Desktop\platform-tools
.\adb.exe logcat -c
```

### 2. Abrir Filme no Cloudstream

1. Abrir Cloudstream no celular
2. Buscar um **FILME** no MaxSeries
3. Clicar no filme
4. Clicar em "Assistir" ou "Play"

### 3. Aguardar Lista de Players

Você deve ver algo como:
```
✅ MegaEmbed 1080p
✅ MyVidPlay 720p
✅ PlayerEmbedAPI HD  ← ESTE É O QUE QUEREMOS TESTAR
✅ DoodStream 480p
```

### 4. Clicar em PlayerEmbedAPI

1. Clicar em "PlayerEmbedAPI HD"
2. Aguardar carregar (pode demorar 20-30s)
3. Observar o que acontece:
   - ✅ **Funciona**: Vídeo começa a reproduzir
   - ❌ **Erro 2004**: Aparece mensagem de erro

### 5. Capturar Logs

#### Se Funcionou ✅
```powershell
.\adb.exe logcat -d > playerembedapi_sucesso_filme.txt
```

#### Se Deu Erro ❌
```powershell
.\adb.exe logcat -d > playerembedapi_erro_filme.txt
```

## 🔍 O Que Procurar nos Logs

### Logs Esperados (Sucesso)

```
MaxSeriesProvider: 🌐🌐🌐 PLAYEREMBEDAPI DETECTADO! 🌐🌐🌐
MaxSeriesProvider: 🎬 IMDB ID extraído: tt12345678
PlayerEmbedAPI: 🚀🚀🚀 EXTRACT CHAMADO! IMDB: tt12345678
PlayerEmbedAPI: ✅ Context obtido
PlayerEmbedAPI: 🌐 Loading: https://viewplayer.online/filme/tt12345678
PlayerEmbedAPI: 🎯 Captured: https://...sssrr.org/?timestamp=...
PlayerEmbedAPI: 📹 Captured: https://storage.googleapis.com/.../video.mp4
MaxSeriesProvider: ✅✅✅ PlayerEmbedAPI: 2 links via WebView ✅✅✅
```

### Logs de Erro (Falha)

```
MaxSeriesProvider: 🌐🌐🌐 PLAYEREMBEDAPI DETECTADO! 🌐🌐🌐
MaxSeriesProvider: 🎬 IMDB ID extraído: tt12345678
PlayerEmbedAPI: 🚀🚀🚀 EXTRACT CHAMADO! IMDB: tt12345678
PlayerEmbedAPI: ✅ Context obtido
PlayerEmbedAPI: 🌐 Loading: https://viewplayer.online/filme/tt12345678
PlayerEmbedAPI: ⏱️ Timeout - captured 0 URLs
```

OU

```
MaxSeriesProvider: 🌐🌐🌐 PLAYEREMBEDAPI DETECTADO! 🌐🌐🌐
MaxSeriesProvider: 🎬 IMDB ID extraído: tt12345678
PlayerEmbedAPI: 🚀🚀🚀 EXTRACT CHAMADO! IMDB: tt12345678
PlayerEmbedAPI: 🎯 Captured: https://...sssrr.org/?timestamp=...
[Depois, ao tentar reproduzir]
ExoPlayer: ERROR_CODE_IO_BAD_HTTP_STATUS (2004)
```

## 📊 Cenários Possíveis

### Cenário 1: PlayerEmbedAPI NÃO Aparece na Lista

**Causa**: IMDB ID não foi extraído (filme usa ViewPlayer mas URL está errada)

**Logs esperados**:
```
MaxSeriesProvider: ❌ IMDB ID não encontrado para PlayerEmbedAPI
```

**Solução**: Verificar se o filme realmente usa ViewPlayer

### Cenário 2: PlayerEmbedAPI Aparece mas Demora Muito

**Causa**: WebView está carregando mas não captura URLs

**Logs esperados**:
```
PlayerEmbedAPI: 🌐 Loading: https://viewplayer.online/filme/...
[30 segundos depois]
PlayerEmbedAPI: ⏱️ Timeout - captured 0 URLs
```

**Solução**: Aumentar timeout ou melhorar automação

### Cenário 3: PlayerEmbedAPI Captura URLs mas Dá Erro 2004

**Causa**: URLs capturadas mas headers incorretos ou URL expirou

**Logs esperados**:
```
PlayerEmbedAPI: 🎯 Captured: https://...
[Depois]
ExoPlayer: ERROR_CODE_IO_BAD_HTTP_STATUS (2004)
```

**Solução**: Adicionar headers ou seguir redirects

### Cenário 4: PlayerEmbedAPI Funciona Perfeitamente

**Causa**: Tudo está funcionando!

**Logs esperados**:
```
PlayerEmbedAPI: 📹 Captured: https://storage.googleapis.com/.../video.mp4
[Vídeo reproduz normalmente]
```

**Solução**: Nenhuma, está funcionando!

## 🎯 Informações Importantes

### Diferença entre Filme e Série

| Tipo | URL | IMDB ID | PlayerEmbedAPI |
|------|-----|---------|----------------|
| **Filme** | `viewplayer.online/filme/tt123456` | ✅ Sim | ✅ Funciona |
| **Série** | `playerthree.online/embed/slug` | ❌ Não | ❌ Não funciona |

### Por Que Séries Não Funcionam?

PlayerEmbedAPI precisa de IMDB ID para construir a URL do ViewPlayer:
```kotlin
val viewPlayerUrl = "https://viewplayer.online/filme/$imdbId"
```

Séries usam slug em vez de IMDB ID:
```
https://playerthree.online/embed/a-knight-of-the-seven-kingdoms/
                                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                                 Slug, não IMDB ID
```

## 📝 Template de Relatório

Após o teste, preencher:

```
TESTE PLAYEREMBEDAPI - FILME

FILME TESTADO:
- Título: [nome do filme]
- URL MaxSeries: [url]
- IMDB ID: [ttXXXXXXXX ou não encontrado]

RESULTADO:
- [ ] PlayerEmbedAPI apareceu na lista
- [ ] PlayerEmbedAPI foi clicado
- [ ] Vídeo começou a carregar
- [ ] Vídeo reproduziu com sucesso
- [ ] Deu erro 2004
- [ ] Outro erro: [descrever]

LOGS CAPTURADOS:
- Arquivo: [nome do arquivo .txt]
- Tamanho: [KB]
- IMDB ID extraído: [sim/não]
- URLs capturadas: [quantidade]
- Erro observado: [sim/não]

OBSERVAÇÕES:
[Descrever o que aconteceu]
```

## 🚀 Executar Agora

```powershell
# 1. Limpar logs
cd C:\Users\KYTHOURS\Desktop\platform-tools
.\adb.exe logcat -c

# 2. Abrir filme no Cloudstream e testar PlayerEmbedAPI

# 3. Capturar logs
.\adb.exe logcat -d > playerembedapi_teste_filme.txt

# 4. Compartilhar arquivo playerembedapi_teste_filme.txt
```

---

**Próxima ação**: Testar com um FILME e compartilhar os logs capturados.
