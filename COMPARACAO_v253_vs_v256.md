# Comparação: v253 (Funcionava) vs v256 (Corrigida)

## 📊 Diferenças Encontradas

### Formato do JSON

| Aspecto | v253 (Funcionava) | v256 (Antes - Erro) | v256 (Agora - Corrigido) |
|---------|-------------------|---------------------|--------------------------|
| **Formatação** | Indentado (com espaços) | Compacto (1 linha) | ✅ Indentado (igual v253) |
| **Quebras de linha** | Sim (`\n`) | Não | ✅ Sim |
| **Arrays** | Multi-linha | Uma linha | ✅ Multi-linha |
| **BOM UTF-8** | Não tinha | Tinha | ✅ Removido |
| **Caracteres especiais** | Codificados estranhamente | Problema pior | ✅ Simplificados |

### Estrutura do repo.json

**v253 (Funcionava):**
```json
{
    "name": "Francisco Plugins",
    "description": "Repositório pessoal de extensões",
    "manifestVersion": 1,
    "pluginLists": [
        "https://franciscoalro.github.io/CloudstreamRepo/plugins.json"
    ]
}
```

**v256 (Agora - Corrigido):**
```json
{
    "name": "Francisco Plugins",
    "description": "Repositorio pessoal de extensoes",
    "manifestVersion": 1,
    "pluginLists": [
        "https://franciscoalro.github.io/CloudstreamRepo/plugins.json"
    ]
}
```

### Estrutura do plugins.json

**v253 (Funcionava):**
```json
[
    {
        "name": "MaxSeries",
        "internalName": "MaxSeries",
        "description": "MaxSeries v253 - Plugin...",
        "version": 253,
        "authors": [
            "franciscoalro"
        ],
        "tvTypes": [
            "TvSeries",
            "Movie"
        ],
        ...
    }
]
```

**v256 (Agora - Corrigido):**
```json
[
    {
        "name": "MaxSeries",
        "internalName": "MaxSeries",
        "description": "MaxSeries v256 - PlayerEmbedAPI V8+V7 Fixes",
        "version": 256,
        "authors": [
            "franciscoalro"
        ],
        "tvTypes": [
            "TvSeries",
            "Movie"
        ],
        ...
    }
]
```

## 🔍 O Problema

O CloudStream parece ter dificuldade com:
1. JSONs em formato compacto (uma linha)
2. BOM UTF-8 no início do arquivo
3. Arrays em uma única linha

## ✅ Solução Aplicada

Agora o formato da v256 é **idêntico** ao da v253:
- ✅ Formatação indentada
- ✅ Arrays multi-linha
- ✅ Sem BOM
- ✅ Sem caracteres especiais problemáticos

## 🧪 Testar

1. Aguarde 2-5 minutos para propagação do GitHub Pages
2. Limpe cache do CloudStream
3. Re-adicione o repositório
4. Tente baixar o MaxSeries v256

## 🔗 URLs

- Repo: https://franciscoalro.github.io/CloudstreamRepo/repo.json
- Plugins: https://franciscoalro.github.io/CloudstreamRepo/plugins.json
