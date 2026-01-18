#!/usr/bin/env python3
"""
Análise da resposta da API /api/v1/player do MegaEmbed
A resposta é um hex string gigante que precisa ser decodificado
"""

import binascii
import json

# Resposta capturada do Burp Suite
hex_response = "933a30ecdabc15152bfbe068bc27d5342f59759c823e7e206be7a128ff897fc44fd4e82e2a801097e8bf2d3bcd927deecf7dd715b665ab57521809a4f68fe756dda2d6b801482e850f9e193f36cb80c0b2711a4324b8126357dac03e5b572909d7c67ce8d8d90cf950986476da2052363f7346b0f3d3e9e26794c05a8fac453c8d153e3c97e9c278d7a841264d234ac3c2844368f3b7071baf34f03e3395e382d57227dac2b465f0bde178164a410ff1b6156d51082fd3e25c7619c01897d61cd455687f75fb4037cd4e2ae1cb1c3529af0214ecba4473e15f5dacea8f19cdf612efef09ddf4bf73effe416ba1af9069ce16a1c954da14a0266e5cc84f9586a059e45cc3da20e0e4ffebbc297ece0a264566bcc83bbf1dc66410a9285db8ae45e458878d74612013ac760a39dd004d3f3305afcf80328c7af8966e127ce61c4022c17188e7f788d64070ac8a9a5a68f7797f2e08fb94ea968fe52bf1e746db5f44bd08d16ca1e42f300c3e59eccce72c42a9b7d90306c5ebbb79a2268a946f2a4a6cb0dfb0ec804f3492ac6f7827e20dea0e2feee98bc8d20650285e51312da5637e5da05e9230fd1d122aacbd8cc50d24408d384cb39477fda9ebd11e9f25f72a60cecb5714aa39ec23399d327e5020dbe10c2e6e854b86f9606473f15ee80019e04277ae8642b105c4403fd86b97f27e8579dd5405f21ff79eb15d6fe511fa65e5db760b1965ec3a7405a44f0222004d8031affa3ed4ba0adbbf7aa039004434468fbab6057e7554a8520c4a1740d762ff471e4e82345d3ea49328c8f7720dc53beb4be3a079f6929cf710dbb6ff60fd08da05a07426833bc24d9b5f37358f4eb52b2a5d8e4ba34da1574cd942bee70218c9ce334cfcb2044c5128002e6d8d71bf995972861c664590e58efcb93d6d0eb47da53b9c0bb4db221ffeeb69ebd1990e5574caf52830a392400cf3cad6608f8accf259dacf5b5a80616ccc57cb5fba63f64136ad77f5e4a19d262e4461dbc5420c0e28660c5e762bfe86831fef16da016c9fa6298efb2a77ef0d576beab020b593e1a01d09cb37df153345368d97808629bbdbe77bcbf87f23dd0c330a6cf4620c29b008d63033f4b6a9d73a27e6cf8018755b3c24b645edcfdbda39d3d15d18b399a4b5b009b4a73e95ae5a9b6399b8635e5f1cf461e595f971041eb1f48dd7eb7ae392f926e3dfb08ac8111790ee54154d2a0844977ee15a05f5eda436e6ac0aabc49df626c1cc97445a452b831cf2ac0e683ad0c08f6754b0234786225eb2088c411411a0a46568cac8da171cc247507ebfe2575a58ff8340e4e28cbd5645e357c80255e4190b71f3b3b24cb25fe84053838a10025308ab2f465c2cf7e1e7fd56ffb1234d92838b6ec5271724bd5b79c15d4c01a9a932c10241b72b526f6f7d3f6921b719a00b48432beca7eeb84a8f6f346d91e83a5f3f3db7fc1514efff2683f9216be960fac9a2d7850e8441db9b29a7846e1e3ef1d70d64e8e236c060af03d80c8bdef1e0e255d47ff886d868cca7cfa795d34041452edb746d734513251fb57a6c16d520a90e1e972f48d9cc9aee1b9fee7f89cb84390a5e7ba33ecb019dc5fa9ba82aa3b689944004dd3df4c3ee7bf06223ed20e15255cd794f458d007d2546644e3302cd4b20254345e9338e4c992e0b99a82b85aeef5eeb7ead8d8a5ff29efb976108d960abad68f13329260fdd341f12b77e4e23bb9a5c814920572f240af7784bcf3f9f80eab84d42c5926b779535f79dc04f5b513e9109576d23a5667c3c77352fc6276b905fa32137c2b3f96805d8b5716ecde0c5cd299e7286d29c210a7907834f61a2d0b4c4534bbf6ed8e266dfed4d24379fb460ca1c6b8eea7a32ccb02908d6b026d49ce9a016d2d3b22fdda1c71ae2e026819a99bf9b5aa12b62b1638ad550f973ed9e198539ff09f5b4acacc2d3a59e3cf2bba79400a601591fffae2e6c1447590f1e8ebb65f14d7d30d588b37383a774b6c1ac8a54bfb812cd2256413346700755043d3629452ea5b8ed3b34341deeabcc573e5b7b4e3b6840a21d798b90df15df0065d1323ca0feace523d2a86fb7066f0916ef6e84cef8e4236918ea2705b956fe18adebc88f8de80f67c7e570efc2f416f88422e8efd00059f43c7242e53d5513aa7ae91826067b7b3e435bd4a4a8545fec6dfc1efedf6bde1e96e503e68f63689938b1ed00a106c3a8acfccacbcd648370adf995f8b173debe5faf1bbb861fb3b204cf2ef4781f6e532c3d7d1a857dfd4bf0c2e092be1de37c44c7f710ef128e3b35b599253ec18d33ed33ef70a35e45b9bdc10f760cff71daec2347533707b120929c0dfecfe8f14fe4450114609672c0aa5e4eeb6556499b7eacbf439c294e24911bbf5da493027517f406632431ea97c6a587f7d4178bd8f5ce3df94fba0492ddde0d7b66ef6a34ec098d96f210fbdac84d21d6a54a78c8cd2cea40d47ca7e0c081dcde85c8a54e6c090d732cc643628063a6f96eab3b1a52fb55f810e13433d2dd6251daa2643e21ace06f274f3b19016a1f4a93cc88b785720c9e3304aca5ea3d8aedfaa2f2db26e61ea7889be4988fe65e3768518fedad1638019f0fe9bf504060278e04df54a20779b1119d9ebcdc8474c1a3cf5b372762ac77319cadf59bf0d7de587b45110fe22b8d730a077fb25c33461f35d2e9defde1614e21649ead78c83484cdc74a3ecf201aae90b3414d630fb05dec4de524ffe8b5a02f4960284f7830ea09f07c71b496450287048e2593e1c94634aef7e3e1e54288819f78df285425935826e3177a8a6b6de93353b8c1e0dcf40049e96265c87bf1b1c8e055e2c5610e63be16a313688cd84b11326fa78707012459331472ba5fbdfaad8659bf641ec3f9575da3dfd8984063bd034ad5aea614b797dbdeb2359057abd5eb1ccb15549357d59c34091776b447dfac920732796751f90d41b68b2dabd116314e9f224ed10c80efb6fe910d9a6c405f870eb2c169cabc6b73b05e3272225e19c80e94d0f1ea6661af3ffb51b6ee6e4483eaa988d7a73c4f776400cd659e2c51a330bb23cf0a061f7867826f04a6bacb5951f5379b2e2b2fa19859a85c470ebae29fbce335b8d72de857079365aa748c3f3ab15df533182eebff294ca80905ba5d8ed8497145687ebd47b8a1226105e52c6a3c2b9fe8e71422ba26c5c0f37a0d7dc2409c614caf48d42efbe26d43ff192481417d362f6f094838be9971d189decbc351e7b8684eae2c7b79bb4e5318f3c5dc9c0b01e8dac93ddf0c0a22ed40c02cc1fd664d6712a995025f83cd99ac3c6d6f296e99041e91d550d7bdb0f2ca30f92736319fd313a6ef03a215036cca0cd75eff858e74a3a88a3dc9f93fe51484f7c48b43361248e85ab3943a33e835dc3bcd2234c51bbefc3a71a04307a64bc45f458b4c4448ecfad1bf3fab4cfecb54c355a1b66e00b51d560c39308b3cb6594c71862ac36763d4d1163583d836a6fac51c9f5ffa5b6457f2c85a341736926e5c3f9532"

print("🔓 DECODIFICANDO RESPOSTA DO MEGAEMBED")
print("=" * 80)
print(f"Tamanho do hex: {len(hex_response)} caracteres")
print(f"Tamanho em bytes: {len(hex_response) // 2} bytes")

# Converter hex para bytes
try:
    raw_bytes = binascii.unhexlify(hex_response)
    print(f"✅ Conversão hex → bytes: OK")
    print(f"   Primeiros 50 bytes (hex): {raw_bytes[:50].hex()}")
    print(f"   Primeiros 50 bytes (raw): {raw_bytes[:50]}")
except Exception as e:
    print(f"❌ Erro ao converter hex: {e}")
    exit(1)

# Tentar decodificar como texto
print("\n📌 Tentando decodificar como texto...")
encodings = ['utf-8', 'latin-1', 'ascii', 'utf-16', 'utf-32']
for encoding in encodings:
    try:
        decoded = raw_bytes.decode(encoding)
        print(f"   ✅ {encoding}: {decoded[:200]}")
        if 'http' in decoded.lower() or 'm3u8' in decoded.lower() or 'txt' in decoded.lower():
            print(f"      🎯 ENCONTRADO URL/M3U8!")
            print(f"      Conteúdo completo:\n{decoded}")
            break
    except:
        print(f"   ❌ {encoding}: falhou")

# Procurar padrões de URL no raw bytes
print("\n📌 Procurando padrões de URL nos bytes...")
url_patterns = [b'http://', b'https://', b'.txt', b'.m3u8', b'srcf.', b'marvel']
for pattern in url_patterns:
    if pattern in raw_bytes:
        idx = raw_bytes.find(pattern)
        print(f"   ✅ Encontrado '{pattern.decode()}' na posição {idx}")
        # Extrair contexto
        start = max(0, idx - 50)
        end = min(len(raw_bytes), idx + 200)
        context = raw_bytes[start:end]
        print(f"      Contexto: {context}")

# Verificar se é JSON comprimido
print("\n📌 Verificando se é JSON comprimido (gzip/zlib)...")
import zlib
import gzip
from io import BytesIO

# Tentar gzip
try:
    with gzip.GzipFile(fileobj=BytesIO(raw_bytes)) as f:
        decompressed = f.read()
    print(f"   ✅ GZIP: Descomprimido {len(decompressed)} bytes")
    print(f"      Conteúdo: {decompressed[:500]}")
    
    # Tentar parsear como JSON
    try:
        data = json.loads(decompressed)
        print(f"      🎯 É JSON! Chaves: {list(data.keys())}")
        print(f"      Dados completos:\n{json.dumps(data, indent=2)}")
    except:
        print(f"      Não é JSON, é texto: {decompressed.decode('utf-8', errors='ignore')[:500]}")
except Exception as e:
    print(f"   ❌ GZIP: {e}")

# Tentar zlib
try:
    decompressed = zlib.decompress(raw_bytes)
    print(f"   ✅ ZLIB: Descomprimido {len(decompressed)} bytes")
    print(f"      Conteúdo: {decompressed[:500]}")
    
    # Tentar parsear como JSON
    try:
        data = json.loads(decompressed)
        print(f"      🎯 É JSON! Chaves: {list(data.keys())}")
        print(f"      Dados completos:\n{json.dumps(data, indent=2)}")
    except:
        print(f"      Não é JSON, é texto: {decompressed.decode('utf-8', errors='ignore')[:500]}")
except Exception as e:
    print(f"   ❌ ZLIB: {e}")

# Verificar se é criptografia (AES, etc)
print("\n📌 Analisando entropia (detectar criptografia)...")
import collections
byte_freq = collections.Counter(raw_bytes)
entropy = -sum((count/len(raw_bytes)) * __import__('math').log2(count/len(raw_bytes)) 
               for count in byte_freq.values())
print(f"   Entropia: {entropy:.2f} bits/byte")
print(f"   Interpretação:")
if entropy > 7.5:
    print(f"      🔒 ALTA entropia ({entropy:.2f}) - Provavelmente CRIPTOGRAFADO")
    print(f"      Pode ser AES, ChaCha20, ou outro algoritmo de criptografia")
elif entropy > 6:
    print(f"      📦 MÉDIA entropia ({entropy:.2f}) - Provavelmente COMPRIMIDO")
else:
    print(f"      📄 BAIXA entropia ({entropy:.2f}) - Texto ou dados estruturados")

print("\n" + "=" * 80)
print("💡 CONCLUSÃO:")
print("   A resposta é um hex string que precisa ser:")
print("   1. Convertido de hex para bytes")
print("   2. Descriptografado (se entropia > 7.5)")
print("   3. Descomprimido (se entropia 6-7.5)")
print("   4. Parseado como JSON ou texto")
print("=" * 80)
