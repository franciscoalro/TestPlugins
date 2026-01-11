#!/usr/bin/env python3
"""
Teste de Detecção MegaEmbed - MaxSeries v47
Verifica se URLs MegaEmbed estão sendo encontradas nas páginas
"""

import requests
import re
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin, urlparse

class MegaEmbedTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
    def test_maxseries_episode(self, episode_url):
        """Testa uma página de episódio do MaxSeries"""
        print(f"🔍 Testando: {episode_url}")
        
        try:
            # 1. Carregar página principal
            response = self.session.get(episode_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            print(f"📄 Status: {response.status_code}")
            print(f"📏 Tamanho: {len(response.text)} chars")
            
            # 2. Procurar iframe principal
            iframe = soup.find('iframe')
            if not iframe:
                print("❌ Nenhum iframe encontrado na página principal")
                return False
                
            iframe_src = iframe.get('src', '')
            if iframe_src.startswith('//'):
                iframe_src = 'https:' + iframe_src
            elif not iframe_src.startswith('http'):
                iframe_src = urljoin(episode_url, iframe_src)
                
            print(f"🖼️ Iframe encontrado: {iframe_src}")
            
            # 3. Carregar iframe (playerthree)
            if 'playerthree' in iframe_src:
                return self.test_playerthree_iframe(iframe_src, episode_url)
            else:
                print(f"⚠️ Iframe não é playerthree: {iframe_src}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao testar episódio: {e}")
            return False
    
    def test_playerthree_iframe(self, iframe_url, referer):
        """Testa iframe do playerthree para encontrar fontes"""
        print(f"\n🎬 Testando PlayterThree: {iframe_url}")
        
        try:
            # Carregar iframe
            response = self.session.get(iframe_url, headers={'Referer': referer})
            soup = BeautifulSoup(response.text, 'html.parser')
            
            print(f"📄 Status iframe: {response.status_code}")
            
            # Procurar botões de fonte
            buttons = soup.find_all('button', {'data-source': True})
            if not buttons:
                # Tentar outros seletores
                buttons = soup.find_all('a', {'data-source': True})
                buttons.extend(soup.find_all('div', {'data-source': True}))
            
            print(f"🔘 Botões encontrados: {len(buttons)}")
            
            sources = []
            megaembed_found = False
            
            for i, btn in enumerate(buttons):
                source_url = btn.get('data-source', '')
                source_text = btn.get_text(strip=True)
                
                print(f"   {i+1}. {source_text}: {source_url}")
                
                if source_url:
                    sources.append({
                        'name': source_text,
                        'url': source_url,
                        'type': self.detect_source_type(source_url)
                    })
                    
                    if 'megaembed' in source_url.lower():
                        megaembed_found = True
                        print(f"   ✅ MegaEmbed detectado: {source_url}")
            
            # Se não encontrou botões, procurar diretamente no HTML
            if not sources:
                print("\n🔍 Procurando URLs diretamente no HTML...")
                sources = self.extract_urls_from_html(response.text)
                
                for source in sources:
                    if 'megaembed' in source['url'].lower():
                        megaembed_found = True
                        print(f"   ✅ MegaEmbed encontrado no HTML: {source['url']}")
            
            # Testar uma URL MegaEmbed se encontrada
            if megaembed_found:
                megaembed_urls = [s['url'] for s in sources if 'megaembed' in s['url'].lower()]
                if megaembed_urls:
                    print(f"\n🧪 Testando MegaEmbed: {megaembed_urls[0]}")
                    self.test_megaembed_url(megaembed_urls[0])
            else:
                print("\n❌ Nenhuma URL MegaEmbed encontrada!")
            
            return {
                'iframe_url': iframe_url,
                'sources_found': len(sources),
                'megaembed_found': megaembed_found,
                'sources': sources
            }
            
        except Exception as e:
            print(f"❌ Erro ao testar iframe: {e}")
            return False
    
    def extract_urls_from_html(self, html):
        """Extrai URLs de vídeo diretamente do HTML"""
        sources = []
        
        # Padrões para encontrar URLs
        patterns = [
            r'https?://[^"\s]+megaembed[^"\s]*',
            r'https?://[^"\s]+playerembedapi[^"\s]*',
            r'https?://[^"\s]+myvidplay[^"\s]*',
            r'https?://[^"\s]+bysebuho[^"\s]*',
            r'https?://[^"\s]+g9r6[^"\s]*'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            for match in matches:
                # Limpar URL
                clean_url = match.rstrip('",\'};')
                sources.append({
                    'name': self.detect_source_type(clean_url),
                    'url': clean_url,
                    'type': self.detect_source_type(clean_url)
                })
        
        return sources
    
    def detect_source_type(self, url):
        """Detecta o tipo de fonte pela URL"""
        url_lower = url.lower()
        
        if 'megaembed' in url_lower:
            return 'MegaEmbed'
        elif 'playerembedapi' in url_lower:
            return 'PlayerEmbedAPI'
        elif 'myvidplay' in url_lower:
            return 'MyVidplay'
        elif 'bysebuho' in url_lower:
            return 'Bysebuho'
        elif 'g9r6' in url_lower:
            return 'G9R6'
        elif 'dood' in url_lower:
            return 'DoodStream'
        else:
            return 'Unknown'
    
    def test_megaembed_url(self, megaembed_url):
        """Testa uma URL MegaEmbed específica"""
        print(f"\n🔬 Análise detalhada MegaEmbed: {megaembed_url}")
        
        try:
            response = self.session.get(megaembed_url)
            print(f"📄 Status: {response.status_code}")
            print(f"📏 Tamanho: {len(response.text)} chars")
            
            # Procurar padrões específicos do MegaEmbed
            html = response.text
            
            # 1. Procurar JavaScript de criptografia
            if 'CryptoJS' in html or 'AES' in html:
                print("🔐 Criptografia detectada (CryptoJS/AES)")
            
            # 2. Procurar URLs de vídeo
            video_patterns = [
                r'https?://[^"\']+\.m3u8[^"\']*',
                r'https?://[^"\']+\.mp4[^"\']*',
                r'https?://storage\.googleapis\.com[^"\']*',
                r'https?://[^"\']*cloudatacdn[^"\']*'
            ]
            
            for pattern in video_patterns:
                matches = re.findall(pattern, html)
                if matches:
                    print(f"🎬 URLs de vídeo encontradas ({len(matches)}):")
                    for match in matches[:3]:  # Mostrar apenas 3
                        print(f"   - {match}")
            
            # 3. Verificar se precisa de JavaScript
            if 'eval(' in html or 'function(' in html:
                print("📜 JavaScript complexo detectado - pode precisar de WebView")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao testar MegaEmbed: {e}")
            return False

def main():
    print("🧪 TESTE DE DETECÇÃO MEGAEMBED - MaxSeries v47")
    print("=" * 60)
    
    tester = MegaEmbedTester()
    
    # URLs de teste do MaxSeries
    test_urls = [
        "https://www.maxseries.one/episodio/the-walking-dead-1x1/",
        "https://www.maxseries.one/episodio/breaking-bad-1x1/",
        "https://www.maxseries.one/episodio/game-of-thrones-1x1/"
    ]
    
    results = []
    
    for url in test_urls:
        print(f"\n{'='*60}")
        result = tester.test_maxseries_episode(url)
        results.append({
            'url': url,
            'result': result
        })
        print(f"{'='*60}")
    
    # Resumo final
    print(f"\n📊 RESUMO DOS TESTES:")
    print(f"{'='*60}")
    
    megaembed_found_count = 0
    for result in results:
        if isinstance(result['result'], dict) and result['result'].get('megaembed_found'):
            megaembed_found_count += 1
            print(f"✅ {result['url']} - MegaEmbed encontrado")
        else:
            print(f"❌ {result['url']} - MegaEmbed NÃO encontrado")
    
    print(f"\n📈 Taxa de detecção MegaEmbed: {megaembed_found_count}/{len(test_urls)} ({megaembed_found_count/len(test_urls)*100:.1f}%)")
    
    if megaembed_found_count == 0:
        print("\n⚠️ PROBLEMA IDENTIFICADO:")
        print("   - MegaEmbed não está sendo encontrado nas páginas")
        print("   - Pode ser problema na detecção de fontes")
        print("   - Verificar se o site mudou a estrutura")

if __name__ == "__main__":
    main()