import json
import hashlib
import requests
from urllib.parse import urlparse

def test_cloudstream_compatibility():
    """Simula o comportamento do CloudStream para diagnosticar problemas"""
    
    print("=" * 60)
    print("TESTE DE COMPATIBILIDADE CLOUDSTREAM")
    print("=" * 60)
    
    # 1. Baixar plugins.json
    print("\n[1] Baixando plugins.json...")
    repo_url = "https://raw.githubusercontent.com/franciscoalro/CloudstreamRepo/main/plugins.json"
    
    try:
        response = requests.get(repo_url, headers={"Cache-Control": "no-cache"})
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('Content-Type')}")
        print(f"   Size: {len(response.content)} bytes")
        
        if response.status_code != 200:
            print(f"   ❌ ERRO: Status code {response.status_code}")
            return
            
    except Exception as e:
        print(f"   ❌ ERRO ao baixar: {e}")
        return
    
    # 2. Parsear JSON
    print("\n[2] Parseando JSON...")
    try:
        plugins = json.loads(response.text)
        print(f"   ✅ JSON válido")
        print(f"   Plugins encontrados: {len(plugins)}")
    except json.JSONDecodeError as e:
        print(f"   ❌ ERRO de parsing: {e}")
        print(f"   Primeiros 200 chars: {response.text[:200]}")
        return
    
    # 3. Validar schema do MaxSeries
    print("\n[3] Validando schema do MaxSeries...")
    maxseries = None
    for plugin in plugins:
        if plugin.get("name") == "MaxSeries":
            maxseries = plugin
            break
    
    if not maxseries:
        print("   ❌ ERRO: MaxSeries não encontrado")
        return
    
    required_fields = ["name", "version", "url", "fileSize"]
    missing_fields = [f for f in required_fields if f not in maxseries]
    
    if missing_fields:
        print(f"   ❌ ERRO: Campos obrigatórios faltando: {missing_fields}")
        return
    
    print(f"   ✅ Schema válido")
    print(f"   Version: {maxseries['version']}")
    print(f"   FileSize: {maxseries['fileSize']}")
    print(f"   URL: {maxseries['url']}")
    if "fileHash" in maxseries:
        print(f"   FileHash: {maxseries['fileHash'][:16]}...")
    
    # 4. Testar download do .cs3
    print("\n[4] Testando download do .cs3...")
    cs3_url = maxseries["url"]
    
    try:
        head_response = requests.head(cs3_url, allow_redirects=True)
        print(f"   Status: {head_response.status_code}")
        print(f"   Content-Length: {head_response.headers.get('Content-Length')}")
        print(f"   Content-Type: {head_response.headers.get('Content-Type')}")
        
        if head_response.status_code != 200:
            print(f"   ❌ ERRO: Arquivo não acessível (status {head_response.status_code})")
            return
            
    except Exception as e:
        print(f"   ❌ ERRO ao acessar arquivo: {e}")
        return
    
    # 5. Verificar tamanho do arquivo
    print("\n[5] Verificando tamanho do arquivo...")
    expected_size = maxseries["fileSize"]
    actual_size = int(head_response.headers.get('Content-Length', 0))
    
    if actual_size != expected_size:
        print(f"   ⚠️ AVISO: Tamanho diferente!")
        print(f"   Esperado: {expected_size} bytes")
        print(f"   Real: {actual_size} bytes")
    else:
        print(f"   ✅ Tamanho correto: {actual_size} bytes")
    
    # 6. Verificar hash SHA256 (se disponível)
    if "fileHash" in maxseries:
        print("\n[6] Verificando hash SHA256...")
        print("   Baixando arquivo para verificar hash...")
        
        try:
            download_response = requests.get(cs3_url, stream=True)
            sha256_hash = hashlib.sha256()
            
            for chunk in download_response.iter_content(chunk_size=8192):
                sha256_hash.update(chunk)
            
            calculated_hash = sha256_hash.hexdigest().upper()
            expected_hash = maxseries["fileHash"].upper()
            
            print(f"   Esperado: {expected_hash}")
            print(f"   Calculado: {calculated_hash}")
            
            if calculated_hash == expected_hash:
                print(f"   ✅ Hash correto!")
            else:
                print(f"   ❌ ERRO: Hash não corresponde!")
                return
                
        except Exception as e:
            print(f"   ❌ ERRO ao verificar hash: {e}")
            return
    
    # 7. Verificar campos específicos do CloudStream
    print("\n[7] Verificando campos específicos do CloudStream...")
    cloudstream_fields = {
        "internalName": maxseries.get("internalName"),
        "description": maxseries.get("description"),
        "authors": maxseries.get("authors"),
        "repositoryUrl": maxseries.get("repositoryUrl"),
        "status": maxseries.get("status"),
        "language": maxseries.get("language"),
        "tvTypes": maxseries.get("tvTypes"),
        "iconUrl": maxseries.get("iconUrl"),
        "apiVersion": maxseries.get("apiVersion"),
        "isAdult": maxseries.get("isAdult")
    }
    
    for field, value in cloudstream_fields.items():
        if value is None:
            print(f"   ⚠️ Campo opcional ausente: {field}")
        else:
            print(f"   ✅ {field}: {value if not isinstance(value, (list, dict)) else type(value).__name__}")
    
    print("\n" + "=" * 60)
    print("✅ TODOS OS TESTES PASSARAM!")
    print("=" * 60)
    print("\nSe o CloudStream ainda não consegue baixar, o problema pode ser:")
    print("1. Cache do app (limpar cache do CloudStream)")
    print("2. Versão antiga do CloudStream (atualizar app)")
    print("3. Problema de rede/firewall")
    print("4. URL do repositório incorreta no app")

if __name__ == "__main__":
    test_cloudstream_compatibility()
