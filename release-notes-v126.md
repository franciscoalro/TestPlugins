# MaxSeries v126 - WebView Melhorado (120s timeout)

## 📅 Data: 18/01/2026

## 🎯 Objetivo
Melhorar o WebView do MegaEmbed para aguardar a descriptografia da API e capturar a URL do vídeo após o JavaScript processar os dados.

## 🔧 Mudanças

### MegaEmbed v5.2 - WebView Otimizado
- ✅ **Timeout aumentado**: 60s → 120s (aguardar descriptografia)
- ✅ **Função tryPlay()**: Tenta forçar play do vídeo a cada 1s
- ✅ **Padrão 6 NOVO**: Busca em atributos `data-src`, `data-url`, `src` de elementos do player
- ✅ **Logs melhorados**: TAG atualizado para v126
- ✅ **Código limpo**: Removido código duplicado

### Estratégias de Extração (ordem):
1. **Direct API** (v125) - Tenta API direta
2. **HTML Regex** - Busca URLs .txt no HTML
3. **JsUnpacker** - Descompacta JavaScript ofuscado
4. **WebView JavaScript-Only** (v126 MELHORADO) - Executa JS e aguarda descriptografia
5. **WebView Interceptação** - Intercepta requisições de rede

## 📊 Timeouts Atualizados

| Extractor | v125 | v126 |
|-----------|------|------|
| MegaEmbed WebView JS | 60s | **120s** |
| MegaEmbed Interceptação | 60s | 60s |
| PlayerEmbedAPI | 30s | 30s |

## 🧪 Como Testar

1. Instalar v126:
```bash
adb install -r MaxSeries\build\MaxSeries.cs3
```

2. Monitorar logs:
```powershell
.\monitor-live.ps1
```

3. Testar episódio:
- Abrir MaxSeries
- Buscar "Terra de Pecados"
- Tentar reproduzir episódio 1
- Verificar logs ADB

## 🔍 O Que Esperar nos Logs

### MegaEmbed - Sucesso:
```
MegaEmbedExtractorV5_v126: === MEGAEMBED V5 ALL STRATEGIES (v126) ===
MegaEmbedExtractorV5_v126: 🔍 [3/5] Tentando WebView JavaScript-Only...
MegaEmbedExtractorV5_v126: 📜 JS Callback capturou: https://.../.txt
MegaEmbedExtractorV5_v126: 🎯 WebView JS capturou: https://.../.txt
MegaEmbedExtractorV5_v126: ✅ WebView JavaScript funcionou!
```

### MegaEmbed - Timeout:
```
MegaEmbedExtractorV5_v126: 🔍 [3/5] Tentando WebView JavaScript-Only...
MegaEmbedExtractorV5_v126: ⚠️ WebView JS: Nenhuma URL capturada
MegaEmbedExtractorV5_v126: 🔍 [4/5] Tentando WebView com Interceptação...
```

## 📝 Notas Técnicas

### Por Que 120s?
- API `/api/v1/info?id=3wnuij` retorna dados criptografados (AES-CBC)
- JavaScript precisa descriptografar antes de gerar URL do vídeo
- Processo pode levar 30-60s dependendo do dispositivo
- 120s garante tempo suficiente para descriptografia completa

### Função tryPlay()
```javascript
function tryPlay() {
    var videos = document.querySelectorAll('video');
    for(var i=0; i<videos.length; i++) {
        if(videos[i].paused) {
            videos[i].muted = true;
            videos[i].play().catch(function(){});
        }
    }
}
```
- Força play do vídeo (muted) para disparar carregamento
- Executado a cada 10 tentativas (1s)
- Pode acelerar processo de descriptografia

### Padrão 6 - Atributos do Player
```javascript
var players = document.querySelectorAll('[class*="player"]');
for(var i=0; i<players.length; i++) {
    var playerData = players[i].getAttribute('data-src') || 
                   players[i].getAttribute('data-url') ||
                   players[i].getAttribute('src');
    if(playerData && playerData.includes('.txt')) {
        resolve(playerData);
    }
}
```
- Busca em elementos com classe contendo "player"
- Verifica atributos `data-src`, `data-url`, `src`
- Captura URL .txt diretamente do DOM

## 🚀 Próximos Passos

Se v126 funcionar:
- ✅ Commit e push para GitHub
- ✅ Criar tag v126.0
- ✅ Criar release no GitHub
- ✅ Atualizar plugins.json

Se v126 falhar:
- Considerar reverse engineering da descriptografia
- Ou implementar solução híbrida (API + WebView)

---

**Versão**: 126  
**Build**: MaxSeries.cs3  
**Tipo**: WebView Optimization  
**Status**: Pronto para teste
