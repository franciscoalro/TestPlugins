#!/usr/bin/env python3
"""
Script para decodificar os offsets do código ofuscado
e descobrir quais parâmetros são usados na chave AES
"""

import re
import sys

def find_string_array(js_content):
    """Encontra o array de strings ofuscado"""
    # Procurar por arrays grandes de strings
    pattern = r"const\s+_0x[a-f0-9]+\s*=\s*\[(.*?)\];"
    matches = re.findall(pattern, js_content, re.DOTALL)
    
    for match in matches:
        # Contar quantas strings tem
        strings = re.findall(r"'([^']*)'", match)
        if len(strings) > 100:  # Array grande
            return strings
    
    return []

def hex_to_dec(hex_str):
    """Converte hex para decimal"""
    if hex_str.startswith('0x'):
        return int(hex_str, 16)
    return int(hex_str)

def main():
    print("╔════════════════════════════════════════════════════════════╗")
    print("║  🔍 Decodificador de Offsets                              ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print()
    
    # Ler o arquivo deobfuscado
    try:
        with open('output/lite_deobf.js', 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print("❌ Arquivo output/lite_deobf.js não encontrado!")
        print("   Execute primeiro: bash run_analysis.sh")
        sys.exit(1)
    
    print("📖 Lendo arquivo deobfuscado...")
    
    # Encontrar o array de strings
    print("🔍 Procurando array de strings...")
    strings = find_string_array(content)
    
    if not strings:
        print("❌ Array de strings não encontrado!")
        sys.exit(1)
    
    print(f"✓ Encontrado array com {len(strings)} strings")
    print()
    
    # Offsets que queremos decodificar
    offsets = {
        '0x309': None,
        '0x2a9': None,
        '0x42a': None,
        '0x607': None,  # Campo 'media' criptografado
    }
    
    print("🔑 Decodificando offsets:")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    for offset_hex, _ in offsets.items():
        offset_dec = hex_to_dec(offset_hex)
        if offset_dec < len(strings):
            value = strings[offset_dec]
            offsets[offset_hex] = value
            print(f"  {offset_hex} ({offset_dec:4d}) = '{value}'")
        else:
            print(f"  {offset_hex} ({offset_dec:4d}) = [FORA DO RANGE]")
    
    print()
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()
    
    # Mostrar a fórmula descoberta
    param1 = offsets.get('0x309', '???')
    param2 = offsets.get('0x2a9', '???')
    param3 = offsets.get('0x42a', '???')
    
    print("🎯 FÓRMULA DA CHAVE AES:")
    print(f"   {param1} + ':' + {param2} + ':' + {param3}")
    print()
    
    # Se conseguimos identificar os parâmetros
    if all([param1 != '???', param2 != '???', param3 != '???']):
        print("✅ Fórmula identificada com sucesso!")
        print()
        print("📝 Exemplo com valores de teste:")
        print("   user_id = 482120")
        print("   slug = kBJLtxCD3")
        print("   md5_id = 28930647")
        print()
        
        # Tentar identificar qual é qual
        params = [param1, param2, param3]
        if 'user' in param1.lower() or 'id' in param1.lower():
            print(f"   Chave = 482120:{param2}:{param3}")
        elif 'slug' in param1.lower():
            print(f"   Chave = kBJLtxCD3:{param2}:{param3}")
        elif 'md5' in param1.lower():
            print(f"   Chave = 28930647:{param2}:{param3}")
        else:
            print(f"   Chave = {param1}:{param2}:{param3}")
        print()
        
        # Salvar resultado
        with open('output/key_formula_decoded.txt', 'w') as f:
            f.write("FÓRMULA DA CHAVE AES DESCOBERTA\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Fórmula: {param1} + ':' + {param2} + ':' + {param3}\n\n")
            f.write("Offsets decodificados:\n")
            for offset_hex, value in offsets.items():
                offset_dec = hex_to_dec(offset_hex)
                f.write(f"  {offset_hex} ({offset_dec:4d}) = '{value}'\n")
        
        print("💾 Resultado salvo em: output/key_formula_decoded.txt")
    else:
        print("⚠️  Não foi possível identificar todos os parâmetros")
        print("    Tente analisar manualmente o código")
    
    print()

if __name__ == '__main__':
    main()
