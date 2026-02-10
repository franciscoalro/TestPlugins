#!/usr/bin/env python3

"""
Script para analisar logs de rede capturados
Extrai URLs da API e informações relevantes
"""

import re
import json

# Logs capturados (cole aqui os logs do navegador)
NETWORK_LOGS = """
1 Zheh[zdO=incoming.telemetry.mozilla.org, zdQ=https://incoming.telemetry.mozilla.org] POST /submit/firefox-desktop/newtab/1/55560b8e-7e2b-4279-a28f-33f61ba004ba false false 200 622 text true 235 1770685965620 8080 235 3 Zheh[zdO=mozilla-ohttp.fastly-edge.com, zdQ=https://mozilla-ohttp.fastly-edge.com] POST / true false 200 765 true 284 1770685967118 8080 284 2 Zheh[zdO=www.google.com, zdQ=https://www.google.com] GET /complete/search?client=firefox&channel=ftr&q= true false 200 8197 JSON true 150 1770685967066 8080 144 4 Zheh[zdO=playerthree.online, zdQ=https://playerthree.online] GET /embed/synden/ false false 200 9893 HTML Terra de Pecados - Synden true 272 1770685968680 8080 271 5 Zheh[zdO=tason.me, zdQ=https://tason.me] GET /tU4anh9K0.js false false 200 2008 script js true 262 1770685970072 8080 262 6 Zheh[zdO=playerthree.online, zdQ=https://playerthree.online] GET /favicon.ico false false 404 704 HTML ico true 1279 1770685970788 8080 1279 7 Zheh[zdO=playerthree.online, zdQ=https://playerthree.online] GET /episodio/255703 false false 200 1995 HTML true 263 1770685973574 8080 262 9 Zheh[zdO=iamcdn.net, zdQ=https://iamcdn.net] GET /player-v2/core.bundle.js false false 304 579 script js true 53 1770685975705 8080 53 10 Zheh[zdO=playerembedapi.link, zdQ=https://playerembedapi.link] GET /sw.import.js false false 304 616 script js true 60 1770685976807 8080 60 11 Zheh[zdO=iamcdn.net, zdQ=https://iamcdn.net] GET /player-v2/sw.bundle.js false false 304 579 script js true 57 1770685976949 8080 57 13 Zheh[zdO=dxqmwq9y0.sssrr.org, zdQ=https://dxqmwq9y0.sssrr.org] GET /sora/307308779/M1ZXVG82V3lReTNQemdNUGJ1NEtBQ2Y0YmUrajF4dituYnZHUEZYZW9IekdmVVpmTnc false false 302 679 text true 279 1770685978343 8080 279 14 Zheh[zdO=montgomery-fashion-enabling-determined.trycloudflare.com, zdQ=https://montgomery-fashion-enabling-determined.trycloudflare.com] GET /sora/307308779/M1ZXVG82V3lReTNQemdNUGJ1NEtBQ2Y0YmUrajF4dituYnZHUEZYZW9IekdmVVpmTnc false false 0 0 true 0 1770685979346 8080 0 15 Zheh[zdO=wss.morphify.net, zdQ=https://wss.morphify.net] GET / false false 101 809 true 491 1770685979674 8080 490 16 Zheh[zdO=dxqmwq9y0.sssrr.org, zdQ=https://dxqmwq9y0.sssrr.org] GET /sora/307308779/M1ZXVG82V3lReTNQemdNUGJ1NEtBQ2Y0YmUrajF4dituYnZHUEZYZW9IekdmVVpmTnc false false 302 661 text true 257 1770685980239 8080 257 17 Zheh[zdO=colours-charms-funk-purchases.trycloudflare.com, zdQ=https://colours-charms-funk-purchases.trycloudflare.com] GET /sora/307308779/M1ZXVG82V3lReTNQemdNUGJ1NEtBQ2Y0YmUrajF4dituYnZHUEZYZW9IekdmVVpmTnc false false 0 0 true 0 1770685980621 8080 0
"""

def parse_network_logs(logs):
    """Parse network logs e extrai informações"""
    
    # Regex para extrair domínio e URL
    pattern = r'Zheh\[zdO=([^,]+), zdQ=([^\]]+)\]\s+(\w+)\s+([^\s]+)'
    
    requests = []
    for match in re.finditer(pattern, logs):
        domain = match.group(1)
        base_url = match.group(2)
        method = match.group(3)
        path = match.group(4)
        
        full_url = base_url + path if not path.startswith('http') else path
        
        requests.append({
            'domain': domain,
            'method': method,
            'url': full_url,
            'path': path
        })
    
    return requests

def analyze_requests(requests):
    """Analisa requisições e identifica padrões"""
    
    print("╔════════════════════════════════════════════════════════════╗")
    print("║  🔍 Análise de Logs de Rede                              ║")
    print("╚════════════════════════════════════════════════════════════╝\n")
    
    print(f"📊 Total de requisições capturadas: {len(requests)}\n")
    
    # Agrupar por domínio
    by_domain = {}
    for req in requests:
        domain = req['domain']
        if domain not in by_domain:
            by_domain[domain] = []
        by_domain[domain].append(req)
    
    print("🌐 Requisições por Domínio:")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    for domain, reqs in by_domain.items():
        print(f"\n📍 {domain} ({len(reqs)} requisições)")
        for req in reqs:
            print(f"   {req['method']} {req['path']}")
    
    print("\n" + "="*60)
    print("🎯 ANÁLISE ESPECÍFICA")
    print("="*60 + "\n")
    
    # Analisar playerembedapi.link
    print("1️⃣  PlayerEmbedAPI")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    playerembed_reqs = by_domain.get('playerembedapi.link', [])
    if playerembed_reqs:
        print(f"✅ Encontradas {len(playerembed_reqs)} requisições")
        for req in playerembed_reqs:
            print(f"   {req['method']} {req['url']}")
        print("\n💡 Ação: Procure por requisições XHR/Fetch adicionais")
        print("   Essas são apenas requisições de scripts/assets")
    else:
        print("❌ Nenhuma requisição encontrada")
    
    # Analisar playerthree.online
    print("\n2️⃣  PlayerThree (Site do Player)")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    playerthree_reqs = by_domain.get('playerthree.online', [])
    if playerthree_reqs:
        print(f"✅ Encontradas {len(playerthree_reqs)} requisições")
        for req in playerthree_reqs:
            print(f"   {req['method']} {req['url']}")
        
        # Extrair ID do episódio
        for req in playerthree_reqs:
            if '/episodio/' in req['path']:
                episode_id = req['path'].split('/episodio/')[-1]
                print(f"\n📺 ID do Episódio: {episode_id}")
                print(f"   URL completa: {req['url']}")
    else:
        print("❌ Nenhuma requisição encontrada")
    
    # Analisar iamcdn.net
    print("\n3️⃣  IamCDN (Bundles JavaScript)")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    iamcdn_reqs = by_domain.get('iamcdn.net', [])
    if iamcdn_reqs:
        print(f"✅ Encontradas {len(iamcdn_reqs)} requisições")
        for req in iamcdn_reqs:
            print(f"   {req['method']} {req['url']}")
        print("\n💡 Esses são os bundles JavaScript que contêm o código de criptografia")
    else:
        print("❌ Nenhuma requisição encontrada")
    
    # Analisar sora/cloudflare
    print("\n4️⃣  Sora/Cloudflare (Possível API de Vídeo)")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    sora_reqs = [req for req in requests if 'sora' in req['path']]
    if sora_reqs:
        print(f"✅ Encontradas {len(sora_reqs)} requisições")
        for req in sora_reqs:
            print(f"   {req['method']} {req['url']}")
            
            # Extrair ID
            if '/sora/' in req['path']:
                parts = req['path'].split('/sora/')
                if len(parts) > 1:
                    sora_id = parts[1].split('/')[0]
                    print(f"   📌 Sora ID: {sora_id}")
        
        print("\n💡 Essas requisições podem conter dados do vídeo")
        print("   Tente acessar essas URLs diretamente")
    else:
        print("❌ Nenhuma requisição encontrada")
    
    print("\n" + "="*60)
    print("🚀 PRÓXIMOS PASSOS")
    print("="*60 + "\n")
    
    print("1. CAPTURAR REQUISIÇÕES XHR/FETCH")
    print("   • Abra DevTools (F12)")
    print("   • Vá para Network → XHR")
    print("   • Recarregue a página")
    print("   • Procure por requisições para /api/")
    print()
    
    print("2. TESTAR URLs IDENTIFICADAS")
    print("   • Acesse as URLs do Sora diretamente")
    print("   • Verifique se retornam JSON com dados")
    print()
    
    print("3. USAR CONSOLE DO NAVEGADOR")
    print("   • Cole o código de interceptação (ver CAPTURA_MANUAL.md)")
    print("   • Recarregue a página")
    print("   • Observe as requisições capturadas")
    print()
    
    # Gerar comandos úteis
    print("="*60)
    print("🔧 COMANDOS PARA TESTAR")
    print("="*60 + "\n")
    
    if sora_reqs:
        print("# Testar URLs do Sora:")
        for req in sora_reqs[:3]:  # Primeiras 3
            print(f'curl "{req["url"]}"')
        print()
    
    if playerthree_reqs:
        episode_req = [r for r in playerthree_reqs if '/episodio/' in r['path']]
        if episode_req:
            print("# Acessar episódio:")
            print(f'{episode_req[0]["url"]}')
            print()

def main():
    print("\n" + "="*60)
    print("  🔍 ANÁLISE DE LOGS DE REDE")
    print("="*60 + "\n")
    
    requests = parse_network_logs(NETWORK_LOGS)
    
    if not requests:
        print("❌ Nenhuma requisição encontrada nos logs")
        print()
        print("💡 Como usar este script:")
        print("  1. Copie os logs de rede do navegador")
        print("  2. Cole na variável NETWORK_LOGS neste script")
        print("  3. Execute novamente")
        return
    
    analyze_requests(requests)
    
    print("\n" + "="*60)
    print("📚 DOCUMENTAÇÃO")
    print("="*60 + "\n")
    print("• CAPTURA_MANUAL.md - Guia completo de captura")
    print("• PROXIMOS_PASSOS.txt - Próximas ações")
    print("• STATUS_ATUAL.md - Status do projeto")
    print()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
