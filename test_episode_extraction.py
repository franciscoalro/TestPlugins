import requests
from bs4 import BeautifulSoup
import json

# User-Agent idêntico ao usado no plugin
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0"

def test_playerthree_episode(episode_id):
    """
    Testa a extração de um episódio do PlayerthreeOnline
    Simula exatamente o que o MaxSeriesProvider faz
    """
    print(f"\n{'='*60}")
    print(f"🧪 TESTANDO EPISÓDIO ID: {episode_id}")
    print(f"{'='*60}\n")
    
    # URL do episódio (formato usado pelo plugin)
    base_url = "https://playerthree.online"
    episode_url = f"{base_url}/episodio/{episode_id}"
    
    print(f"📍 URL: {episode_url}")
    
    # Headers idênticos ao plugin
    headers = {
        "User-Agent": USER_AGENT,
        "Referer": "https://www.maxseries.one",
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "*/*",
        "Accept-Language": "pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3"
    }
    
    try:
        # Fazer requisição
        print("🌐 Fazendo requisição...")
        response = requests.get(episode_url, headers=headers, timeout=10)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📏 Tamanho da resposta: {len(response.text)} chars")
        
        # Salvar HTML bruto
        with open(f"episode_{episode_id}_raw.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        print(f"💾 HTML salvo em: episode_{episode_id}_raw.html")
        
        # Parse com BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Procurar data-source (método do plugin)
        print("\n🔍 Procurando por data-source...")
        sources_found = []
        
        # Método 1: Regex no HTML bruto (como o plugin faz)
        import re
        data_source_pattern = re.compile(r'data-source\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)
        matches = data_source_pattern.findall(response.text)
        
        if matches:
            print(f"✅ Encontrado {len(matches)} data-source via REGEX:")
            for i, match in enumerate(matches, 1):
                print(f"   {i}. {match}")
                sources_found.append(match)
        else:
            print("❌ Nenhum data-source encontrado via REGEX")
        
        # Método 2: BeautifulSoup (alternativo)
        print("\n🔍 Procurando por elementos com data-source...")
        elements_with_data_source = soup.find_all(attrs={"data-source": True})
        
        if elements_with_data_source:
            print(f"✅ Encontrado {len(elements_with_data_source)} elementos:")
            for i, elem in enumerate(elements_with_data_source, 1):
                source = elem.get('data-source')
                print(f"   {i}. Tag: {elem.name}, Source: {source}")
                if source not in sources_found:
                    sources_found.append(source)
        else:
            print("❌ Nenhum elemento com data-source encontrado")
        
        # Análise adicional
        print("\n📋 ANÁLISE DO HTML:")
        print(f"   - Total de botões: {len(soup.find_all('button'))}")
        print(f"   - Total de links: {len(soup.find_all('a'))}")
        print(f"   - Total de divs: {len(soup.find_all('div'))}")
        
        # Procurar por iframes (caso seja redirecionamento)
        iframes = soup.find_all('iframe')
        if iframes:
            print(f"\n🖼️ Encontrado {len(iframes)} iframes:")
            for i, iframe in enumerate(iframes, 1):
                print(f"   {i}. {iframe.get('src', 'sem src')}")
        
        # Mostrar primeiros 500 chars do HTML
        print("\n📄 PREVIEW DO HTML (primeiros 500 chars):")
        print("-" * 60)
        print(response.text[:500])
        print("-" * 60)
        
        # Salvar resultado em JSON
        result = {
            "episode_id": episode_id,
            "url": episode_url,
            "status_code": response.status_code,
            "html_size": len(response.text),
            "sources_found": sources_found,
            "total_buttons": len(soup.find_all('button')),
            "total_links": len(soup.find_all('a')),
            "has_iframes": len(iframes) > 0
        }
        
        with open(f"episode_{episode_id}_analysis.json", "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Análise salva em: episode_{episode_id}_analysis.json")
        
        # Conclusão
        print("\n" + "="*60)
        if sources_found:
            print(f"✅ SUCESSO: {len(sources_found)} sources encontradas")
            print("   O problema NÃO é a requisição HTTP.")
            print("   Verifique se o plugin está usando a regex correta.")
        else:
            print("❌ FALHA: Nenhuma source encontrada")
            print("   Possíveis causas:")
            print("   1. O site mudou a estrutura HTML")
            print("   2. A página precisa de JavaScript para carregar")
            print("   3. O site está bloqueando o User-Agent")
        print("="*60)
        
        return sources_found
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        return []

if __name__ == "__main__":
    # Testar com o episódio que você tentou (Breaking Bad)
    # ID 3633 foi o que apareceu nos logs
    episode_id = input("Digite o ID do episódio (ex: 3633 para Breaking Bad): ").strip()
    
    if not episode_id:
        episode_id = "3633"  # Default
    
    sources = test_playerthree_episode(episode_id)
    
    print(f"\n🎯 RESULTADO FINAL: {len(sources)} sources encontradas")
