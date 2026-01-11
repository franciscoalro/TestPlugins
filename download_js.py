import requests

# URL do JavaScript principal do MegaEmbed
url = 'https://megaembed.link/assets/index-CQ0L9dOW.js'

print(f'Baixando JavaScript de: {url}')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0',
    'Accept': '*/*',
    'Referer': 'https://megaembed.link/'
}

try:
    response = requests.get(url, headers=headers, timeout=30)
    
    if response.status_code == 200:
        content = response.text
        
        # Salvar
        output_path = r'd:\TestPlugins-master\megaembed_player.js'
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f'✅ Baixado com sucesso!')
        print(f'Tamanho: {len(content)} chars')
        print(f'Salvo em: {output_path}')
        print(f'\nPrimeiras 500 chars:')
        print(content[:500])
    else:
        print(f'❌ Erro HTTP {response.status_code}')
        
except Exception as e:
    print(f'❌ Erro: {e}')
