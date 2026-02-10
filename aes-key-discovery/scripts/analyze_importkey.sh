#!/bin/bash

# Análise focada em crypto.subtle.importKey

FILE="$1"

echo "=== CONTEXTO COMPLETO DE importKey ==="
echo ""

# Encontrar todas as ocorrências de importKey com contexto amplo
grep -n "importKey" "$FILE" | while read -r line; do
    LINE_NUM=$(echo "$line" | cut -d: -f1)
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Ocorrência na linha $LINE_NUM:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Mostrar 30 linhas antes e 50 linhas depois
    START=$((LINE_NUM - 30))
    END=$((LINE_NUM + 50))
    
    if [ $START -lt 1 ]; then
        START=1
    fi
    
    sed -n "${START},${END}p" "$FILE" | cat -n
    echo ""
done

echo ""
echo "=== PROCURANDO VARIÁVEIS USADAS EM importKey ==="
echo ""

# Procurar por variáveis que podem conter a chave
grep -B 50 "importKey" "$FILE" | grep -E "(var|let|const|function)" | tail -20

echo ""
echo "=== PROCURANDO CHAMADAS DE FUNÇÃO ANTES DE importKey ==="
echo ""

# Procurar funções que podem gerar a chave
grep -B 30 "importKey" "$FILE" | grep -oE "[a-zA-Z_][a-zA-Z0-9_]*\(" | sort -u
