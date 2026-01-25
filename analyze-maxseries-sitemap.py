#!/usr/bin/env python3
"""
Analisa o sitemap do MaxSeries para descobrir novas funcionalidades
"""

import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from collections import defaultdict

def analyze_sitemap():
    print("🗺️ ANÁLISE DO SITEMAP DO MAXSERIES")
    print("="*80)
    
    base_url = "https://www.maxseries.pics"
    sitemap_url = f"{base_url}/sitemap_index.xml"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0'
    }
    
    try:
        print(f"\n📥 Baixando sitemap: {sitemap_url}")
        response = requests.get(sitemap_url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Erro: HTTP {response.status_code}")
            return
        
        print(f"✅ Sitemap baixado ({len(response.text)} bytes)\n")
        
        # Parse XML
        root = ET.fromstring(response.content)
        
        # Namespace do sitemap
        ns = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        
        # Encontrar todos os sitemaps
        sitemaps = root.findall('.//sm:loc', ns)
        
        print(f"📋 Sitemaps encontrados: {len(sitemaps)}\n")
        
        all_urls = []
        categories = defaultdict(list)
        
        for sitemap in sitemaps:
            sitemap_url = sitemap.text
            print(f"🔍 Analisando: {sitemap_url}")
            
            try:
                sub_response = requests.get(sitemap_url, headers=headers, timeout=10)
                sub_root = ET.fromstring(sub_response.content)
                
                urls = sub_root.findall('.//sm:loc', ns)
                print(f"   📄 URLs: {len(urls)}")
                
                for url in urls:
                    url_text = url.text
                    all_urls.append(url_text)
                    
                    # Categorizar URLs
                    if '/filmes/' in url_text:
                        categories['filmes'].append(url_text)
                    elif '/series/' in url_text:
                        categories['series'].append(url_text)
                    elif '/generos/' in url_text:
                        categories['generos'].append(url_text)
                    elif '/lancamentos' in url_text:
                        categories['lancamentos'].append(url_text)
                    elif '/populares' in url_text:
                        categories['populares'].append(url_text)
                    elif '/ano/' in url_text:
                        categories['anos'].append(url_text)
                    elif '/elenco/' in url_text or '/ator/' in url_text:
                        categories['elenco'].append(url_text)
                    else:
                        categories['outros'].append(url_text)
                
            except Exception as e:
                print(f"   ⚠️ Erro: {e}")
        
        print(f"\n{'='*80}")
        print("📊 RESUMO DAS CATEGORIAS")
        print(f"{'='*80}\n")
        
        for cat, urls in sorted(categories.items(), key=lambda x: len(x[1]), reverse=True):
            print(f"📁 {cat.upper()}: {len(urls)} URLs")
            
            # Mostrar exemplos
            if urls:
                print(f"   Exemplos:")
                for url in urls[:3]:
                    print(f"   • {url}")
                print()
        
        # Descobrir novos gêneros
        print(f"{'='*80}")
        print("🎭 GÊNEROS DISPONÍVEIS")
        print(f"{'='*80}\n")
        
        generos_unicos = set()
        for url in categories['generos']:
            # Extrair nome do gênero da URL
            parts = url.split('/generos/')
            if len(parts) > 1:
                genero = parts[1].rstrip('/')
                generos_unicos.add(genero)
        
        for genero in sorted(generos_unicos):
            print(f"  • {genero}")
        
        # Descobrir anos disponíveis
        if categories['anos']:
            print(f"\n{'='*80}")
            print("📅 ANOS DISPONÍVEIS")
            print(f"{'='*80}\n")
            
            anos_unicos = set()
            for url in categories['anos']:
                parts = url.split('/ano/')
                if len(parts) > 1:
                    ano = parts[1].rstrip('/')
                    anos_unicos.add(ano)
            
            for ano in sorted(anos_unicos, reverse=True):
                print(f"  • {ano}")
        
        # Sugestões de melhorias
        print(f"\n{'='*80}")
        print("💡 SUGESTÕES DE MELHORIAS PARA O PLUGIN")
        print(f"{'='*80}\n")
        
        suggestions = []
        
        # Verificar se há categorias não implementadas
        if categories['lancamentos']:
            suggestions.append("✨ Adicionar categoria 'Lançamentos'")
        
        if categories['populares']:
            suggestions.append("✨ Adicionar categoria 'Populares'")
        
        if categories['anos']:
            suggestions.append("✨ Adicionar filtro por ano")
        
        if categories['elenco']:
            suggestions.append("✨ Adicionar busca por ator/elenco")
        
        # Verificar gêneros não implementados
        generos_implementados = {'acao', 'comedia', 'drama', 'terror', 'romance', 'animacao'}
        generos_faltando = generos_unicos - generos_implementados
        
        if generos_faltando:
            suggestions.append(f"✨ Adicionar gêneros faltando: {', '.join(sorted(generos_faltando))}")
        
        if suggestions:
            for suggestion in suggestions:
                print(f"  {suggestion}")
        else:
            print("  ✅ Plugin está completo!")
        
        # Estatísticas finais
        print(f"\n{'='*80}")
        print("📈 ESTATÍSTICAS")
        print(f"{'='*80}\n")
        print(f"  Total de URLs: {len(all_urls)}")
        print(f"  Filmes: {len(categories['filmes'])}")
        print(f"  Séries: {len(categories['series'])}")
        print(f"  Gêneros únicos: {len(generos_unicos)}")
        
    except Exception as e:
        print(f"❌ Erro ao analisar sitemap: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_sitemap()
