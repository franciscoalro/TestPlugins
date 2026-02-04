#!/usr/bin/env python3
"""
Script de deploy do MaxSeries.cs3 para nuvem e atualizacao do repositorio
"""

import os
import sys
import json
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

# Configuracoes
PLUGIN_FILE = "MaxSeries/build/MaxSeries.cs3"
VERSION = "v260"
REPO_JSON_FILES = [
    "plugins.json",
    "repo.json", 
    "CloudstreamRepo/plugins.json"
]

def check_plugin_exists():
    """Verifica se o plugin foi compilado"""
    if not os.path.exists(PLUGIN_FILE):
        print("ERRO: Plugin nao encontrado!")
        print("Execute primeiro: cd MaxSeries && ../gradlew make")
        return False
    
    size = os.path.getsize(PLUGIN_FILE)
    print(f"OK: Plugin encontrado: {PLUGIN_FILE}")
    print(f"Tamanho: {size / 1024:.2f} KB")
    return True

def upload_to_transfer_sh():
    """Faz upload para transfer.sh"""
    print("\nFazendo upload para transfer.sh...")
    
    try:
        import requests
        
        with open(PLUGIN_FILE, 'rb') as f:
            response = requests.put(
                f"https://transfer.sh/MaxSeries_{VERSION}.cs3",
                data=f,
                headers={'Content-Type': 'application/octet-stream'}
            )
        
        if response.status_code == 200:
            url = response.text.strip()
            print(f"Upload concluido!")
            print(f"URL: {url}")
            return url
        else:
            print(f"Erro no upload: {response.status_code}")
            return None
            
    except ImportError:
        print("requests nao instalado. Tentando com curl...")
        return upload_with_curl()
    except Exception as e:
        print(f"Erro: {e}")
        return None

def upload_with_curl():
    """Faz upload usando curl"""
    try:
        result = subprocess.run(
            ["curl", "--progress-bar", "--upload-file", PLUGIN_FILE, 
             f"https://transfer.sh/MaxSeries_{VERSION}.cs3"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            url = result.stdout.strip()
            print(f"Upload concluido!")
            print(f"URL: {url}")
            return url
        else:
            print(f"Erro no upload: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"Erro: {e}")
        return None

def update_repo_json(url):
    """Atualiza os arquivos JSON do repositorio"""
    print(f"\nAtualizando repositorios...")
    
    updated = []
    
    for json_file in REPO_JSON_FILES:
        if not os.path.exists(json_file):
            print(f"Arquivo nao encontrado: {json_file}")
            continue
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Procurar e atualizar MaxSeries
            found = False
            
            if 'plugins' in data:
                for plugin in data['plugins']:
                    if plugin.get('name') == 'MaxSeries':
                        plugin['url'] = url
                        plugin['version'] = VERSION
                        plugin['lastUpdated'] = datetime.utcnow().isoformat() + 'Z'
                        found = True
                        break
                
                if not found:
                    # Adicionar novo
                    data['plugins'].append({
                        'name': 'MaxSeries',
                        'url': url,
                        'version': VERSION,
                        'lastUpdated': datetime.utcnow().isoformat() + 'Z',
                        'status': 1,
                        'description': 'MaxSeries Provider com AES, CDN e Session Manager'
                    })
            
            # Salvar
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"Atualizado: {json_file}")
            updated.append(json_file)
            
        except Exception as e:
            print(f"Erro ao atualizar {json_file}: {e}")
    
    return updated

def copy_to_cloudstream_repo():
    """Copia o plugin para o diretorio CloudstreamRepo"""
    target_dir = "CloudstreamRepo"
    
    if not os.path.exists(target_dir):
        print(f"Diretorio {target_dir} nao existe")
        return False
    
    target_file = os.path.join(target_dir, "MaxSeries.cs3")
    
    try:
        shutil.copy2(PLUGIN_FILE, target_file)
        print(f"Copiado para: {target_file}")
        return True
    except Exception as e:
        print(f"Erro ao copiar: {e}")
        return False

def main():
    print("=" * 60)
    print("DEPLOY DO MAXSERIES PLUGIN")
    print("=" * 60)
    
    # 1. Verificar plugin
    if not check_plugin_exists():
        sys.exit(1)
    
    # 2. Copiar para CloudstreamRepo
    copy_to_cloudstream_repo()
    
    # 3. Perguntar metodo de upload
    print("\nOpcoes de upload:")
    print("1. transfer.sh (temporario, 14 dias)")
    print("2. Copiar apenas para CloudstreamRepo/")
    print("3. Cancelar")
    
    choice = input("\nEscolha (1-3): ").strip()
    
    if choice == '1':
        url = upload_to_transfer_sh()
        if url:
            # Atualizar JSONs
            updated = update_repo_json(url)
            
            print("\n" + "=" * 60)
            print("DEPLOY CONCLUIDO!")
            print("=" * 60)
            print(f"\nPlugin: MaxSeries {VERSION}")
            print(f"URL: {url}")
            print(f"\nRepositorios atualizados:")
            for f in updated:
                print(f"   - {f}")
            print("\nIMPORTANTE: A URL do transfer.sh expira em 14 dias!")
            print("   Para deploy permanente, use GitHub Releases ou Netlify.")
        else:
            print("\nDeploy falhou!")
            sys.exit(1)
            
    elif choice == '2':
        print("\nPlugin copiado para CloudstreamRepo/MaxSeries.cs3")
        print("\nVoce pode hospedar esse arquivo em:")
        print("- GitHub Pages")
        print("- Netlify")
        print("- Qualquer servidor HTTP")
        
    elif choice == '3':
        print("\nCancelado")
        sys.exit(0)
    else:
        print("\nOpcao invalida")
        sys.exit(1)

if __name__ == "__main__":
    main()
