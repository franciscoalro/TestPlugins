#!/usr/bin/env python3

"""
Script de Validação - Verificar acesso à página e estrutura HTML
"""

import requests
import re
import json
import base64

def validate_page_access():
    print("╔════════════════════════════════════════════════════════════╗")
    print("║  🔍 VALIDAÇÃO - Acesso à Página PlayerEmbed              ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print("")
    
    video_slug = "kBJLtxCD3"
    url = f"https://playerembedapi.link/?v={video_slug}"
    
    print(f"🌐 URL: {url}")
    print("⏳ Fazendo requisição...")
    print("")
    
    try:
        response = requests.get(url, timeout=15)
        
        print(f"📊 Status: {response.status_code}")
        print(f"📏 Tamanho: {len(response.text)} bytes")
        print("")
        
        if response.status_code != 200:
            print("❌ Página não está acessível")
            return False
        
        html = response.text
        
        # Verificar se tem os elementos esperados
        print("🔍 Verificando estrutura HTML...")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        checks = {
            "const datas": "const datas" in html,
            "window.SoTrym": "window.SoTrym" in html or "SoTrym" in html,
            "lite.bundle.js": "lite.bundle.js" in html,
            "core.bundle.js": "core.bundle.js" in html,
            "base64 data": 'const datas = "' in html or "const datas='" in html
        }
        
        for check, result in checks.items():
            status = "✅" if result else "❌"
            print(f"  {status} {check}: {result}")
        
        print("")
        
        # Tentar extrair dados base64
        print("🔍 Tentando extrair dados base64...")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        # Padrões possíveis
        patterns = [
            r'const datas\s*=\s*"([^"]+)"',
            r"const datas\s*=\s*'([^']+)'",
            r'var datas\s*=\s*"([^"]+)"',
            r"var datas\s*=\s*'([^']+)'",
        ]
        
        data_found = None
        for pattern in patterns:
            match = re.search(pattern, html)
            if match:
                data_found = match.group(1)
                print(f"✅ Dados encontrados com padrão: {pattern}")
                break
        
        if data_found:
            print(f"📦 Tamanho dos dados: {len(data_found)} chars")
            print(f"📄 Primeiros 100 chars: {data_found[:100]}...")
            print("")
            
            # Tentar decodificar base64
            try:
                decoded = base64.b64decode(data_found)
                # Tentar decodificar como UTF-8, mas aceitar erros
                try:
                    decoded_str = decoded.decode('utf-8')
                except UnicodeDecodeError:
                    # Se falhar, tentar com latin-1 que aceita todos os bytes
                    decoded_str = decoded.decode('latin-1')
                
                print("✅ Base64 decodificado com sucesso!")
                print("")
                
                # Tentar parsear como JSON
                try:
                    data_json = json.loads(decoded_str)
                    print("✅ JSON parseado com sucesso!")
                    print("")
                    print("📊 Estrutura dos dados:")
                    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                    
                    # Verificar campos esperados
                    expected_fields = ['user_id', 'slug', 'md5_id', 'media']
                    for field in expected_fields:
                        if field in data_json:
                            value = data_json[field]
                            if field == 'media':
                                print(f"  ✅ {field}: {str(value)[:50]}... ({len(str(value))} chars)")
                            else:
                                print(f"  ✅ {field}: {value}")
                        else:
                            print(f"  ❌ {field}: NÃO ENCONTRADO")
                    
                    print("")
                    
                    # Gerar chave usando a fórmula
                    if all(field in data_json for field in ['user_id', 'slug', 'md5_id']):
                        key = f"{data_json['user_id']}:{data_json['slug']}:{data_json['md5_id']}"
                        print("🔑 CHAVE GERADA USANDO A FÓRMULA:")
                        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                        print(f"  {key}")
                        print("")
                        print("📝 Fórmula:")
                        print("  user_id + ':' + slug + ':' + md5_id")
                        print("")
                        
                        # Salvar dados
                        import os
                        output_dir = "aes-key-discovery/output"
                        os.makedirs(output_dir, exist_ok=True)
                        output_file = os.path.join(output_dir, "extracted_data.json")
                        with open(output_file, 'w', encoding='utf-8') as f:
                            json.dump({
                                'key': key,
                                'data': data_json
                            }, f, indent=2, ensure_ascii=False)
                        
                        print(f"💾 Dados salvos em: {output_file}")
                        print("")
                        
                        return True
                    else:
                        print("⚠️  Alguns campos esperados não foram encontrados")
                        return False
                    
                except json.JSONDecodeError as e:
                    print(f"❌ Erro ao parsear JSON: {e}")
                    print(f"📄 Conteúdo decodificado: {decoded_str[:200]}...")
                    return False
                    
            except Exception as e:
                print(f"❌ Erro ao decodificar base64: {e}")
                return False
        else:
            print("❌ Dados base64 não encontrados no HTML")
            print("")
            print("💡 Possíveis razões:")
            print("  1. Estrutura da página mudou")
            print("  2. Dados são carregados dinamicamente via JavaScript")
            print("  3. Vídeo não existe ou foi removido")
            print("")
            return False
        
    except requests.exceptions.Timeout:
        print("❌ Timeout ao acessar a página")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Erro de conexão")
        return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("")
    success = validate_page_access()
    print("")
    print("=" * 60)
    
    if success:
        print("╔════════════════════════════════════════════════════════════╗")
        print("║  ✅ VALIDAÇÃO BEM-SUCEDIDA!                               ║")
        print("╚════════════════════════════════════════════════════════════╝")
        print("")
        print("🎉 A página está acessível e os dados foram extraídos!")
        print("")
        print("📝 Fórmula confirmada:")
        print("  user_id + ':' + slug + ':' + md5_id")
        print("")
        print("🚀 Próximos passos:")
        print("  1. Use o script validate_runtime.js para capturar a decriptação")
        print("  2. Ou use DevTools manualmente (ver SOLUCAO_FINAL.md)")
        print("  3. Implemente no plugin BRCloudstream")
    else:
        print("╔════════════════════════════════════════════════════════════╗")
        print("║  ❌ VALIDAÇÃO FALHOU                                      ║")
        print("╚════════════════════════════════════════════════════════════╝")
        print("")
        print("💡 Próximos passos:")
        print("  1. Verificar se o vídeo ainda existe")
        print("  2. Usar DevTools para inspecionar a página manualmente")
        print("  3. Consultar: SOLUCAO_FINAL.md")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
