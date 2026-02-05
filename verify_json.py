#!/usr/bin/env python3
import json
import urllib.request

print("=== VERIFICANDO JSON NO GITHUB ===")

# Baixar plugins.json
url = "https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/plugins.json"
try:
    with urllib.request.urlopen(url) as response:
        data = response.read()
        
        # Verificar primeiro byte
        print(f"\nPrimeiro byte: 0x{data[0]:02X}")
        
        # Se tiver BOM, remover
        if data[0:3] == b'\xef\xbb\xbf':
            print("AVISO: Arquivo tem BOM!")
            data = data[3:]
        else:
            print("OK: Sem BOM")
        
        # Parse JSON
        plugins = json.loads(data.decode('utf-8'))
        
        if isinstance(plugins, list):
            print(f"\nOK: É uma LISTA com {len(plugins)} plugins!")
            for plugin in plugins:
                print(f"  - {plugin['name']} v{plugin['version']}")
        else:
            print("\nERRO: Não é uma lista!")
            
except Exception as e:
    print(f"Erro: {e}")

# Verificar repo.json
print("\n=== REPO.JSON ===")
url = "https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/repo.json"
try:
    with urllib.request.urlopen(url) as response:
        data = response.read()
        
        if data[0:3] == b'\xef\xbb\xbf':
            data = data[3:]
            
        repo = json.loads(data.decode('utf-8'))
        print(f"Nome: {repo['name']}")
        print(f"Manifest Version: {repo['manifestVersion']}")
        print(f"Plugin Lists: {repo['pluginLists']}")
        print("\nOK: repo.json válido!")
except Exception as e:
    print(f"Erro: {e}")
