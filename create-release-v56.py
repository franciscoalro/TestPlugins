#!/usr/bin/env python3
"""
Criar GitHub Release v56.0 automaticamente
"""

import requests
import json
import subprocess
import os

def create_github_release():
    print("🚀 Criando GitHub Release v56.0 automaticamente")
    print("=" * 60)
    
    # Verificar se o arquivo existe
    if not os.path.exists("MaxSeries.cs3"):
        print("❌ Arquivo MaxSeries.cs3 não encontrado!")
        return False
    
    file_size = os.path.getsize("MaxSeries.cs3")
    print(f"📦 Arquivo MaxSeries.cs3: {file_size} bytes")
    
    # Configurações
    owner = "franciscoalro"
    repo = "TestPlugins"
    tag = "v56.0"
    name = "MaxSeries v56 - Critical AnimesOnlineCC Fixes"
    
    # Corpo da release
    body = """## 🔧 MaxSeries v56 - Critical AnimesOnlineCC Fixes

### ✅ CORREÇÕES CRÍTICAS APLICADAS:
- **Tratamento de erro robusto**: Try/catch em todas as funções principais
- **Logs detalhados**: Log.d() ao invés de println() para debug no Android
- **Busca de imagem robusta**: Suporte a src, data-src, data-lazy-src, data-original
- **URLs consistentes**: Uso de fixUrl() e fixUrlNull() em todos os lugares
- **Melhor busca de elementos**: Seletores mais robustos para título e poster
- **Suporte híbrido**: Funciona com formato MaxSeries e AnimesOnlineCC de episódios

### 🎯 BASEADO NO ANIMESONLINECC FUNCIONANDO:
- Estrutura de error handling idêntica ao AnimesOnlineCC
- Padrões de busca de elementos similares
- Logs detalhados para facilitar troubleshooting
- Tratamento robusto de URLs e imagens

### 📱 DEVE RESOLVER:
- **Problema principal**: Conteúdo não aparecendo no CloudStream app
- **Logs vazios**: Agora com logs detalhados para debug
- **Imagens quebradas**: Busca robusta em múltiplos atributos
- **URLs malformadas**: fixUrl() consistente

### 🔍 TESTE AUTOMATIZADO:
```
🌐 Site: https://www.maxseries.one ✅ (Status: 200)
🔍 Seletor 'div.items article.item': ✅ (36 itens encontrados)
🎬 Página de filmes: ✅ (1 filme encontrado)
📺 Página de séries: ✅ (42 séries encontradas)
🔍 Pesquisa: ✅ (funcional)
```

**Site**: https://www.maxseries.one/
**Filtro YouTube**: ✅ Ativo
**Extractors**: DoodStream, MegaEmbed, PlayerEmbedAPI"""
    
    try:
        # Obter SHA do commit atual
        result = subprocess.run(['git', 'rev-parse', 'HEAD'], 
                              capture_output=True, text=True, check=True)
        commit_sha = result.stdout.strip()
        print(f"📝 Commit SHA: {commit_sha}")
        
        # Primeiro, criar a tag
        print("🏷️ Criando tag...")
        try:
            subprocess.run(['git', 'tag', '-a', tag, '-m', name], check=True)
            subprocess.run(['git', 'push', 'origin', tag], check=True)
            print(f"✅ Tag {tag} criada e enviada!")
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Tag pode já existir: {e}")
        
        # Dados da release
        release_data = {
            "tag_name": tag,
            "target_commitish": commit_sha,
            "name": name,
            "body": body,
            "draft": False,
            "prerelease": False
        }
        
        # URL da API
        api_url = f"https://api.github.com/repos/{owner}/{repo}/releases"
        
        print("🌐 Tentando criar release via API...")
        
        # Headers básicos
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Python-Release-Creator"
        }
        
        # Tentar criar release
        response = requests.post(api_url, json=release_data, headers=headers)
        
        if response.status_code == 201:
            release_info = response.json()
            print("✅ Release criado com sucesso!")
            print(f"🔗 URL: {release_info['html_url']}")
            
            # Upload do arquivo
            upload_url = release_info['upload_url'].replace('{?name,label}', f'?name=MaxSeries.cs3')
            
            print("📤 Fazendo upload do MaxSeries.cs3...")
            
            with open('MaxSeries.cs3', 'rb') as f:
                file_data = f.read()
            
            upload_headers = {
                "Accept": "application/vnd.github.v3+json",
                "Content-Type": "application/octet-stream"
            }
            
            upload_response = requests.post(upload_url, data=file_data, headers=upload_headers)
            
            if upload_response.status_code == 201:
                asset_info = upload_response.json()
                print("✅ Arquivo MaxSeries.cs3 enviado com sucesso!")
                print(f"📥 Download URL: {asset_info['browser_download_url']}")
                return True
            else:
                print(f"❌ Erro no upload: {upload_response.status_code}")
                print(f"📋 Resposta: {upload_response.text}")
                
        elif response.status_code == 422:
            print("⚠️ Release já existe ou erro de validação")
            print(f"📋 Resposta: {response.text}")
            
            # Tentar obter release existente
            get_url = f"https://api.github.com/repos/{owner}/{repo}/releases/tags/{tag}"
            get_response = requests.get(get_url, headers=headers)
            
            if get_response.status_code == 200:
                existing_release = get_response.json()
                print(f"✅ Release {tag} já existe!")
                print(f"🔗 URL: {existing_release['html_url']}")
                return True
                
        else:
            print(f"❌ Erro na API: {response.status_code}")
            print(f"📋 Resposta: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # Fallback: instruções manuais
    print("\n🔄 Método alternativo - Instruções manuais:")
    print(f"1. Acesse: https://github.com/{owner}/{repo}/releases/new")
    print(f"2. Tag: {tag}")
    print(f"3. Título: {name}")
    print("4. Faça upload do arquivo MaxSeries.cs3")
    print("5. Copie a descrição do arquivo CREATE_GITHUB_RELEASE_V56.md")
    
    return False

if __name__ == "__main__":
    success = create_github_release()
    
    print("\n🎯 VERIFICAÇÃO FINAL:")
    print("1. Acesse: https://github.com/franciscoalro/TestPlugins/releases")
    print("2. Verifique se o release v56.0 foi criado")
    print("3. Confirme se o arquivo MaxSeries.cs3 está disponível")
    print("4. Teste no CloudStream app")
    
    if success:
        print("\n✅ Release v56.0 criado com sucesso!")
    else:
        print("\n⚠️ Pode ser necessário criar o release manualmente")