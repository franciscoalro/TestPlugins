#!/usr/bin/env python3
"""
Teste específico do PlayterThree AJAX
Simula exatamente o que o MaxSeries faz
"""

import requests
from bs4 import BeautifulSoup
import re

def test_maxseries_flow():
    """Simula o fluxo exato do MaxSeries"""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'
    })
    
    # 1. Testar uma página real do MaxSeries
    episode_url = "https://www.maxseries.one/episodio/breaking-bad-1x1/"
    
    print(f"🔍 Testando: {episode_url}")
    
    try:
        # Carregar página principal
        response = session.get(episode_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Encontrar iframe
        iframe = soup.find('iframe')
        if not iframe:
            print("❌ Nenhum iframe encontrado")
            return
            
        iframe_src = iframe.get('src', '')
        if iframe_src.startswith('//'):
            iframe_src = 'https:' + iframe_src
            
        print(f"🖼️ Iframe: {iframe_src}")
        
        # Verificar se é playerthree e tem formato correto
        if 'playerthree' in iframe_src:
            # Extrair ID do episódio do formato esperado pelo MaxSeries
            # O MaxSeries espera: data.contains("#") && data.contains("playerthree")
            # E procura por: Regex("#\\d+_(\\d+)")
            
            print(f"📋 URL de dados atual: {episode_url}")
            print(f"🔍 Procurando padrão #\\d+_(\\d+) na URL...")
            
            # O problema pode estar aqui - vamos verificar se a URL tem o formato correto
            pattern = r"#\d+_(\d+)"
            match = re.search(pattern, episode_url)
            
            if match:
                ep_id = match.group(1)
                print(f"✅ Episode ID encontrado: {ep_id}")
                
                # Testar AJAX call como o MaxSeries faz
                ajax_url = f"https://playerthree.online/episodio/{ep_id}"
                print(f"🌐 Testando AJAX: {ajax_url}")
                
                ajax_response = session.get(
                    ajax_url,
                    headers={
                        "Referer": episode_url,
                        "X-Requested-With": "XMLHttpRequest"
                    }
                )
                
                print(f"📄 AJAX Status: {ajax_response.status_code}")
                print(f"📏 AJAX Size: {len(ajax_response.text)} chars")
                
                if ajax_response.status_code == 200:
                    ajax_soup = BeautifulSoup(ajax_response.text, 'html.parser')
                    
                    # Procurar botões com data-source
                    buttons = ajax_soup.select("button[data-source]")
                    print(f"🔘 Botões data-source encontrados: {len(buttons)}")
                    
                    for i, btn in enumerate(buttons):
                        src = btn.get('data-source', '')
                        text = btn.get_text(strip=True)
                        print(f"   {i+1}. {text}: {src}")
                        
                        # Verificar se é MegaEmbed
                        if 'megaembed' in src.lower():
                            print(f"   ✅ MegaEmbed encontrado: {src}")
                    
                    if not buttons:
                        print("⚠️ Nenhum botão data-source encontrado no AJAX")
                        # Salvar resposta para análise
                        with open('ajax_response.html', 'w', encoding='utf-8') as f:
                            f.write(ajax_response.text)
                        print("💾 Resposta AJAX salva em: ajax_response.html")
                        
                        # Procurar outros padrões
                        print("🔍 Procurando outros padrões...")
                        all_buttons = ajax_soup.find_all('button')
                        print(f"   Total de botões: {len(all_buttons)}")
                        
                        for btn in all_buttons:
                            attrs = dict(btn.attrs) if btn.attrs else {}
                            text = btn.get_text(strip=True)
                            if attrs or text:
                                print(f"   - '{text}': {attrs}")
                
            else:
                print(f"❌ Episode ID não encontrado na URL: {episode_url}")
                print("⚠️ O MaxSeries espera URLs no formato: ...#123_456")
                print("🔧 Isso pode explicar por que MegaEmbed não aparece!")
                
                # Vamos verificar se há outro padrão na URL
                print(f"\n🔍 Analisando URL completa para outros padrões...")
                
                # Talvez o ID esteja em outro lugar
                # Vamos carregar o iframe diretamente
                print(f"🖼️ Carregando iframe diretamente: {iframe_src}")
                
                iframe_response = session.get(iframe_src, headers={"Referer": episode_url})
                print(f"📄 Iframe Status: {iframe_response.status_code}")
                
                if iframe_response.status_code == 200:
                    iframe_soup = BeautifulSoup(iframe_response.text, 'html.parser')
                    
                    # Procurar por IDs de episódio no iframe
                    iframe_html = iframe_response.text
                    
                    # Padrões possíveis
                    id_patterns = [
                        r'episodio["\s]*:["\s]*["\']?(\d+)',
                        r'episode["\s]*:["\s]*["\']?(\d+)',
                        r'data-episode[^>]*["\'](\d+)',
                        r'/episodio/(\d+)',
                        r'ep_id["\s]*=["\s]*["\']?(\d+)'
                    ]
                    
                    found_ids = []
                    for pattern in id_patterns:
                        matches = re.findall(pattern, iframe_html, re.IGNORECASE)
                        if matches:
                            found_ids.extend(matches)
                            print(f"   Padrão '{pattern}': {matches}")
                    
                    if found_ids:
                        # Testar com o primeiro ID encontrado
                        test_id = found_ids[0]
                        print(f"\n🧪 Testando com ID encontrado: {test_id}")
                        
                        ajax_url = f"https://playerthree.online/episodio/{test_id}"
                        ajax_response = session.get(
                            ajax_url,
                            headers={
                                "Referer": episode_url,
                                "X-Requested-With": "XMLHttpRequest"
                            }
                        )
                        
                        print(f"📄 AJAX Status: {ajax_response.status_code}")
                        
                        if ajax_response.status_code == 200:
                            ajax_soup = BeautifulSoup(ajax_response.text, 'html.parser')
                            buttons = ajax_soup.select("button[data-source]")
                            print(f"🔘 Botões encontrados: {len(buttons)}")
                            
                            for btn in buttons:
                                src = btn.get('data-source', '')
                                text = btn.get_text(strip=True)
                                print(f"   - {text}: {src}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    print("🧪 TESTE PLAYERTHREE AJAX - Simulando MaxSeries")
    print("=" * 60)
    test_maxseries_flow()