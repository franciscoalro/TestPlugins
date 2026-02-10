#!/usr/bin/env python3

"""
Script para testar diferentes endpoints da API PlayerEmbed
"""

import requests
import json

def test_endpoint(url, description):
    """Testa um endpoint específico"""
    print(f"\n🔍 Testando: {description}")
    print(f"   URL: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   ✅ Resposta JSON recebida!")
                print(f"   📄 Dados:")
                print(json.dumps(data, indent=2, ensure_ascii=False)[:500])
                
                # Verificar se tem os campos que procuramos
                if isinstance(data, dict):
                    if 'user_id' in data and 'slug' in data and 'md5_id' in data:
                        print(f"\n   🎯 ENCONTRADO! Este endpoint tem os dados necessários!")
                        return data
                
                return data
            except json.JSONDecodeError:
                print(f"   ⚠️  Resposta não é JSON")
                print(f"   Content: {response.text[:200]}")
        else:
            print(f"   ❌ Erro: {response.status_code}")
            if response.text:
                print(f"   Message: {response.text[:200]}")
    
    except requests.exceptions.Timeout:
        print(f"   ❌ Timeout")
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Erro de conexão")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    return None

def main():
    print("╔════════════════════════════════════════════════════════════╗")
    print("║  🌐 Teste de Endpoints da API PlayerEmbed                ║")
    print("╚════════════════════════════════════════════════════════════╝")
    
    video_id = "kBJLtxCD3"
    base_url = "https://playerembedapi.link"
    
    # Lista de endpoints possíveis
    endpoints = [
        (f"{base_url}/api/media?v={video_id}", "API Media (query param)"),
        (f"{base_url}/api/media/{video_id}", "API Media (path param)"),
        (f"{base_url}/api/video?v={video_id}", "API Video (query param)"),
        (f"{base_url}/api/video/{video_id}", "API Video (path param)"),
        (f"{base_url}/api/player?v={video_id}", "API Player (query param)"),
        (f"{base_url}/api/player/{video_id}", "API Player (path param)"),
        (f"{base_url}/api/embed?v={video_id}", "API Embed (query param)"),
        (f"{base_url}/api/embed/{video_id}", "API Embed (path param)"),
        (f"{base_url}/api/v1/media?v={video_id}", "API v1 Media"),
        (f"{base_url}/api/v2/media?v={video_id}", "API v2 Media"),
        (f"{base_url}/media/{video_id}", "Media direto"),
        (f"{base_url}/video/{video_id}", "Video direto"),
    ]
    
    print(f"\n📊 Testando {len(endpoints)} endpoints possíveis...")
    print(f"🎬 Vídeo: {video_id}")
    
    results = []
    for url, description in endpoints:
        result = test_endpoint(url, description)
        if result:
            results.append({
                'url': url,
                'description': description,
                'data': result
            })
    
    print("\n" + "="*60)
    print("📊 RESUMO DOS RESULTADOS")
    print("="*60)
    
    if results:
        print(f"\n✅ Encontrados {len(results)} endpoints funcionando:\n")
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['description']}")
            print(f"   URL: {result['url']}")
            
            # Verificar se tem os campos necessários
            data = result['data']
            if isinstance(data, dict):
                has_user_id = 'user_id' in data
                has_slug = 'slug' in data
                has_md5_id = 'md5_id' in data
                has_media = 'media' in data
                
                if has_user_id and has_slug and has_md5_id and has_media:
                    print(f"   🎯 TEM TODOS OS CAMPOS NECESSÁRIOS!")
                    print(f"      user_id: {data['user_id']}")
                    print(f"      slug: {data['slug']}")
                    print(f"      md5_id: {data['md5_id']}")
                    print(f"      media: {data['media'][:50]}...")
                    
                    # Salvar em arquivo
                    output_file = f"output/api_data_{video_id}.json"
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    print(f"      💾 Salvo em: {output_file}")
                else:
                    print(f"   ⚠️  Campos: user_id={has_user_id}, slug={has_slug}, md5_id={has_md5_id}, media={has_media}")
            print()
    else:
        print("\n❌ Nenhum endpoint funcionou")
        print("\n💡 Possíveis razões:")
        print("  1. Vídeo não existe ou foi removido")
        print("  2. API requer autenticação")
        print("  3. API mudou completamente")
        print("  4. Endpoint está em outro domínio")
        print("\n🔧 Próximos passos:")
        print("  1. Verificar se o vídeo existe no site")
        print("  2. Usar DevTools para ver as requisições reais")
        print("  3. Consultar: CAPTURA_MANUAL.md")
        print("  4. Tentar outro vídeo")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
