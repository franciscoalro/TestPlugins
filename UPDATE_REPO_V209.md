# Atualizar Repositório para v209

## 🎯 Objetivo

Atualizar o arquivo `repo.json` no branch `builds` para incluir a versão v209 do MaxSeries.

## 📋 Passos

### 1. Verificar Branch Atual
```bash
git branch
```

### 2. Mudar para Branch Builds
```bash
git checkout builds
```

### 3. Atualizar repo.json

Editar o arquivo `repo.json` e atualizar a versão do MaxSeries:

```json
{
  "name": "BRCloudstream Repository",
  "description": "Repositório de extensões brasileiras para Cloudstream",
  "manifestVersion": 1,
  "pluginLists": [
    "https://raw.githubusercontent.com/franciscoalro/brcloudstream/builds/plugins.json"
  ]
}
```

### 4. Atualizar plugins.json

Editar `plugins.json`:

```json
[
  {
    "name": "MaxSeries",
    "url": "https://github.com/franciscoalro/brcloudstream/releases/download/v209/MaxSeries.cs3",
    "version": 209,
    "description": "MaxSeries v209 - 7 Extractors + 24 Categories",
    "authors": ["franciscoalro"],
    "status": 1,
    "tvTypes": ["TvSeries", "Movie"],
    "language": "pt-BR",
    "iconUrl": "https://www.maxseries.one/wp-content/themes/dooplay/assets/img/favicon.png"
  }
]
```

### 5. Commit e Push
```bash
git add repo.json plugins.json
git commit -m "chore: Update MaxSeries to v209"
git push origin builds
```

### 6. Voltar para Main
```bash
git checkout main
```

## 🔗 URLs Importantes

### Repositório
```
https://raw.githubusercontent.com/franciscoalro/brcloudstream/refs/heads/builds/repo.json
```

### Release v209
```
https://github.com/franciscoalro/brcloudstream/releases/tag/v209
```

### Download Direto
```
https://github.com/franciscoalro/brcloudstream/releases/download/v209/MaxSeries.cs3
```

## ✅ Verificação

Após atualizar, testar no Cloudstream:

1. Remover repositório antigo (se existir)
2. Adicionar repositório atualizado
3. Verificar se v209 aparece
4. Instalar e testar

## 📝 Changelog para repo.json

```
v209 (26 Jan 2026)
- Added 4 new video extractors
- DoodStream, StreamTape, Mixdrop, Filemoon
- Success rate: 85% → 99%
- Total: 7 extractors + fallback
```

---

**Data:** 26 Janeiro 2026  
**Versão:** 209
