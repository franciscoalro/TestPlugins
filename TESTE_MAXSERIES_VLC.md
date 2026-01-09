# Teste MaxSeries → VLC - Resultados

## Resumo

Testamos a extração de links de vídeo direto do MaxSeries para reprodução no VLC.

## Estrutura do MaxSeries

1. **Página da série** → contém iframe para `playerthree.online`
2. **Iframe** → lista episódios com `data-episode-id`
3. **AJAX** → `/episodio/{id}` retorna botões com `data-source`
4. **Players disponíveis**:
   - `playerembedapi.link` - JavaScript ofuscado
   - `megaembed.link` - API criptografada
   - `bysebuho.com` (Doodstream) - Tokens dinâmicos

## Resultado dos Testes

❌ **Não foi possível extrair links diretos automaticamente**

### Motivos:
- Players usam **JavaScript ofuscado/packed**
- URLs de vídeo são **Blob URLs** gerados dinamicamente
- **Tokens temporários** que expiram rapidamente
- **Verificação de referrer** obrigatória
- APIs retornam dados **criptografados**

## Como Extrair Manualmente

1. Abra o player no navegador (ex: `https://megaembed.link/#rckhv6`)
2. Pressione **F12** → aba **Network**
3. Filtre por **m3u8** ou **mp4**
4. Clique em **Play** no player
5. Copie a URL que aparecer
6. Abra no VLC:
   ```
   vlc "URL_DO_VIDEO" --http-referrer="URL_DO_PLAYER"
   ```

## Sobre o Plugin CloudStream

O plugin MaxSeries v23 usa `loadExtractor()` que tenta os extractors padrão do CloudStream. Alguns players podem funcionar se o CloudStream tiver extractors compatíveis.

Players que **podem funcionar** no CloudStream:
- Doodstream (se tiver extractor atualizado)
- Filemoon
- StreamTape

Players que **não funcionam**:
- MegaEmbed (API proprietária)
- PlayerEmbedAPI (JavaScript ofuscado)

## Conclusão

A extração automática de links de vídeo desses players modernos requer:
- Execução completa de JavaScript
- Interceptação de rede em tempo real
- Engenharia reversa do código ofuscado

O CloudStream consegue reproduzir alguns porque tem extractors específicos que fazem essa engenharia reversa.
