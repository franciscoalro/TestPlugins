#!/bin/bash

# Procura padrões de criptografia no código

FILE="$1"

echo "=== PADRÃO 1: crypto.subtle.importKey ==="
grep -n -A 20 -B 5 "importKey" "$FILE" | head -100

echo ""
echo "=== PADRÃO 2: AES-CBC ou AES-GCM ==="
grep -n -A 10 -B 5 "AES-" "$FILE"

echo ""
echo "=== PADRÃO 3: Derivação de chave ==="
grep -n -A 15 -B 5 -E "(deriveKey|pbkdf2|hkdf)" "$FILE"

echo ""
echo "=== PADRÃO 4: Concatenação de strings (possível fórmula) ==="
grep -n -E "(\+|concat|join).*user_id|slug|md5_id" "$FILE" | head -50

echo ""
echo "=== PADRÃO 5: Funções MD5/SHA ==="
grep -n -A 10 -B 5 -E "(MD5|md5|SHA|sha)\(" "$FILE" | head -100

echo ""
echo "=== PADRÃO 6: TextEncoder (conversão para bytes) ==="
grep -n -A 5 "TextEncoder" "$FILE"

echo ""
echo "=== PADRÃO 7: ArrayBuffer/Uint8Array ==="
grep -n -E "(ArrayBuffer|Uint8Array|Buffer\.from)" "$FILE" | head -30
