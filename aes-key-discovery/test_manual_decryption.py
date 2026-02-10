#!/usr/bin/env python3

"""
Script para testar decriptação manualmente com dados fornecidos
"""

import hashlib
import base64
import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

def md5(text):
    """Gera hash MD5"""
    return hashlib.md5(text.encode()).hexdigest()

def decrypt_openssl_format(encrypted_data, password):
    """Decripta formato OpenSSL (Salted__)"""
    try:
        # Decodificar base64
        data = base64.b64decode(encrypted_data)
        
        # Verificar se começa com "Salted__"
        if data[:8] != b'Salted__':
            print("⚠️  Dados não estão no formato OpenSSL (Salted__)")
            return None
        
        # Extrair salt
        salt = data[8:16]
        ciphertext = data[16:]
        
        # Derivar chave e IV usando EVP_BytesToKey (compatível com OpenSSL)
        key_iv = evp_bytes_to_key(password.encode(), salt, 32, 16)
        key = key_iv[:32]
        iv = key_iv[32:48]
        
        # Criar cipher
        cipher = AES.new(key, AES.MODE_CBC, iv)
        
        # Decriptar
        decrypted = cipher.decrypt(ciphertext)
        
        # Remover padding
        decrypted = unpad(decrypted, AES.block_size)
        
        return decrypted.decode('utf-8')
    except Exception as e:
        print(f"❌ Erro na decriptação: {e}")
        return None

def evp_bytes_to_key(password, salt, key_len, iv_len):
    """Implementação de EVP_BytesToKey (compatível com OpenSSL)"""
    m = []
    i = 0
    while len(b''.join(m)) < (key_len + iv_len):
        md = hashlib.md5()
        data = password + salt
        if i > 0:
            data = m[i - 1] + data
        md.update(data)
        m.append(md.digest())
        i += 1
    return b''.join(m)[:key_len + iv_len]

def test_formula(user_id, slug, md5_id, encrypted_media):
    """Testa a fórmula descoberta"""
    
    print("\n╔════════════════════════════════════════════════════════════╗")
    print("║  🔓 Teste Manual de Decriptação                          ║")
    print("╚════════════════════════════════════════════════════════════╝\n")
    
    print("📊 Dados Fornecidos:")
    print(f"  user_id: {user_id}")
    print(f"  slug: {slug}")
    print(f"  md5_id: {md5_id}")
    print(f"  media: {encrypted_media[:50]}...")
    print()
    
    # Fórmula descoberta: user_id:slug:md5_id
    formula_value = f"{user_id}:{slug}:{md5_id}"
    
    print("🔑 Fórmula Descoberta:")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"  user_id + ':' + slug + ':' + md5_id")
    print(f"  = {formula_value}")
    print()
    
    # Tentar decriptar diretamente (sem MD5)
    print("🔓 Tentativa 1: Chave direta (sem hash)")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    result = decrypt_openssl_format(encrypted_media, formula_value)
    if result:
        print("✅ SUCESSO! Decriptação bem-sucedida!")
        print()
        print("📄 Dados Decriptados:")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        try:
            parsed = json.loads(result)
            print(json.dumps(parsed, indent=2, ensure_ascii=False))
        except:
            print(result)
        print()
        print("🎉 A fórmula está CORRETA!")
        return True
    else:
        print("❌ Falhou")
        print()
    
    # Tentar com MD5
    print("🔓 Tentativa 2: MD5 da chave")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    hash_value = md5(formula_value)
    print(f"  MD5: {hash_value}")
    result = decrypt_openssl_format(encrypted_media, hash_value)
    if result:
        print("✅ SUCESSO! Decriptação bem-sucedida!")
        print()
        print("📄 Dados Decriptados:")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        try:
            parsed = json.loads(result)
            print(json.dumps(parsed, indent=2, ensure_ascii=False))
        except:
            print(result)
        print()
        print("🎉 A fórmula com MD5 está CORRETA!")
        return True
    else:
        print("❌ Falhou")
        print()
    
    # Testar outras combinações
    print("🔓 Tentativa 3: Outras combinações")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    formulas = [
        ("user_id + slug + md5_id", f"{user_id}{slug}{md5_id}"),
        ("slug + user_id + md5_id", f"{slug}{user_id}{md5_id}"),
        ("md5_id + user_id + slug", f"{md5_id}{user_id}{slug}"),
    ]
    
    for name, value in formulas:
        print(f"  Testando: {name}")
        result = decrypt_openssl_format(encrypted_media, value)
        if result:
            print(f"  ✅ SUCESSO com: {name}")
            print()
            print("📄 Dados Decriptados:")
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            try:
                parsed = json.loads(result)
                print(json.dumps(parsed, indent=2, ensure_ascii=False))
            except:
                print(result)
            return True
    
    print("❌ Nenhuma combinação funcionou")
    print()
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()
    print("⚠️  Possíveis razões:")
    print("  1. Campo 'media' está incorreto ou corrompido")
    print("  2. Algoritmo de criptografia diferente")
    print("  3. Formato de dados diferente")
    print("  4. Parâmetros user_id, slug ou md5_id incorretos")
    
    return False

def main():
    print("\n" + "="*60)
    print("  🔓 TESTE MANUAL DE DECRIPTAÇÃO - PlayerEmbedAPI")
    print("="*60 + "\n")
    
    print("💡 INSTRUÇÕES:")
    print("  1. Obtenha os dados da API manualmente")
    print("  2. Edite este script e preencha os valores abaixo")
    print("  3. Execute: python test_manual_decryption.py")
    print()
    
    # ============================================================
    # DADOS REAIS CAPTURADOS DA API
    # ============================================================
    
    user_id = "482120"
    slug = "kBJLtxCD3"
    md5_id = "28930647"
    # Dados do campo 'media' (base64 extraído do HTML)
    encrypted_media = "vEj0XHUwMDA2q1x1MDAwNIOMNv4n1dkxpk/NQUz4lFam8OQ8VN5cdTAwMThcdTAwMWWvk1NcdTAwMTNjyFxiJGAo3rHh2C9cdTAwMTjgTFx1MDAxMjVcdTAwMTBPamurbFQ97ONcdTAwMWRVXHUwMDE4LJq/XHUwMDFhRFx1MDAwMJCoq/dcdTAwMTFWiVx1MDAxM+pXXHUwMDE2ikRcdN/hL1x1MDAxOFxyg0P9VLRya4TjV+BzTkEjvdowwFx1MDAwNVx1MDAxNISVWidO91x1MDAwNlx1MDAxMDZSXVvK7fF4e7c5N1x1MDAxYTJgXkzYViRfOCFcdMspfMdTPobK2dm9zZKewVx1MDAxZlQ2/9DttlximcajX9z/tKHaXHUwMDE213f5nJ4rXHTHXHUwMDE1XGL1z1xubmZcdTAwMDSesGA9luTlOVx1MDAxMVVWvn8wboAjbbxcdTAwMTU7LEGu8Vx1MDAwYqtcdTAwMTblcSl7xX9o8KtcdTAwMTmDXGJW5WBcdTAwMDKpvJnB6/JcdTAwMTdBk/dmnaW2wKucRbBzXGaVX3HSlJQhVT+vP8ClZFx1MDAxMVKzxVx1MDAxOH+mNbNWNLGdlITtxStqPYSmPzFcdTAwMWZ/3Fx1MDAxZmvWaVx1MDAxMidS1uLKK2zxwzmASt2Kxlb2bk4xXCJrttt4+pJi+jpcdTAwMWHqXGbmpodrhbbW2VxuXHUwMDE2XHUwMDAwJVx1MDAwM/pcdTAwMTLl7F+2JkjxzZ55XHUwMDFjNeeY8plcdTAwMTCRoVbTt1x1MDAxN4aGRmrQhP1H2JNcIr2XxZ1cdTAwMTfC61x1MDAxYVxc3Vx1MDAwMniEmFxuXHUwMDA3+lx1MDAxOFx1MDAwNZjHO5CBcqt2VDb6yaI38LBcXDxGbCi2ilxyl2Pk4q8rbN17oG9DXHUwMDE1MlSm8mj+eVKHTtwp+q5cdTAwMWRNbVx1MDAxMMRrtyVrLVx1MDAwMVx1MDAxNWlcdTAwMDTlMeTM8rBA1e9LJY3Q7VxcXHUwMDFjL9lTmWeVgN/WOTnwXHUwMDAzRe/HnXk8XHUwMDEzqvBcdTAwMDHzOu34l1x1MDAwZS1RnSRcdPTUz84po6yehLeQuU9uXHUwMDA3JZL/XHUwMDE4XHUwMDFmWazlqV/rXHUwMDA3aC9cdTAwMTPB6sB0g6WuXHUwMDE1JVx1MDAwMlVcIvFUi1xif1ZcIrPEz4l2TE7sXHUwMDAyzasv6IH0UO7gq1x1MDAwN4C9XVx1MDAwN1x1MDAxMSRk5rT6Un5cbtBcdTAwMDPTXHUwMDEzedPdMFx1MDAxNTq08kemQMFcdTAwMThcdTAwMDBrii9PXHUwMDA2siNcdTAwMTFGwip8NFx1MDAxN2qWkVx0S/PDrUedsX9KWD9pzFx1MDAxOYGgeFx013lcdTAwMTCPwDdRXHQvjvuchVx1MDAwYrGFmHlcdTAwMWb/xcQ2m6/FXHUwMDE35zhkXHUwMDE0L3z9x6DLNGz3lFx1MDAxOVxupVFcdTAwMTlv8Fx1MDAwN7Lf9p1Kx4NTfGZcdTAwMWOHguRcYjkzXHUwMDFhWfiN4zXEXGZAqb/CdiHKq0vmUdnGVVnOSFx1MDAxNd7vqFxui1x1MDAxOFxiXHUwMDE1XHUwMDFk9tRIXHUwMDA1XHLcutTHmDsydlx1MDAxOZJccoTrLip6euPk6NXcV/9URFx1MDAxZCym7mE6w7E1mIJcdTAwMDBcdTAwMWO+veyldf5tnlx1MDAwMTAkWHFMa5JyXHUwMDE3XFy6xlxc9baZXCLE0sDF9IJ3flx1MDAxNVx1MDAxYYhTXGYzPP/ibWo02UxygnhqYYJ3wb4sPWfESEBHNrqcXHUwMDFjbFRV6TBkSmdcdTAwMWE9fVx1MDAwZZXs8kJcZplykEtw4TBcdTAwMWVcZkvd4/RIUVx1MDAxZfLomcyVSPLTRljnyY423ypTiHOAqlx1MDAwYlHTNjF32f/BSPxkknDD8ECyvGtL4L5cdTAwMGJcdTAwMGKp6Hi2pd/KmLz0XHTHq1x1MDAxY9HkoFx1MDAxM1x00KYw37lzXG5RmVx1MDAxNXQ+2u9cdTAwMTV1Skm9cGP1olMuXHUwMDBl2JmmMpWXZCa12U+RXHQ7ZtHXbJRCde3g+1x1MDAwYrXxxPPvSDRKzk6IcSvyQMckuVx1MDAwMvkqvzSuhXqg4lxmgtFWXHUwMDE2oafSKufrwaSd3pPmYN/Z6z9cdPqu8j7CQexcdTAwMTJQzdhcdTAwMDPGI1VD07d8ajZB1lx1MDAxYeb8xVPkPmyie5vA8tleXHUwMDA1u0g5uN5pXHUwMDA0PZjGSlx1MDAxZlfOtM9e5NKi+FXeXG6ztDqjqmiIIFxc1JdQrEiKJenivDHnqPGAeFfPL960XHUwMDE4tdyjt8nkd/N3kClcXM3BL3NcdTAwMTKIc9uzVfBsSLYlgfP8r2EkmDTn5lx1MDAxZjK2dlx1MDAxZv/w7i7Uidd6XHUwMDBio5JyJftcdTAwMDBUotJcdTAwMDeU8FJcdTAwMGIl4tRcdTAwMDDXRmJcdFx1MDAwMXVcdTAwMDFcdTAwMWU8l52dfFx1MDAwNnpcdTAwMDW4vLBdaXBcdTAwMTLexWhcdTAwMDHbhci5tlx1MDAxYdJcdTAwMTRSjVx1MDAwYjHkSO01aCpP6zm2vsEvZOP15N5SMU9IPYnw/UtRI9DSXHUwMDFk9Fx1MDAwNbqDWGxUXHUwMDEz1LGMN4GJycGPO7fsXFxdXHUwMDA11absaYVcdTAwMWIsTE5u5yunsDteJnmTvr32VKCn/VKsy1U025Gvnd3oUudXY3xjXHUwMDBlk7bEqlx1MDAxY1x1MDAxZqiVZcJg+W//xZRcdTAwMWKUXHUwMDA2UHvF9JM="
    
    # ============================================================
    
    if encrypted_media == "U2FsdGVkX1...":
        print("⚠️  ATENÇÃO: Você precisa editar este script!")
        print()
        print("📝 Passos:")
        print("  1. Abra o arquivo: test_manual_decryption.py")
        print("  2. Localize a seção 'EDITE AQUI'")
        print("  3. Substitua os valores com dados reais da API")
        print("  4. Salve e execute novamente")
        print()
        print("📡 Para obter os dados:")
        print("  • Use Burp Suite para interceptar a requisição")
        print("  • Ou use o navegador DevTools (Network tab)")
        print("  • Ou use curl/Postman para fazer a requisição")
        print()
        return
    
    # Executar teste
    success = test_formula(user_id, slug, md5_id, encrypted_media)
    
    if success:
        print()
        print("╔════════════════════════════════════════════════════════════╗")
        print("║  ✅ SUCESSO! Fórmula validada com dados reais!           ║")
        print("╚════════════════════════════════════════════════════════════╝")
        print()
        print("🚀 Próximos passos:")
        print("  1. Documentar a fórmula confirmada")
        print("  2. Implementar no plugin BRCloudstream")
        print("  3. Testar com múltiplos vídeos")
    else:
        print()
        print("╔════════════════════════════════════════════════════════════╗")
        print("║  ❌ Falha na validação                                    ║")
        print("╚════════════════════════════════════════════════════════════╝")
        print()
        print("💡 Próximos passos:")
        print("  1. Verificar se os dados estão corretos")
        print("  2. Usar Frida para capturar a chave em runtime")
        print("  3. Analisar o código JavaScript manualmente")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
