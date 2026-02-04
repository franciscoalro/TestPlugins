#!/usr/bin/env python3
"""
Script para criar release v263 no GitHub
"""

import os
import sys
import json
import hashlib
import requests
from pathlib import Path

VERSION = "263"
REPO_OWNER = "franciscoalro"
REPO_NAME = "TestPlugins"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

def log_step(msg):
    print(f"\n{'='*50}")
    print(f"  {msg}")
    print(f"{'='*50}")

def log_success(msg):
    print(f"[OK] {msg}")

def log_error(msg):
    print(f"[ERRO] {msg}")

def log_info(msg):
    print(f"[INFO] {msg}")

def calculate_sha256(filepath):
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha256.update(chunk)
    return sha256.hexdigest()

def update_jsons(version, file_size, file_hash):
    plugins = [{
        "url": f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/main/MaxSeries.cs3",
        "status": 1,
        "version": int(version),
        "apiVersion": 1,
        "name": "MaxSeries",
        "internalName": "MaxSeries",
        "authors": ["franciscoalro"],
        "description": f"MaxSeries v{version} - PlayerEmbedAPI Otimizado: V8 (Pure HTTP) prioritario + V7 (WebView) com timeout 25s como fallback",
        "repositoryUrl": f"https://github.com/{REPO_OWNER}/{REPO_NAME}",
        "tvTypes": ["TvSeries", "Movie"],
        "language": "pt-BR",
        "iconUrl": f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/main/icon.png",
        "fileSize": file_size
    }]
    
    with open("plugins.json", "w", encoding="utf-8") as f:
        json.dump(plugins, f, indent=2, ensure_ascii=False)
    log_success("plugins.json atualizado")
    
    repo = {
        "name": "MaxSeries",
        "description": f"MaxSeries v{version} - PlayerEmbedAPI Otimizado: V8 (Pure HTTP) prioritario + V7 (WebView) com timeout 25s como fallback",
        "manifestVersion": 1,
        "pluginLists": [f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/main/plugins.json"]
    }
    
    with open("repo.json", "w", encoding="utf-8") as f:
        json.dump(repo, f, indent=2, ensure_ascii=False)
    log_success("repo.json atualizado")
    
    simple = [{
        "url": f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/download/v{version}/MaxSeries.cs3",
        "status": 1,
        "version": int(version),
        "name": "MaxSeries",
        "description": f"MaxSeries v{version} - PlayerEmbedAPI Otimizado"
    }]
    
    with open("plugins-simple.json", "w", encoding="utf-8") as f:
        json.dump(simple, f, indent=2, ensure_ascii=False)
    log_success("plugins-simple.json atualizado")
    
    minimal = [{
        "name": "MaxSeries",
        "description": f"MaxSeries v{version} - PlayerEmbedAPI Otimizado: V8 (Pure HTTP) prioritario + V7 (WebView) com timeout 25s como fallback",
        "version": version,
        "url": f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/download/v{version}/MaxSeries.cs3",
        "status": 1,
        "apiVersion": 1
    }]
    
    with open("plugins-minimal.json", "w", encoding="utf-8") as f:
        json.dump(minimal, f, indent=2, ensure_ascii=False)
    log_success("plugins-minimal.json atualizado")

def create_github_release(version, file_size, file_hash):
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    release_body = f"""MaxSeries v{version} - PlayerEmbedAPI Otimizado

Novidades:
- PlayerEmbedAPI V8 (Pure HTTP) agora e tentado PRIMEIRO (~50-100ms)
- PlayerEmbedAPI V7 (WebView) usado como FALLBACK com timeout de 25s
- Carregamento de videos muito mais rapido e confiavel

Correcoes:
- Fix: Timeout do V7 causando exception null
- Fix: Carregamento lento quando V7 era tentado primeiro  
- Otimizacao do fluxo de extracao

Performance:
- V8 (Pure HTTP): ~50-100ms (Principal)
- V7 (WebView): Ate 25s (Fallback)

Arquivos:
- MaxSeries.cs3: {file_size / 1024:.2f} KB
- SHA256: {file_hash}

Instalacao:
1. Baixe o arquivo MaxSeries.cs3
2. Abra o Cloudstream3
3. Configuracoes -> Extensoes -> Instalar de arquivo
4. Selecione o arquivo baixado

Ou use o repo:
https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/main/repo.json
"""
    
    log_info("Criando release no GitHub...")
    release_data = {
        "tag_name": f"v{version}",
        "target_commitish": "main",
        "name": f"MaxSeries v{version}",
        "body": release_body,
        "draft": False,
        "prerelease": False
    }
    
    response = requests.post(
        f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases",
        headers=headers,
        json=release_data
    )
    
    if response.status_code != 201:
        log_error(f"Falha ao criar release: {response.text}")
        return False
    
    release_info = response.json()
    release_id = release_info["id"]
    log_success(f"Release criada: {release_info['html_url']}")
    
    log_info("Fazendo upload de MaxSeries.cs3...")
    
    upload_url = f"https://uploads.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/{release_id}/assets?name=MaxSeries.cs3"
    
    with open("MaxSeries.cs3", "rb") as f:
        file_content = f.read()
    
    upload_headers = headers.copy()
    upload_headers["Content-Type"] = "application/octet-stream"
    
    upload_response = requests.post(
        upload_url,
        headers=upload_headers,
        data=file_content
    )
    
    if upload_response.status_code != 201:
        log_error(f"Falha no upload: {upload_response.text}")
        return False
    
    log_success(f"Upload concluido: {upload_response.json()['browser_download_url']}")
    return True

def main():
    log_step("MaxSeries Release Automatizado v263")
    
    if not GITHUB_TOKEN:
        log_error("GITHUB_TOKEN nao definido!")
        print("Defina com: set GITHUB_TOKEN=seu_token")
        sys.exit(1)
    
    log_success("GITHUB_TOKEN definido")
    
    cs3_path = Path("MaxSeries.cs3")
    if not cs3_path.exists():
        log_error("MaxSeries.cs3 nao encontrado!")
        sys.exit(1)
    
    file_size = cs3_path.stat().st_size
    log_success(f"Arquivo encontrado: {file_size / 1024:.2f} KB")
    
    log_step("Calculando Hash SHA256")
    file_hash = calculate_sha256(cs3_path)
    log_info(f"SHA256: {file_hash}")
    
    log_step("Atualizando Arquivos JSON")
    update_jsons(VERSION, file_size, file_hash)
    
    log_step("Criando Release no GitHub")
    if not create_github_release(VERSION, file_size, file_hash):
        sys.exit(1)
    
    log_step("Release v263 Concluido!")
    print(f"\nResumo:")
    print(f"   Versao: v{VERSION}")
    print(f"   Arquivo: MaxSeries.cs3 ({file_size / 1024:.2f} KB)")
    print(f"   SHA256: {file_hash}")
    print(f"\nTudo automatizado com sucesso!")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
