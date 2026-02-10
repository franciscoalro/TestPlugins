#!/bin/bash

# Script para capturar a chave AES em runtime usando diferentes métodos

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  🎯 Captura de Chave AES em Runtime                       ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

echo "Escolha o método:"
echo "  1. Frida Hook (mais efetivo)"
echo "  2. Burp Suite (interceptação)"
echo "  3. mitmproxy (captura automática)"
echo "  4. Análise do bundle deobfuscado"
echo "  5. Teste de decriptação com hashes MD5"
echo ""
read -p "Opção (1-5): " choice

case $choice in
    1)
        echo ""
        echo "🔧 Método 1: Frida Hook"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        echo "📋 PASSOS:"
        echo "  1. Abrir Chrome em outra janela"
        echo "  2. Executar: frida -U Chrome -l scripts/frida_hook.js"
        echo "  3. Abrir: https://playerembedapi.link/?v=kBJLtxCD3"
        echo "  4. Ver logs no terminal do Frida"
        echo ""
        echo "💡 O Frida capturará:"
        echo "  • Chamadas para crypto.subtle.importKey"
        echo "  • keyData (em hex e text)"
        echo "  • algorithm usado"
        echo "  • Stack trace"
        echo ""
        echo "Pressione Enter para ver o script Frida..."
        read
        cat scripts/frida_hook.js
        ;;
    2)
        echo ""
        echo "🔧 Método 2: Burp Suite"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        bash scripts/burp_intercept.sh
        ;;
    3)
        echo ""
        echo "🔧 Método 3: mitmproxy"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        echo "📋 PASSOS:"
        echo "  1. Executar: mitmproxy -p 8080 -s scripts/mitmproxy_capture.py"
        echo "  2. Configurar navegador para usar proxy 127.0.0.1:8080"
        echo "  3. Abrir: https://playerembedapi.link/?v=kBJLtxCD3"
        echo "  4. Ver capturas em: output/mitmproxy_crypto.txt"
        echo ""
        ;;
    4)
        echo ""
        echo "🔧 Método 4: Análise do Bundle Deobfuscado"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        echo "Procurando padrões específicos no bundle deobfuscado..."
        echo ""
        
        if [ ! -f "output/lite_deobf.js" ]; then
            echo "❌ Arquivo deobfuscado não encontrado!"
            echo "   Execute primeiro: bash run_analysis.sh"
            exit 1
        fi
        
        # Procurar por padrões específicos
        echo "🔍 Procurando por 'expandKey' (função que processa a chave):"
        grep -n "expandKey" output/lite_deobf.js | head -10
        echo ""
        
        echo "🔍 Procurando por concatenação com slug + md5_id:"
        grep -n "slug.*+.*md5_id\|md5_id.*+.*slug" output/lite_deobf.js | head -10
        echo ""
        
        echo "🔍 Procurando por TextEncoder.encode (usado antes de importKey):"
        grep -n "TextEncoder.*encode\|encode.*TextEncoder" output/lite_deobf.js | head -10
        echo ""
        
        echo "🔍 Contexto ao redor de importKey:"
        grep -B 20 -A 20 "importKey" output/lite_deobf.js | head -50
        echo ""
        ;;
    5)
        echo ""
        echo "🔧 Método 5: Teste de Decriptação com Hashes MD5"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        echo "📊 Fórmulas candidatas (da análise avançada):"
        echo ""
        echo "1. MD5(user_id + slug + md5_id) = 7f2bea2fcccbb2d98ddddb9b08114b7d"
        echo "2. MD5(user_id + md5_id + slug) = 6d7f47451b982b4c91558d18df0b3aab"
        echo "3. MD5(slug + user_id + md5_id) = 3d0654e0feb477e3c6bb57bfdf8372aa"
        echo "4. MD5(slug + md5_id + user_id) = b755eab7ac45a9f5ee51923887ad8abe"
        echo "5. MD5(md5_id + user_id + slug) = 1ae4c5d4348ed3edbcfbf4995c9cc8aa"
        echo "6. MD5(md5_id + slug + user_id) = f7ac4b2a11ae7ec1d5b5c11bb13aba61"
        echo ""
        echo "💡 Para testar, você precisa:"
        echo "  1. Capturar o campo 'media' criptografado de uma resposta real"
        echo "  2. Testar decriptação com cada hash acima como chave AES"
        echo "  3. Ver qual funciona"
        echo ""
        echo "Executando teste com Node.js..."
        
        if command -v node &> /dev/null; then
            node test_decryption.js
        else
            echo "❌ Node.js não instalado!"
            echo "   Instale com: sudo apt install nodejs"
        fi
        ;;
    *)
        echo "❌ Opção inválida"
        exit 1
        ;;
esac

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "💡 PRÓXIMOS PASSOS:"
echo "  1. Se capturou a chave, testar decriptação"
echo "  2. Se não funcionou, tentar outro método"
echo "  3. Documentar a fórmula descoberta"
echo ""
