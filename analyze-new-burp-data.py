#!/usr/bin/env python3
"""
Analisar os novos dados do Burp Suite
Agora temos PlayerEmbedAPI que parece mais simples!
"""

import re

# Dados do Burp Suite (formato simplificado)
burp_data = """
2773 GET /api/v1/player?t=3772aacff2bd31142eec3d5b0f291f4e... 200 780 JSON
2787 GET /?v=kBJLtxCD3 200 11514 HTML Land.of.Sin.S01E01.1080p.NF.WEB-DL.DDP5.1.Atmos.H.264.DUAL-DUBLASERIES.mp4
2813 GET /sora/254403930/MFFGS0hON3dBelNNUzQ1LzhpVFZSY1hRcXF3Ujd0ZklvdFN6eVVIQ1NMcUdJQWllaEE 302 676
2814 GET /sora/254403930/MFFGS0hON3dBelNNUzQ1LzhpVFZSY1hRcXF3Ujd0ZklvdFN6eVVIQ1NMcUdJQWllaEE (cloudflare)
2815 GET /sora/651198119/VVc5ZWM1MjlHTGFMT0NwaG91YVA5Z0hwR3ZZa1lTSUlPdzVrWW8zak5EZ1l1dWlhcFE 302 670
2816 GET /sora/651198119/VVc5ZWM1MjlHTGFMT0NwaG91YVA5Z0hwR3ZZa1lTSUlPdzVrWW8zak5EZ1l1dWlhcFE (cloudflare)
"""

print("🔍 ANÁLISE DOS NOVOS DADOS DO BURP SUITE")
print("=" * 80)

print("\n📌 DESCOBERTA 1: PlayerEmbedAPI")
print("   URL: https://playerembedapi.link/?v=kBJLtxCD3")
print("   Resposta: HTML com título 'Land.of.Sin.S01E01.1080p.NF.WEB-DL...'")
print("   Tamanho: 11514 bytes")
print("   ✅ Este player parece MUITO MAIS SIMPLES que o MegaEmbed!")

print("\n📌 DESCOBERTA 2: URLs Sora (Base64)")
print("   Padrão: /sora/{ID}/{BASE64_STRING}")
print("   ")
print("   URL 1: /sora/254403930/MFFGS0hON3dBelNNUzQ1LzhpVFZSY1hRcXF3Ujd0ZklvdFN6eVVIQ1NMcUdJQWllaEE")
print("   URL 2: /sora/651198119/VVc5ZWM1MjlHTGFMT0NwaG91YVA5Z0hwR3ZZa1lTSUlPdzVrWW8zak5EZ1l1dWlhcFE")
print("   ")
print("   Status: 302 (Redirect)")
print("   Destino: Cloudflare tunnel (trycloudflare.com)")

print("\n📌 DESCOBERTA 3: Cloudflare Tunnels")
print("   sunny-appointments-cia-honey.trycloudflare.com")
print("   greene-samba-slight-fonts.trycloudflare.com")
print("   ")
print("   ⚠️  Esses são túneis temporários do Cloudflare")
print("   ⚠️  Mudam frequentemente")

print("\n📌 DESCOBERTA 4: Domínios Sora")
print("   i34mbcqo17.sssrr.org")
print("   dxqmwq9y0.sssrr.org")
print("   kbk7xceiq0.sssrr.org")
print("   htm4jbxon18.sssrr.org")
print("   ")
print("   Padrão: {random}.sssrr.org")
print("   Protocolo: WebSocket (/future)")

print("\n" + "=" * 80)
print("💡 ANÁLISE:")
print()
print("1. MegaEmbed:")
print("   - Usa criptografia AES-CBC")
print("   - Chave aleatória")
print("   - Complexo de implementar")
print()
print("2. PlayerEmbedAPI: ⭐⭐⭐")
print("   - Parece MUITO MAIS SIMPLES")
print("   - HTML direto (11KB)")
print("   - Provavelmente tem URL do vídeo no HTML")
print("   - RECOMENDADO para análise!")
print()
print("3. Sora URLs:")
print("   - Base64 encoded")
print("   - Redirect para Cloudflare tunnels")
print("   - Provavelmente são os links finais do vídeo")
print()
print("=" * 80)
print("🎯 RECOMENDAÇÃO:")
print()
print("   ANALISE O PLAYEREMBEDAPI PRIMEIRO!")
print("   É muito mais simples que o MegaEmbed")
print()
print("   Próximos passos:")
print("   1. Salvar o HTML de playerembedapi.link/?v=kBJLtxCD3")
print("   2. Procurar por URLs de vídeo no HTML")
print("   3. Decodificar as strings Base64")
print("   4. Implementar extractor simples")
print("=" * 80)

# Decodificar as strings Base64
print("\n📌 DECODIFICANDO BASE64:")
import base64

base64_strings = [
    "MFFGS0hON3dBelNNUzQ1LzhpVFZSY1hRcXF3Ujd0ZklvdFN6eVVIQ1NMcUdJQWllaEE",
    "VVc5ZWM1MjlHTGFMT0NwaG91YVA5Z0hwR3ZZa1lTSUlPdzVrWW8zak5EZ1l1dWlhcFE",
]

for i, b64_str in enumerate(base64_strings, 1):
    try:
        decoded = base64.b64decode(b64_str).decode('utf-8')
        print(f"\n   String {i}:")
        print(f"   Base64: {b64_str[:50]}...")
        print(f"   Decoded: {decoded}")
    except Exception as e:
        print(f"   String {i}: Erro ao decodificar - {e}")

print("\n" + "=" * 80)
