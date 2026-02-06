# Correções Aplicadas - CloudStream Plugins

## Data: 05/02/2026

## Problema Identificado
Os plugins não estavam funcionando porque os arquivos `.cs3` na pasta `builds/` estavam com **tamanhos incorretos** comparados aos originais do saimuelrepo. O CloudStream faz validação de checksum (tamanho do arquivo) e rejeita downloads quando o tamanho não corresponde ao declarado no `plugins.json`.

## Providers que Funcionavam
- ✅ DonghuaNoSekai (19,328 bytes - correto)
- ✅ Doramas (16,792 bytes - correto)  
- ✅ NovelasFlix (18,629 bytes - correto)

## Providers que NÃO Funcionavam (e por quê)
| Provider | Tamanho Antigo | Tamanho Correto | Diferença |
|----------|---------------|-----------------|-----------|
| MaxSeries | 653,406 bytes | 747,166 bytes | -93,760 bytes |
| MegaFlix | 21,595 bytes | 15,126 bytes | +6,469 bytes |
| PobreFlix | 34,193 bytes | 20,855 bytes | +13,338 bytes |
| NetCine | 28,346 bytes | 17,639 bytes | +10,707 bytes |
| Streamberry | Desatualizado | 20,378 bytes | Desconhecida |
| TopFilmes | Desatualizado | 13,586 bytes | Desconhecida |

## Correções Aplicadas

### 1. Arquivos .cs3 Atualizados
Todos os arquivos `.cs3` foram copiados do `saimuelrepo` para a pasta `builds/`:
- MaxSeries.cs3 (747,166 bytes)
- MegaFlix.cs3 (15,126 bytes)
- PobreFlix.cs3 (20,855 bytes)
- NetCine.cs3 (17,639 bytes)
- Streamberry.cs3 (20,378 bytes)
- TopFilmes.cs3 (13,586 bytes)
- AnimesCloud.cs3 (22,370 bytes)
- AnimesDigital.cs3 (27,391 bytes)
- Anroll.cs3 (35,987 bytes)
- BetterAnime.cs3 (18,515 bytes)
- DonghuaNoSekai.cs3 (19,328 bytes)
- Doramas.cs3 (16,792 bytes)
- EmbedCanais.cs3 (9,758 bytes)
- FilmesOn.cs3 (22,862 bytes)
- GoFlix.cs3 (18,662 bytes)
- NovelasFlix.cs3 (18,629 bytes)
- OverFlix.cs3 (22,835 bytes)
- UltraCine.cs3 (17,613 bytes)
- VisionCine.cs3 (26,559 bytes)

### 2. plugins.json Atualizado
- Atualizado `fileSize` para todos os providers
- URLs apontando para `saimuelbr/saimuelrepo`
- Todas as versões e apiVersion corretas

### 3. Código Fonte Sincronizado
Arquivos Kotlin do MaxSeries foram sincronizados com o saimuelrepo:
- MaxSeries.kt
- Todos os extractores
- Utilitários (crypto, network, resolver, session, utils)

## Como Usar no CloudStream

### Opção 1: Usar o Repositório SaimuelBR (Recomendado)
1. Abra o CloudStream
2. Vá em "Configurações" → "Extensões" → "Adicionar repositório"
3. Cole esta URL:
   ```
   https://raw.githubusercontent.com/saimuelbr/saimuelrepo/main/builds/repo.json
   ```
4. Toque em "Adicionar"
5. Os plugins aparecerão na lista para download

### Opção 2: Usar Seu Próprio Repositório
Se quiser hospedar no seu próprio GitHub:

1. **Crie um repositório no GitHub** (ex: `seuusuario/cloudstream-repo`)

2. **Faça upload dos arquivos**:
   - Todos os `.cs3` da pasta `builds/`
   - `plugins.json`
   - `repo.json` (atualizado com sua URL)

3. **Atualize o repo.json**:
   ```json
   {
     "name": "Meu Repositório",
     "iconUrl": "https://seu-icon-url.png",
     "description": "Repositório de plugins",
     "manifestVersion": 1,
     "pluginLists": [
       "https://raw.githubusercontent.com/SEUUSUARIO/NOMEREPO/main/builds/plugins.json"
     ]
   }
   ```

4. **Atualize o plugins.json** - Troque todas as URLs:
   ```json
   "url": "https://raw.githubusercontent.com/SEUUSUARIO/NOMEREPO/main/builds/NomePlugin.cs3"
   ```

5. **No CloudStream**, adicione a URL do seu repo.json

## Estrutura de Arquivos
```
brcloudstream/
├── builds/
│   ├── MaxSeries.cs3          ✅ Atualizado (747KB)
│   ├── MegaFlix.cs3           ✅ Atualizado (15KB)
│   ├── PobreFlix.cs3          ✅ Atualizado (21KB)
│   ├── NetCine.cs3            ✅ Atualizado (17KB)
│   ├── DonghuaNoSekai.cs3     ✅ Atualizado (19KB)
│   ├── Doramas.cs3            ✅ Atualizado (17KB)
│   ├── NovelasFlix.cs3        ✅ Atualizado (18KB)
│   ├── Streamberry.cs3        ✅ Atualizado (20KB)
│   ├── TopFilmes.cs3          ✅ Atualizado (14KB)
│   ├── AnimesCloud.cs3        ✅ Atualizado (22KB)
│   ├── AnimesDigital.cs3      ✅ Atualizado (27KB)
│   ├── Anroll.cs3             ✅ Atualizado (36KB)
│   ├── BetterAnime.cs3        ✅ Atualizado (19KB)
│   ├── EmbedCanais.cs3        ✅ Atualizado (10KB)
│   ├── FilmesOn.cs3           ✅ Atualizado (23KB)
│   ├── GoFlix.cs3             ✅ Atualizado (19KB)
│   ├── OverFlix.cs3           ✅ Atualizado (23KB)
│   ├── UltraCine.cs3          ✅ Atualizado (17KB)
│   ├── VisionCine.cs3         ✅ Atualizado (27KB)
│   └── plugins.json           ✅ Atualizado
├── plugins.json               ✅ Atualizado
├── repo.json                  ✅ Atualizado
└── MaxSeries/                 ✅ Código sincronizado
    └── src/main/kotlin/...
```

## Próximos Passos

1. **Teste no CloudStream** usando a URL do saimuelrepo primeiro
2. Se funcionar, você pode:
   - Continuar usando o saimuelrepo (sempre atualizado)
   - Ou criar seu próprio fork no GitHub

3. **Para atualizar no futuro**:
   - Copie os novos arquivos .cs3 do saimuelrepo
   - Atualize o plugins.json com os novos tamanhos
   - Faça commit e push para o GitHub

## Contato e Suporte
- Repositório original: `saimuelbr/saimuelrepo`
- Versão MaxSeries atual: v264

---

**Nota**: Os arquivos `.cs3` são binários compilados. Eles precisam ser exatamente iguais aos do repositório fonte para funcionar corretamente no CloudStream.
