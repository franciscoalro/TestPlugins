#!/bin/bash

# Extrai strings relevantes do bundle

FILE="$1"

if [ ! -f "$FILE" ]; then
    echo "Erro: Arquivo não encontrado: $FILE"
    exit 1
fi

echo "=== STRINGS RELACIONADAS A CRYPTO ==="
grep -oE "(crypto|AES|importKey|decrypt|encrypt|subtle|CryptoKey)[a-zA-Z0-9_\.]*" "$FILE" | sort -u

echo ""
echo "=== STRINGS RELACIONADAS A PARÂMETROS ==="
grep -oE "(user_id|slug|md5_id|media|video_id)[a-zA-Z0-9_\.]*" "$FILE" | sort -u

echo ""
echo "=== POSSÍVEIS FUNÇÕES DE HASH ==="
grep -oE "(MD5|SHA|Hash|hash|md5)[a-zA-Z0-9_\.]*" "$FILE" | sort -u

echo ""
echo "=== STRINGS HEXADECIMAIS (possíveis chaves) ==="
grep -oE "[0-9a-fA-F]{32,}" "$FILE" | head -20

echo ""
echo "=== URLS E ENDPOINTS ==="
grep -oE "https?://[a-zA-Z0-9\.\-/]+" "$FILE" | sort -u
