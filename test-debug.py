#!/usr/bin/env python3
import requests
import re

def debug_maxseries():
    print("🔍 DEBUG MAXSERIES - Estrutura HTML")
    print("=" * 50)
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    try:
        response = session.get("https://www.maxseries.one", timeout=15)
        html = response.text
        
        print(f"Status: {response.status_code}")
        print(f"HTML Length: {len(html)} chars")
        
        # Verificar diferentes padrões de item
        patterns = [
            r'<article[^>]*class="[^"]*item[^"]*"',
            r'<div[^>]*class="[^"]*item[^"]*"',
            r'<article[^>]*>',
            r'<div[^>]*class="[^"]*movie[^"]*"',
            r'<div[^>]*class="[^"]*post[^"]*"'
        ]
        
        for i, pattern in enumerate(patterns):
            matches = re.findall(pattern, html, re.IGNORECASE)
            print(f"Padrão {i+1}: {len(matches)} matches - {pattern}")
        
        # Procurar links de conteúdo
        link_patterns = [
            r'href="([^"]*(?:series|filme|movie)[^"]*)"',
            r'href="(https://www\.maxseries\.one/[^"]+)"'
        ]
        
        all_links = []
        for pattern in link_patterns:
            links = re.findall(pattern, html, re.IGNORECASE)
            all_links.extend(links)
        
        print(f"\n🔗 Links encontrados: {len(all_links)}")
        for i, link in enumerate(all_links[:5]):  # Mostrar apenas os 5 primeiros
            print(f"   {i+1}. {link}")
        
        # Testar primeiro link se existir
        if all_links:
            test_url = all_links[0]
            print(f"\n🎬 Testando: {test_url}")
            
            try:
                item_response = session.get(test_url, timeout=10)
                if item_response.status_code == 200:
                    print("✅ Página acessível")
                    
                    # Procurar iframe
                    iframe_matches = re.findall(r'<iframe[^>]+src="([^"]+)"', item_response.text)
                    print(f"🎯 iframes encontrados: {len(iframe_matches)}")
                    
                    for iframe in iframe_matches[:3]:
                        if iframe.startswith('//'):
                            iframe = 'https:' + iframe
                        print(f"   - {iframe}")
                        
                        # Identificar tipo
                        if "megaembed" in iframe.lower():
                            print("     Tipo: MegaEmbed ✅")
                        elif "playerembedapi" in iframe.lower():
                            print("     Tipo: PlayerEmbedAPI ✅")
                        elif any(d in iframe.lower() for d in ["myvidplay", "bysebuho", "g9r6", "doodstream"]):
                            print("     Tipo: DoodStream Clone ✅")
                        else:
                            print("     Tipo: Outro")
                else:
                    print(f"❌ Erro ao acessar: {item_response.status_code}")
            except Exception as e:
                print(f"❌ Erro: {e}")
        
        # Verificar se site está usando Cloudflare
        if "cloudflare" in html.lower() or "cf-ray" in str(response.headers):
            print("\n⚠️ Site protegido por Cloudflare")
        
        # Verificar se tem JavaScript pesado
        if "eval(function(p,a,c,k,e" in html:
            print("🔧 Site usa JavaScript empacotado")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")

if __name__ == "__main__":
    debug_maxseries()