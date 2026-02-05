#!/usr/bin/env python3
import json

# Criar plugins.json
plugins = [
    {
        "url": "https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/MaxSeries.cs3",
        "status": 1,
        "version": 264,
        "apiVersion": 1,
        "name": "MaxSeries",
        "internalName": "MaxSeries",
        "authors": ["franciscoalro"],
        "description": "MaxSeries v264",
        "repositoryUrl": "https://github.com/franciscoalro/TestPlugins",
        "tvTypes": ["TvSeries", "Movie"],
        "language": "pt-BR",
        "fileSize": 747487
    },
    {
        "url": "https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/AnimesOnlineCC.cs3",
        "status": 1,
        "version": 10,
        "apiVersion": 1,
        "name": "AnimesOnlineCC",
        "internalName": "AnimesOnlineCC",
        "authors": ["franciscoalro"],
        "description": "AnimesOnlineCC v10",
        "repositoryUrl": "https://github.com/franciscoalro/TestPlugins",
        "tvTypes": ["Anime"],
        "language": "pt-BR",
        "fileSize": 27630
    },
    {
        "url": "https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/Vizer.cs3",
        "status": 1,
        "version": 2,
        "apiVersion": 1,
        "name": "Vizer",
        "internalName": "Vizer",
        "authors": ["franciscoalro"],
        "description": "Vizer v2",
        "repositoryUrl": "https://github.com/franciscoalro/TestPlugins",
        "tvTypes": ["TvSeries", "Movie"],
        "language": "pt-BR",
        "fileSize": 41496
    },
    {
        "url": "https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/NetCine.cs3",
        "status": 1,
        "version": 2,
        "apiVersion": 1,
        "name": "NetCine",
        "internalName": "NetCine",
        "authors": ["franciscoalro"],
        "description": "NetCine v2",
        "repositoryUrl": "https://github.com/franciscoalro/TestPlugins",
        "tvTypes": ["TvSeries", "Movie"],
        "language": "pt-BR",
        "fileSize": 28346
    },
    {
        "url": "https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/MegaFlix.cs3",
        "status": 1,
        "version": 2,
        "apiVersion": 1,
        "name": "MegaFlix",
        "internalName": "MegaFlix",
        "authors": ["franciscoalro"],
        "description": "MegaFlix v2",
        "repositoryUrl": "https://github.com/franciscoalro/TestPlugins",
        "tvTypes": ["TvSeries", "Movie"],
        "language": "pt-BR",
        "fileSize": 21595
    },
    {
        "url": "https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/PobreFlix.cs3",
        "status": 1,
        "version": 2,
        "apiVersion": 1,
        "name": "PobreFlix",
        "internalName": "PobreFlix",
        "authors": ["franciscoalro"],
        "description": "PobreFlix v2",
        "repositoryUrl": "https://github.com/franciscoalro/TestPlugins",
        "tvTypes": ["TvSeries", "Movie"],
        "language": "pt-BR",
        "fileSize": 34193
    },
    {
        "url": "https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/OverFlix.cs3",
        "status": 1,
        "version": 2,
        "apiVersion": 1,
        "name": "OverFlix",
        "internalName": "OverFlix",
        "authors": ["franciscoalro"],
        "description": "OverFlix v2",
        "repositoryUrl": "https://github.com/franciscoalro/TestPlugins",
        "tvTypes": ["TvSeries", "Movie"],
        "language": "pt-BR",
        "fileSize": 39078
    }
]

# Salvar sem BOM
with open('plugins.json', 'w', encoding='utf-8') as f:
    json.dump(plugins, f, indent=2, ensure_ascii=False)

print("OK: plugins.json criado (UTF-8 sem BOM)")

# Criar repo.json
repo = {
    "name": "Franciscoalro Plugins",
    "description": "Repositorio de plugins para CloudStream3",
    "manifestVersion": 1,
    "pluginLists": [
        "https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/plugins.json"
    ]
}

with open('repo.json', 'w', encoding='utf-8') as f:
    json.dump(repo, f, indent=2, ensure_ascii=False)

print("OK: repo.json criado (UTF-8 sem BOM)")

# Verificar
with open('plugins.json', 'rb') as f:
    first_byte = f.read(1)
    if first_byte == b'[':
        print("OK: plugins.json sem BOM")
    else:
        print(f"AVISO: plugins.json primeiro byte: {first_byte}")
