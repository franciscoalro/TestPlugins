#!/usr/bin/env python3
"""
Analisador HAR - MaxSeries
Extrair informações valiosas do arquivo HAR do navegador
"""

import json
import re
from urllib.parse import urlparse, parse_qs
import os

class MaxSeriesHARAnalyzer:
    def __init__(self, har_file_path):
        self.har_file_path = har_file_path
        self.har_data = None
        
    def load_har_file(self):
        """Carregar arquivo HAR"""
        try:
            if not os.path.exists(self.har_file_path):
                print(f"❌ Arquivo não encontrado: {self.har_file_path}")
                return False
            
            with open(self.har_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Tentar carregar como JSON
            try:
                self.har_data = json.loads(content)
                print(f"✅ Arquivo HAR carregado: {len(content)} chars")
                return True
            except json.JSONDecodeError:
                # Se não for JSON válido, pode ser texto puro com dados HAR
                print("⚠️ Não é JSON válido, tentando extrair dados...")
                self.extract_from_text(content)
                return True
                
        except Exception as e:
            print(f"❌ Erro ao carregar arquivo: {e}")
            return False
    
    def extract_from_text(self, content):
        """Extrair dados de texto puro"""
        print("🔍 Analisando conteúdo como texto...")
        
        # Procurar URLs de vídeo no texto
        video_patterns = [
            r'https?://[^"\s]+\.m3u8[^"\s]*',
            r'https?://[^"\s]+\.mp4[^"\s]*',
            r'https?://[^"\s]+\.ts[^"\s]*',
            r'https?://[^"\s]+/playlist\.m3u8[^"\s]*'
        ]
        
        found_videos = []
        for pattern in video_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            found_videos.extend(matches)
        
        if found_videos:
            print(f"🎥 URLs de vídeo encontradas no texto: {len(found_videos)}")
            for i, url in enumerate(set(found_videos)):
                print(f"   {i+1}. {url}")
        
        # Procurar requisições específicas
        self.analyze_text_requests(content)
    
    def analyze_text_requests(self, content):
        """Analisar requisições no texto"""
        print("\n🔍 Procurando padrões de requisições...")
        
        # Padrões importantes
        patterns = {
            'PlayerEmbedAPI': r'playerembedapi\.link[^"\s]*',
            'MegaEmbed': r'megaembed\.link[^"\s]*',
            'PlayThree': r'playerthree\.online[^"\s]*',
            'AJAX Episodio': r'/episodio/\d+',
            'M3U8 Streams': r'https?://[^"\s]+\.m3u8[^"\s]*',
            'MP4 Videos': r'https?://[^"\s]+\.mp4[^"\s]*',
            'CDN URLs': r'https?://cdn[^"\s]+',
            'Stream URLs': r'https?://[^"\s]*stream[^"\s]*'
        }
        
        for name, pattern in patterns.items():
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                print(f"\n📡 {name}: {len(matches)} encontradas")
                for match in set(matches)[:5]:  # Primeiras 5 únicas
                    print(f"   - {match}")
    
    def analyze_har_data(self):
        """Analisar dados HAR estruturados"""
        if not self.har_data:
            print("❌ Dados HAR não carregados")
            return
        
        print("\n🔍 ANÁLISE DETALHADA DO HAR")
        print("=" * 50)
        
        # Extrair entradas
        entries = []
        if 'log' in self.har_data and 'entries' in self.har_data['log']:
            entries = self.har_data['log']['entries']
        
        print(f"📊 Total de requisições: {len(entries)}")
        
        # Analisar requisições
        video_requests = []
        ajax_requests = []
        player_requests = []
        
        for entry in entries:
            request = entry.get('request', {})
            response = entry.get('response', {})
            url = request.get('url', '')
            method = request.get('method', '')
            status = response.get('status', 0)
            
            # Classificar requisições
            if any(ext in url.lower() for ext in ['.m3u8', '.mp4', '.ts']):
                video_requests.append({
                    'url': url,
                    'method': method,
                    'status': status,
                    'size': response.get('bodySize', 0)
                })
            
            elif '/episodio/' in url or 'ajax' in url.lower():
                ajax_requests.append({
                    'url': url,
                    'method': method,
                    'status': status,
                    'headers': request.get('headers', [])
                })
            
            elif any(player in url.lower() for player in ['playerembedapi', 'megaembed', 'playerthree']):
                player_requests.append({
                    'url': url,
                    'method': method,
                    'status': status
                })
        
        # Mostrar resultados
        self.show_video_requests(video_requests)
        self.show_ajax_requests(ajax_requests)
        self.show_player_requests(player_requests)
        
        # Extrair informações valiosas
        self.extract_valuable_info(entries)
    
    def show_video_requests(self, video_requests):
        """Mostrar requisições de vídeo"""
        print(f"\n🎥 REQUISIÇÕES DE VÍDEO ({len(video_requests)})")
        print("-" * 40)
        
        if not video_requests:
            print("❌ Nenhuma requisição de vídeo encontrada")
            return
        
        for i, req in enumerate(video_requests[:10]):  # Primeiras 10
            print(f"{i+1}. {req['method']} {req['status']} - {req['url']}")
            if req['size'] > 0:
                print(f"   📊 Tamanho: {req['size']} bytes")
    
    def show_ajax_requests(self, ajax_requests):
        """Mostrar requisições AJAX"""
        print(f"\n📡 REQUISIÇÕES AJAX ({len(ajax_requests)})")
        print("-" * 40)
        
        for i, req in enumerate(ajax_requests[:5]):  # Primeiras 5
            print(f"{i+1}. {req['method']} {req['status']} - {req['url']}")
            
            # Mostrar headers importantes
            for header in req['headers']:
                name = header.get('name', '').lower()
                value = header.get('value', '')
                if name in ['referer', 'x-requested-with', 'authorization']:
                    print(f"   📋 {name}: {value}")
    
    def show_player_requests(self, player_requests):
        """Mostrar requisições de players"""
        print(f"\n🎮 REQUISIÇÕES DE PLAYERS ({len(player_requests)})")
        print("-" * 40)
        
        for i, req in enumerate(player_requests[:5]):  # Primeiras 5
            print(f"{i+1}. {req['method']} {req['status']} - {req['url']}")
    
    def extract_valuable_info(self, entries):
        """Extrair informações valiosas para o plugin"""
        print(f"\n💎 INFORMAÇÕES VALIOSAS PARA O PLUGIN")
        print("=" * 50)
        
        # Procurar padrões específicos
        patterns_found = {
            'video_urls': [],
            'api_endpoints': [],
            'auth_tokens': [],
            'headers_importantes': [],
            'cookies': []
        }
        
        for entry in entries:
            request = entry.get('request', {})
            response = entry.get('response', {})
            url = request.get('url', '')
            
            # URLs de vídeo diretas
            if any(ext in url.lower() for ext in ['.m3u8', '.mp4']):
                patterns_found['video_urls'].append(url)
            
            # Endpoints de API
            if any(keyword in url.lower() for keyword in ['api', 'ajax', 'episodio']):
                patterns_found['api_endpoints'].append(url)
            
            # Headers importantes
            for header in request.get('headers', []):
                name = header.get('name', '').lower()
                value = header.get('value', '')
                if name in ['authorization', 'x-api-key', 'x-auth-token']:
                    patterns_found['auth_tokens'].append(f"{name}: {value}")
                elif name in ['referer', 'origin', 'user-agent']:
                    patterns_found['headers_importantes'].append(f"{name}: {value}")
            
            # Cookies importantes
            for cookie in request.get('cookies', []):
                name = cookie.get('name', '')
                if any(keyword in name.lower() for keyword in ['auth', 'token', 'session']):
                    patterns_found['cookies'].append(f"{name}: {cookie.get('value', '')}")
        
        # Mostrar resultados
        for category, items in patterns_found.items():
            if items:
                print(f"\n🔍 {category.upper().replace('_', ' ')}:")
                unique_items = list(set(items))[:5]  # Primeiras 5 únicas
                for item in unique_items:
                    print(f"   - {item}")
        
        # Gerar recomendações
        self.generate_recommendations(patterns_found)
    
    def generate_recommendations(self, patterns):
        """Gerar recomendações para melhorar o plugin"""
        print(f"\n🚀 RECOMENDAÇÕES PARA O PLUGIN")
        print("=" * 50)
        
        recommendations = []
        
        if patterns['video_urls']:
            recommendations.append("✅ URLs de vídeo encontradas - plugin pode extrair diretamente")
        
        if patterns['api_endpoints']:
            recommendations.append("📡 Endpoints de API identificados - implementar requisições específicas")
        
        if patterns['auth_tokens']:
            recommendations.append("🔐 Tokens de autenticação encontrados - adicionar ao plugin")
        
        if patterns['headers_importantes']:
            recommendations.append("📋 Headers importantes identificados - incluir nas requisições")
        
        if not patterns['video_urls']:
            recommendations.append("⚠️ Nenhuma URL de vídeo direta - focar em extractors JavaScript")
        
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")
        
        # Código de exemplo
        if patterns['video_urls'] or patterns['api_endpoints']:
            print(f"\n💻 CÓDIGO DE EXEMPLO PARA O PLUGIN:")
            print("```kotlin")
            
            if patterns['headers_importantes']:
                print("// Headers importantes identificados:")
                for header in patterns['headers_importantes'][:3]:
                    name, value = header.split(': ', 1)
                    print(f'val headers = mapOf("{name}" to "{value}")')
            
            if patterns['api_endpoints']:
                print("\n// Endpoints de API encontrados:")
                for endpoint in patterns['api_endpoints'][:2]:
                    print(f'val apiUrl = "{endpoint}"')
            
            print("```")

def main():
    # Caminho do arquivo HAR
    har_file_path = r"C:\Users\KYTHOURS\Documents\harmaxseries.txt"
    
    print("🔍 ANALISADOR HAR - MAXSERIES")
    print("=" * 50)
    print(f"📁 Arquivo: {har_file_path}")
    print()
    
    # Criar analisador
    analyzer = MaxSeriesHARAnalyzer(har_file_path)
    
    # Carregar e analisar
    if analyzer.load_har_file():
        if analyzer.har_data:
            analyzer.analyze_har_data()
        
        print(f"\n🎯 CONCLUSÃO:")
        print("As informações extraídas podem ser usadas para:")
        print("1. 🎥 Identificar URLs de vídeo reais")
        print("2. 📡 Entender requisições AJAX necessárias")
        print("3. 🔐 Descobrir headers/tokens de autenticação")
        print("4. 🚀 Melhorar o plugin MaxSeries v16.0")
    else:
        print("❌ Falha ao carregar arquivo HAR")

if __name__ == "__main__":
    main()