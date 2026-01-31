import re

with open('MaxSeries/src/main/kotlin/com/franciscoalro/maxseries/extractors/PlayerEmbedAPIExtractor.kt', 'r', encoding='utf-8') as f:
    content = f.read()

# Substituir a linha problemática
content = content.replace(
    'val decodedJson = String(decodedBytes, Charsets.UTF_8)',
    'val decodedString = String(decodedBytes, Charsets.ISO_8859_1)'
)

content = content.replace(
    'Log.d(TAG, "✅ JSON decodificado: ${decodedJson.take(200)}...")',
    'Log.d(TAG, "✅ JSON decodificado (ISO-8859-1): ${decodedString.take(200)}...")'
)

# Substituir todas as ocorrências de decodedJson por decodedString para os regex
content = content.replace(
    'userIdRegex.find(decodedJson)',
    'userIdRegex.find(decodedString)'
)
content = content.replace(
    'slugRegex.find(decodedJson)',
    'slugRegex.find(decodedString)'
)
content = content.replace(
    'md5IdRegex.find(decodedJson)',
    'md5IdRegex.find(decodedString)'
)

with open('MaxSeries/src/main/kotlin/com/franciscoalro/maxseries/extractors/PlayerEmbedAPIExtractor.kt', 'w', encoding='utf-8') as f:
    f.write(content)

print("Arquivo atualizado!")
