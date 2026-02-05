#!/usr/bin/env python3
"""
Diagnostico completo do plugin CloudStream
"""

import zipfile
import json
import os
import sys

def check_cs3_file(filepath):
    """Verifica se o arquivo CS3 esta valido"""
    print(f"\n=== Verificando {filepath} ===")
    
    if not os.path.exists(filepath):
        print(f"[ERRO] Arquivo nao encontrado: {filepath}")
        return False
    
    file_size = os.path.getsize(filepath)
    print(f"[OK] Arquivo existe: {file_size} bytes")
    
    try:
        with zipfile.ZipFile(filepath, 'r') as zf:
            files = zf.namelist()
            print(f"[OK] E um arquivo ZIP valido")
            print(f"[OK] Total de entradas: {len(files)}")
            
            # Verificar estrutura AAR
            required_files = ['AndroidManifest.xml', 'classes.jar']
            for req in required_files:
                if req in files:
                    print(f"[OK] Contem {req}")
                else:
                    print(f"[ERRO] Nao contem {req}")
                    return False
            
            # Verificar classes.jar
            import io
            classes_jar_data = zf.read('classes.jar')
            with zipfile.ZipFile(io.BytesIO(classes_jar_data), 'r') as classes_zf:
                class_files = classes_zf.namelist()
                print(f"[OK] classes.jar contem {len(class_files)} arquivos")
                
                # Procurar por classes principais
                main_plugin = [f for f in class_files if 'Plugin.class' in f and '$' not in f]
                main_provider = [f for f in class_files if 'Provider.class' in f and '$' not in f]
                
                if main_plugin:
                    print(f"[OK] Plugin principal encontrado: {main_plugin[0]}")
                else:
                    print(f"[ERRO] Plugin principal nao encontrado")
                    return False
                
                if main_provider:
                    print(f"[OK] Provider encontrado: {main_provider[0]}")
                else:
                    print(f"[ERRO] Provider nao encontrado")
                    return False
                
                # Verificar anotacao CloudStream
                cloudstream_files = [f for f in class_files if 'Cloudstream' in f or 'cloudstream' in f.lower()]
                if cloudstream_files:
                    print(f"[OK] Referencias CloudStream: {len(cloudstream_files)}")
                
        print(f"\n[OK] Arquivo {filepath} esta VALIDO!")
        return True
        
    except zipfile.BadZipFile:
        print(f"[ERRO] Arquivo nao e um ZIP valido")
        return False
    except Exception as e:
        print(f"[ERRO] Erro ao verificar arquivo: {e}")
        return False

def check_plugins_json(filepath):
    """Verifica se o plugins.json esta valido"""
    print(f"\n=== Verificando {filepath} ===")
    
    if not os.path.exists(filepath):
        print(f"[ERRO] Arquivo nao encontrado: {filepath}")
        return False
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"[OK] JSON valido")
        
        if not isinstance(data, list):
            print(f"[ERRO] JSON deve ser uma lista")
            return False
        
        print(f"[OK] Contem {len(data)} plugin(s)")
        
        for i, plugin in enumerate(data):
            print(f"\n  Plugin {i+1}:")
            
            required_fields = ['name', 'url', 'version', 'status', 'internalName']
            for field in required_fields:
                if field in plugin:
                    print(f"    [OK] {field}: {plugin.get(field)}")
                else:
                    print(f"    [ERRO] Campo obrigatorio ausente: {field}")
                    return False
            
            # Verificar se o arquivo existe
            plugin_url = plugin.get('url', '')
            if plugin_url.endswith('.cs3'):
                local_file = os.path.basename(plugin_url)
                if os.path.exists(local_file):
                    actual_size = os.path.getsize(local_file)
                    json_size = plugin.get('fileSize', 0)
                    if actual_size == json_size:
                        print(f"    [OK] fileSize corresponde: {actual_size} bytes")
                    else:
                        print(f"    [AVISO] fileSize diferente: JSON={json_size}, Real={actual_size}")
        
        print(f"\n[OK] {filepath} esta VALIDO!")
        return True
        
    except json.JSONDecodeError as e:
        print(f"[ERRO] JSON invalido: {e}")
        return False
    except Exception as e:
        print(f"[ERRO] Erro: {e}")
        return False

def check_repo_json(filepath):
    """Verifica se o repo.json esta valido"""
    print(f"\n=== Verificando {filepath} ===")
    
    if not os.path.exists(filepath):
        print(f"[ERRO] Arquivo nao encontrado: {filepath}")
        return False
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"[OK] JSON valido")
        
        required_fields = ['name', 'manifestVersion', 'pluginLists']
        for field in required_fields:
            if field in data:
                print(f"[OK] {field}: {data.get(field)}")
            else:
                print(f"[ERRO] Campo obrigatorio ausente: {field}")
                return False
        
        if not isinstance(data.get('pluginLists'), list):
            print(f"[ERRO] pluginLists deve ser uma lista")
            return False
        
        print(f"\n[OK] {filepath} esta VALIDO!")
        return True
        
    except json.JSONDecodeError as e:
        print(f"[ERRO] JSON invalido: {e}")
        return False
    except Exception as e:
        print(f"[ERRO] Erro: {e}")
        return False

def main():
    print("="*60)
    print("DIAGNOSTICO DO PLUGIN CLOUDSTREAM")
    print("="*60)
    
    results = []
    
    # Verificar arquivos
    results.append(('MaxSeries.cs3', check_cs3_file('MaxSeries.cs3')))
    results.append(('plugins.json', check_plugins_json('plugins.json')))
    results.append(('repo.json', check_repo_json('repo.json')))
    
    # Resumo
    print("\n" + "="*60)
    print("RESUMO")
    print("="*60)
    
    all_passed = True
    for name, passed in results:
        status = "[OK] PASSOU" if passed else "[ERRO] FALHOU"
        print(f"{status}: {name}")
        if not passed:
            all_passed = False
    
    print("\n" + "="*60)
    if all_passed:
        print("[OK] TODOS OS ARQUIVOS ESTAO VALIDOS!")
        print("\nSe o plugin nao aparece no CloudStream, verifique:")
        print("1. A URL do repositorio esta correta:")
        print("   https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/repo.json")
        print("2. O CloudStream tem permissao de internet")
        print("3. Tente remover e adicionar o repositorio novamente")
        print("4. Limpe o cache do CloudStream")
        print("5. Reinicie o aplicativo CloudStream")
    else:
        print("[ERRO] ALGUNS ARQUIVOS ESTAO INVALIDOS!")
        print("Corrija os problemas acima e tente novamente.")
    print("="*60)
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())
