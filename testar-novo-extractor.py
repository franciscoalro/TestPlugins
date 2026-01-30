#!/usr/bin/env python3
"""
Template completo para testar um novo extractor antes de implementar em Kotlin
"""

import requests
import re
import json
from urllib.parse import urljoin, urlparse

class NovoExtractorTester:
    """
    Classe para testar um novo extractor de vídeo
    
    Uso:
        tester = NovoExtractorTester("https://site-exemplo.com/embed/12345")
        resultado = tester.testar_completo()
    """
    
    def __init__(self, url_embed):
        self.url_embed = url_embed
        self.html = None
        self.resultados = {
            "url_acessivel": False,
            "titulo": None,
            "urls_video": [],
            "scripts_encontrados": [],
            "apis_descobertas": [],
            "requer_javascript": False,
            "recomendacao_implementacao": ""
        }
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
        }
    
    def testar_acessibilidade(self):
        """Testa se a URL do embed é acessível"""
        print("\n" + "="*60)
        print("🔍 TESTE 1: Acessibilidade da URL")
        print("="*60)
        
        try:
            print(f"URL: {self.url_embed}")
            response = requests.get(
                self.url_embed, 
                headers=self.headers, 
                timeout=15,
                allow_redirects=True
            )
            
            self.resultados["url_acessivel"] = response.status_code == 200
            
            print(f"Status Code: {response.status_code}")
            print(f"Content-Type: {response.headers.get('Content-Type', 'N/A')}")
            print(f"Tamanho: {len(response.text)} caracteres")
            print(f"Redirecionamentos: {len(response.history)}")
            
            if response.history:
                print("\nCadeia de redirecionamentos:")
                for resp in response.history:
                    print(f"  → {resp.status_code}: {resp.url}")
                print(f"  → Final: {response.url}")
            
            self.html = response.text
            
            # Extrair título
            title_match = re.search(r'<title[^>]*>(.*?)</title>', self.html, re.IGNORECASE | re.DOTALL)
            if title_match:
                self.resultados["titulo"] = title_match.group(1).strip()
                print(f"Título: {self.resultados['titulo']}")
            
            return True
            
        except requests.exceptions.Timeout:
            print("❌ TIMEOUT: Site demorou mais de 15s para responder")
            return False
        except requests.exceptions.ConnectionError:
            print("❌ ERRO DE CONEXÃO: Não foi possível conectar ao site")
            return False
        except Exception as e:
            print(f"❌ ERRO: {e}")
            return False
    
    def analisar_html(self):
        """Analisa o HTML em busca de padrões"""
        if not self.html:
            return
        
        print("\n" + "="*60)
        print("📄 TESTE 2: Análise do HTML")
        print("="*60)
        
        # Salvar HTML para análise manual
        filename = f"analise_{urlparse(self.url_embed).netloc.replace('.', '_')}.html"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(self.html)
        print(f"💾 HTML salvo em: {filename}")
        
        # Procurar por elementos de vídeo
        elementos_video = re.findall(r'<video[^>]*>.*?</video>', self.html, re.IGNORECASE | re.DOTALL)
        elementos_source = re.findall(r'<source[^>]+>', self.html, re.IGNORECASE)
        
        print(f"\nElementos encontrados:")
        print(f"  <video>: {len(elementos_video)}")
        print(f"  <source>: {len(elementos_source)}")
        
        if elementos_video:
            print("\n  Exemplos de <video>:")
            for i, vid in enumerate(elementos_video[:2]):
                print(f"    {i+1}. {vid[:150]}...")
    
    def procurar_urls_video(self):
        """Procura URLs de vídeo no HTML e scripts"""
        print("\n" + "="*60)
        print("🎬 TESTE 3: URLs de Vídeo")
        print("="*60)
        
        if not self.html:
            print("❌ HTML não disponível")
            return
        
        # Padrões comuns de URLs de vídeo
        padroes = [
            (r'(https?://[^"\s<>]+\.m3u8[^"\s<>]*)', 'M3U8 (HLS)'),
            (r'(https?://[^"\s<>]+\.mp4[^"\s<>]*)', 'MP4 direto'),
            (r'(https?://[^"\s<>]+\.txt[^"\s<>]*(?:master|index)[^"\s<>]*)', 'TXT Master'),
            (r'"file"\s*:\s*"(https?://[^"]+)"', 'JSON file'),
            (r'src\s*:\s*["\'](https?://[^"\']+)["\']', 'src atributo'),
            (r'(https?://storage\.googleapis\.com/[^"\s<>]+)', 'Google Cloud Storage'),
            (r'(https?://[^"\s<>]*cdn[^"\s<>]*/[^"\s<>]*\.(?:m3u8|mp4|txt))', 'CDN genérica'),
            (r'(https?://[^"\s<>]*\.(?:top|shop|cyou|sbs)/[^"\s<>]*\.(?:m3u8|txt))', 'CDN TLD específica'),
        ]
        
        urls_encontradas = []
        
        for pattern, descricao in padroes:
            matches = re.findall(pattern, self.html, re.IGNORECASE)
            for match in matches:
                if match not in [u['url'] for u in urls_encontradas]:
                    urls_encontradas.append({
                        'url': match,
                        'tipo': descricao
                    })
                    print(f"\n✅ [{descricao}]")
                    print(f"   URL: {match[:80]}...")
        
        self.resultados["urls_video"] = urls_encontradas
        
        if not urls_encontradas:
            print("⚠️ Nenhuma URL de vídeo encontrada no HTML")
            print("💡 Possíveis causas:")
            print("   - Vídeo é carregado via JavaScript")
            print("   - Requer interação do usuário (clique)")
            print("   - URL está em arquivo JS externo")
            print("   - Dados estão criptografados")
            self.resultados["requer_javascript"] = True
    
    def analisar_scripts(self):
        """Analisa scripts JavaScript"""
        print("\n" + "="*60)
        print("📜 TESTE 4: Análise de Scripts")
        print("="*60)
        
        if not self.html:
            return
        
        # Extrair scripts inline
        scripts_inline = re.findall(r'<script[^>]*>(.*?)</script>', self.html, re.DOTALL | re.IGNORECASE)
        
        # Extrair URLs de scripts externos
        scripts_externos = re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', self.html, re.IGNORECASE)
        
        print(f"Scripts inline: {len(scripts_inline)}")
        print(f"Scripts externos: {len(scripts_externos)}")
        
        # Procurar por padrões interessantes nos scripts
        padroes_interessantes = [
            (r'eval\s*\(', 'eval() - possível ofuscação'),
            (r'atob\s*\(', 'atob() - decodificação base64'),
            (r'JSON\.parse\s*\(', 'JSON.parse()'),
            (r'\.m3u8', 'Referência a M3U8'),
            (r'videoUrl\s*=', 'Variável videoUrl'),
            (r'source\s*:\s*', 'Propriedade source'),
            (r'fetch\s*\(', 'Chamada fetch()'),
            (r'XMLHttpRequest', 'Requisição XHR'),
            (r'axios|jquery', 'Biblioteca HTTP'),
            (r'AES|CryptoJS|crypto', 'Criptografia'),
            (r'encrypt|decrypt', 'Funções de cripto'),
        ]
        
        scripts_com_padroes = []
        
        for i, script in enumerate(scripts_inline):
            if len(script) > 50:  # Ignorar scripts vazios
                for pattern, descricao in padroes_interessantes:
                    if re.search(pattern, script, re.IGNORECASE):
                        if i not in scripts_com_padroes:
                            scripts_com_padroes.append(i)
                            print(f"\n📜 Script {i+1} contém: {descricao}")
                            print(f"   Trecho: {script[:200]}...")
        
        self.resultados["scripts_encontrados"] = scripts_com_padroes
    
    def procurar_apis(self):
        """Procura por endpoints de API"""
        print("\n" + "="*60)
        print("🔌 TESTE 5: APIs e Endpoints")
        print("="*60)
        
        if not self.html:
            return
        
        # Padrões de API
        api_patterns = [
            r'(https?://[^"\s<>]+/api/[^"\s<>]*)',
            r'(https?://[^"\s<>]+/v\d+/[^"\s<>]*)',
            r'["\']([^"\']*api[^"\']*\?[^"\']*)["\']',
            r'(https?://[^"\s<>]+\.json[^"\s<>]*)',
        ]
        
        apis_encontradas = []
        
        for pattern in api_patterns:
            matches = re.findall(pattern, self.html, re.IGNORECASE)
            for match in matches:
                if match not in apis_encontradas:
                    apis_encontradas.append(match)
                    print(f"\n🔗 API: {match[:80]}...")
                    
                    # Tentar fazer requisição de teste
                    try:
                        resp = requests.get(match, headers=self.headers, timeout=5)
                        print(f"   Status: {resp.status_code}")
                        print(f"   Tipo: {resp.headers.get('Content-Type', 'N/A')}")
                        
                        # Tentar parsear JSON
                        try:
                            data = resp.json()
                            print(f"   ✅ Resposta JSON válida")
                            if isinstance(data, dict):
                                print(f"   Campos: {list(data.keys())}")
                        except:
                            print(f"   📄 Resposta: {resp.text[:100]}...")
                            
                    except Exception as e:
                        print(f"   ⚠️ Erro ao testar: {e}")
        
        self.resultados["apis_descobertas"] = apis_encontradas
    
    def validar_urls_encontradas(self):
        """Valida se as URLs de vídeo são acessíveis"""
        print("\n" + "="*60)
        print("✅ TESTE 6: Validação de URLs")
        print("="*60)
        
        for url_info in self.resultados["urls_video"]:
            url = url_info['url']
            print(f"\nTestando: {url[:60]}...")
            
            try:
                # HEAD request para não baixar o vídeo inteiro
                resp = requests.head(url, headers=self.headers, timeout=10, allow_redirects=True)
                
                print(f"   Status: {resp.status_code}")
                
                if resp.status_code == 200:
                    content_type = resp.headers.get('Content-Type', 'unknown')
                    content_length = resp.headers.get('Content-Length', 'unknown')
                    
                    print(f"   Content-Type: {content_type}")
                    print(f"   Tamanho: {content_length} bytes")
                    
                    url_info['valido'] = True
                    url_info['content_type'] = content_type
                else:
                    print(f"   ❌ Status não é 200")
                    url_info['valido'] = False
                    
            except Exception as e:
                print(f"   ❌ Erro: {e}")
                url_info['valido'] = False
    
    def gerar_recomendacao(self):
        """Gera recomendação de implementação"""
        print("\n" + "="*60)
        print("💡 RECOMENDAÇÃO DE IMPLEMENTAÇÃO")
        print("="*60)
        
        urls_validas = [u for u in self.resultados["urls_video"] if u.get('valido')]
        
        if urls_validas:
            print("\n✅ IMPLEMENTAÇÃO DIRETA (sem WebView)")
            print("-" * 40)
            print("O extractor pode ser implementado com HTTP simples:")
            print("")
            print("1. Fazer request para URL do embed")
            print("2. Extrair URL de vídeo do HTML com Regex")
            print("3. Retornar link via callback.invoke()")
            print("")
            print("Exemplo de código Kotlin:")
            print("-" * 40)
            
            # Gerar código exemplo
            exemplo_url = urls_validas[0]['url']
            pattern_sugerido = exemplo_url.split('/')[-1].split('?')[0]
            
            print(f'''class MeuExtractor : ExtractorApi() {{
    override var name = "MeuExtractor"
    override var mainUrl = "{urlparse(self.url_embed).netloc}"
    override val requiresReferer = true

    override suspend fun getUrl(url: String, referer: String?, 
                                subtitleCallback: (SubtitleFile) -> Unit,
                                callback: (ExtractorLink) -> Unit) {{
        
        val response = app.get(url, headers = mapOf(
            "User-Agent" to "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        ))
        
        val videoRegex = Regex("""({exemplo_url[:30]}[^\\"\\s]+)""")
        val match = videoRegex.find(response.text)
        
        match?.groupValues?.get(1)?.let {{ videoUrl ->
            callback.invoke(
                newExtractorLink(
                    source = name,
                    name = "$name Auto",
                    url = videoUrl,
                    type = ExtractorLinkType.VIDEO
                ) {{
                    this.referer = url
                }}
            )
        }}
    }}
}}''')
            
        elif self.resultados["requer_javascript"]:
            print("\n⚠️ IMPLEMENTAÇÃO COM WEBVIEW NECESSÁRIA")
            print("-" * 40)
            print("O site carrega o vídeo via JavaScript:")
            print("")
            print("Opções:")
            print("1. Usar WebViewResolver do CloudStream")
            print("2. Implementar WebView manual com interceptação")
            print("3. Analisar APIs internas do site")
            print("")
            print("Próximos passos:")
            print("- Abrir URL no navegador com DevTools")
            print("- Analisar Network tab para encontrar API")
            print("- Ou usar Burp Suite para interceptar requisições")
            
        else:
            print("\n❌ NÃO FOI POSSÍVEL DETERMINAR MÉTODO")
            print("-" * 40)
            print("Sugestões:")
            print("- Verificar se URL do embed está correta")
            print("- Testar com headers diferentes")
            print("- Analisar com Burp Suite ou similar")
    
    def salvar_relatorio(self):
        """Salva relatório completo"""
        filename = f"relatorio_{urlparse(self.url_embed).netloc.replace('.', '_')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.resultados, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Relatório salvo em: {filename}")
    
    def testar_completo(self):
        """Executa todos os testes"""
        print("\n" + "="*60)
        print("🧪 TESTE COMPLETO DE EXTRACTOR")
        print(f"URL: {self.url_embed}")
        print("="*60)
        
        if not self.testar_acessibilidade():
            print("\n❌ Não foi possível acessar a URL. Teste abortado.")
            return self.resultados
        
        self.analisar_html()
        self.procurar_urls_video()
        self.analisar_scripts()
        self.procurar_apis()
        
        if self.resultados["urls_video"]:
            self.validar_urls_encontradas()
        
        self.gerar_recomendacao()
        self.salvar_relatorio()
        
        print("\n" + "="*60)
        print("✅ TESTE CONCLUÍDO")
        print("="*60)
        
        return self.resultados


def main():
    """Uso via linha de comando"""
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python testar-novo-extractor.py <URL_DO_EMBED>")
        print("")
        print("Exemplos:")
        print("  python testar-novo-extractor.py 'https://playerembedapi.link/?v=4PHWs34H0'")
        print("  python testar-novo-extractor.py 'https://megaembed.link/#3wnuij'")
        sys.exit(1)
    
    url = sys.argv[1]
    tester = NovoExtractorTester(url)
    tester.testar_completo()


if __name__ == "__main__":
    main()
