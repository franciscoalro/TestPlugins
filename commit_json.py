#!/usr/bin/env python3
import json
import subprocess
import os

# Criar plugins.json sem BOM
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

# Criar repo.json
repo = {
    "name": "Franciscoalro Plugins",
    "description": "Repositorio de plugins para CloudStream3",
    "manifestVersion": 1,
    "pluginLists": [
        "https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/plugins.json"
    ]
}

# Salvar sem BOM
with open('plugins.json', 'wb') as f:
    f.write(json.dumps(plugins, indent=2, ensure_ascii=False).encode('utf-8'))

with open('repo.json', 'wb') as f:
    f.write(json.dumps(repo, indent=2, ensure_ascii=False).encode('utf-8'))

print("Arquivos criados sem BOM")

# Git commands
subprocess.run(['git', 'add', 'plugins.json', 'repo.json'], check=True)
subprocess.run(['git', 'commit', '-m', 'Fix JSON files without BOM for CloudStream3 compatibility'], check=True)
subprocess.run(['git', 'push', 'origin', 'main'], check=True)

print("Commit e push realizados!")
