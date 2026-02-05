#!/usr/bin/env python3
"""
Build system para plugins CloudStream3
Gera arquivos .cs3 a partir dos AARs de build
"""

import os
import json
import subprocess
import shutil

def run_build():
    """Executa o build do Gradle"""
    print("=== BUILD PLUGINS CLOUDSTREAM3 ===\n")
    
    # Limpar builds antigos
    print("Limpando builds antigos...")
    providers = ["MaxSeries", "AnimesOnlineCC", "Vizer", "NetCine", "MegaFlix", "PobreFlix", "OverFlix"]
    
    for provider in providers:
        build_dir = f"{provider}/build"
        if os.path.exists(build_dir):
            shutil.rmtree(build_dir)
            print(f"  Limpado: {provider}")
    
    # Executar build
    print("\nExecutando build...")
    result = subprocess.run(
        ["./gradlew", "assembleRelease", "-x", "test", "--no-daemon"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"ERRO no build:\n{result.stderr}")
        return False
    
    print("Build concluído!")
    return True

def copy_aar_to_cs3():
    """Copia AARs para CS3"""
    print("\n=== GERANDO ARQUIVOS .CS3 ===")
    
    providers = {
        "MaxSeries": {"version": 264, "tvTypes": ["TvSeries", "Movie"]},
        "AnimesOnlineCC": {"version": 10, "tvTypes": ["Anime"]},
        "Vizer": {"version": 2, "tvTypes": ["TvSeries", "Movie"]},
        "NetCine": {"version": 2, "tvTypes": ["TvSeries", "Movie"]},
        "MegaFlix": {"version": 2, "tvTypes": ["TvSeries", "Movie"]},
        "PobreFlix": {"version": 2, "tvTypes": ["TvSeries", "Movie"]},
        "OverFlix": {"version": 2, "tvTypes": ["TvSeries", "Movie"]},
    }
    
    plugins = []
    
    for provider, info in providers.items():
        aar_release = f"{provider}/build/outputs/aar/{provider}-release.aar"
        aar_debug = f"{provider}/build/outputs/aar/{provider}-debug.aar"
        cs3_file = f"{provider}.cs3"
        
        # Preferir release, mas usar debug se não existir
        if os.path.exists(aar_release):
            shutil.copy(aar_release, cs3_file)
            print(f"  ✓ {provider}.cs3 (release)")
        elif os.path.exists(aar_debug):
            shutil.copy(aar_debug, cs3_file)
            print(f"  ✓ {provider}.cs3 (debug)")
        else:
            print(f"  ✗ {provider} - AAR não encontrado")
            continue
        
        # Obter tamanho
        size = os.path.getsize(cs3_file)
        
        # Criar entrada do plugin
        plugin = {
            "url": f"https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/{cs3_file}",
            "status": 1,
            "version": info["version"],
            "apiVersion": 1,
            "name": provider,
            "internalName": provider,
            "authors": ["franciscoalro"],
            "description": f"{provider} v{info['version']}",
            "repositoryUrl": "https://github.com/franciscoalro/TestPlugins",
            "tvTypes": info["tvTypes"],
            "language": "pt-BR",
            "fileSize": size
        }
        plugins.append(plugin)
    
    return plugins

def update_json_files(plugins):
    """Atualiza plugins.json e repo.json"""
    print("\n=== ATUALIZANDO JSONS ===")
    
    # plugins.json
    with open("plugins.json", "wb") as f:
        f.write(json.dumps(plugins, indent=2, ensure_ascii=False).encode("utf-8"))
        f.write(b"\n")
    print("  ✓ plugins.json")
    
    # repo.json
    repo = {
        "name": "Franciscoalro Plugins",
        "description": "Repositorio de plugins para CloudStream3",
        "manifestVersion": 1,
        "pluginLists": [
            "https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/plugins.json"
        ]
    }
    
    with open("repo.json", "wb") as f:
        f.write(json.dumps(repo, indent=2, ensure_ascii=False).encode("utf-8"))
        f.write(b"\n")
    print("  ✓ repo.json")

def verify_files():
    """Verifica se os arquivos estão corretos"""
    print("\n=== VERIFICAÇÃO ===")
    
    # Verificar plugins.json
    with open("plugins.json", "rb") as f:
        data = f.read()
        if data[0:3] == b"\xef\xbb\xbf":
            print("  ✗ plugins.json tem BOM!")
        else:
            print("  ✓ plugins.json sem BOM")
        
        plugins = json.loads(data.decode("utf-8"))
        if isinstance(plugins, list):
            print(f"  ✓ plugins.json é array com {len(plugins)} plugins")
        else:
            print("  ✗ plugins.json não é array!")
    
    # Verificar CS3
    with open("MaxSeries.cs3", "rb") as f:
        header = f.read(4)
        if header[:2] == b"PK":
            print("  ✓ MaxSeries.cs3 é ZIP válido (AAR)")
        else:
            print(f"  ✗ MaxSeries.cs3 não é ZIP. Header: {header.hex()}")

def main():
    # Build
    if not run_build():
        return 1
    
    # Gerar CS3
    plugins = copy_aar_to_cs3()
    
    # Atualizar JSONs
    update_json_files(plugins)
    
    # Verificar
    verify_files()
    
    print("\n=== BUILD CONCLUÍDO ===")
    print(f"Total de plugins: {len(plugins)}")
    print("\nPara instalar no CloudStream3:")
    print("  https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/repo.json")
    
    return 0

if __name__ == "__main__":
    exit(main())
