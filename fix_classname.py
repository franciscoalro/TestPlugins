#!/usr/bin/env python3
import re

# Ler o arquivo em modo binário e decodificar
with open('MaxSeries/src/main/kotlin/com/franciscoalro/maxseries/MaxSeries.kt', 'rb') as f:
    raw = f.read()

# Remover BOM se existir
if raw.startswith(b'\xef\xbb\xbf'):
    raw = raw[3:]

# Decodificar
content = raw.decode('utf-8', errors='replace')

# Substituir o nome da classe
content = content.replace('class MaxSeriesProvider : MainAPI()', 'class MaxSeries : MainAPI()')
content = content.replace('"MaxSeriesProvider"', '"MaxSeries"')

# Salvar sem BOM
with open('MaxSeries/src/main/kotlin/com/franciscoalro/maxseries/MaxSeries.kt', 'w', encoding='utf-8') as f:
    f.write(content)

print("Arquivo MaxSeries.kt atualizado")

# Verificar
with open('MaxSeries/src/main/kotlin/com/franciscoalro/maxseries/MaxSeries.kt', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for i, line in enumerate(lines[125:132], 126):
        if 'class MaxSeries' in line:
            print(f"{i}: {line.rstrip()}")
