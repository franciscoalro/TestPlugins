#!/usr/bin/env python3
import urllib.request
import json

print("=== Verificando arquivos no GitHub ===\n")

# Verificar repo.json
url = 'https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/repo.json'
print("repo.json:")
try:
    with urllib.request.urlopen(url) as response:
        data = response.read()
        repo = json.loads(data.decode('utf-8'))
        print(f"  name: {repo['name']}")
        print(f"  manifestVersion: {repo['manifestVersion']}")
        print(f"  pluginLists: {repo['pluginLists']}")
        print("  OK\n")
except Exception as e:
    print(f"  ERRO: {e}\n")

# Verificar plugins.json
url = 'https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/plugins.json'
print("plugins.json:")
try:
    with urllib.request.urlopen(url) as response:
        data = response.read()
        print(f"  Primeiro byte: 0x{data[0]:02X}")
        
        if data[0:3] == b'\xef\xbb\xbf':
            print("  AVISO: TEM BOM!")
            data = data[3:]
        else:
            print("  OK: Sem BOM")
        
        plugins = json.loads(data.decode('utf-8'))
        print(f"  Tipo: {type(plugins).__name__}")
        
        if isinstance(plugins, list):
            print(f"  OK: Lista com {len(plugins)} plugins")
            for plugin in plugins:
                print(f"    - {plugin['name']} v{plugin['version']} ({plugin['fileSize']} bytes)")
        else:
            print(f"  ERRO: Nao e lista!")
        print()
except Exception as e:
    print(f"  ERRO: {e}\n")

# Verificar MaxSeries.cs3
url = 'https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/MaxSeries.cs3'
print("MaxSeries.cs3:")
try:
    with urllib.request.urlopen(url) as response:
        data = response.read()
        print(f"  Tamanho: {len(data)} bytes")
        
        # Verificar se é ZIP
        if data[0:2] == b'PK':
            print(f"  OK: ZIP valido (AAR/CS3)")
        else:
            print(f"  ERRO: Nao e ZIP. Header: {data[0:4].hex()}")
        print()
except Exception as e:
    print(f"  ERRO: {e}\n")

print("=== Verificacao concluida ===")
