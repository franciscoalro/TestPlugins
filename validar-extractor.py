#!/usr/bin/env python3
"""
Validador de Extractors para CloudStream
Testa se um extractor vai funcionar ANTES do build
"""

import requests
import re
import sys
import json
from urllib.parse import urlparse

class ExtractorValidator:
    def __init__(self):
        self.results = {
            "url_acessivel": False,
            "encontrou_video": False,
            "formato_suportado": False,
            "headers_necessarios": [],
            "urls_encontradas": [],
            "recomendacao": ""
        }
    
    def validar(self, url_extractor, referer=None):
        """Valida se um extractor vai funcionar"""
        print(f"\n{'='*60}")
        print(f"🔍 VALIDANDO EXTRACTOR")
        print(f"{'='*60}")
        print(f"URL: {url_extractor}")
        print(f"Referer: {referer or 'N/A'}")
        
        # 1. Testar se URL é acessível
        print(f"\n[1/5] Testando acessibilidade...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        if referer:
            headers['Referer'] = referer
            
        try:
            response = requests.get(url_extractor, headers=headers, timeout=15)
            self.results["url_acessivel"] = response.status_code == 200
            print(f"   Status: {response.status_code}")
            print(f"   Tamanho: {len(response.text)} bytes")
            
            if response.status_code != 200:
                print(f"   ❌ URL não acessível!")
                return self.results
        except Exception as e:
            print(f"   ❌ Erro: {e}")
            return self.results
        
        html = response.text
        
        # 2. Procurar URLs de vídeo
        print(f"\n[2/5] Procurando URLs de vídeo...")
        padroes = [
            (r'(https?://[^"\s<>]+\.m3u8[^"\s<>]*)', 'M3U8'),
            (r'(https?://[^"\s<>]+\.mp4[^"\s<>]*)', 'MP4'),
            (r'(https?://storage\.googleapis\.com/[^"\s<>]+)', 'Google Cloud Storage'),
            (r'(https?://[^"\s<>]*cloudatacdn\.com[^"\s<>]*)', 'CloudAtaCDN'),
            (r'(https?://[^"\s<>]*iamcdn\.net[^"\s<>]*)', 'IAMCDN'),
            (r'(https?://[^"\s<>]*sssrr\.org[^"\s<>]*)', 'SSSRR CDN'),
            (r'"file"\s*:\s*"([^"]+\.m3u8[^"]*)"', 'JSON file M3U8'),
            (r'"file"\s*:\s*"([^"]+\.mp4[^"]*)"', 'JSON file MP4'),
            (r'source\s*:\s*["\']([^"\']+)["\']', 'source JS'),
        ]
        
        for pattern, tipo in padroes:
            matches = re.findall(pattern, html, re.IGNORECASE)
            for match in matches:
                if match not in self.results["urls_encontradas"]:
                    self.results["urls_encontradas"].append({
                        "url": match,
                        "tipo": tipo
                    })
                    print(f"   ✅ [{tipo}] {match[:80]}...")
        
        self.results["encontrou_video"] = len(self.results["urls_encontradas"]) > 0
        
        if not self.results["encontrou_video"]:
            print(f"   ⚠️ Nenhuma URL de vídeo encontrada no HTML")
            print(f"   💡 Pode precisar de JavaScript (WebView necessário)")
        
        # 3. Verificar formato
        print(f"\n[3/5] Verificando formatos suportados...")
        formatos_suportados = ['.m3u8', '.mp4', 'googleapis.com']
        for url_info in self.results["urls_encontradas"]:
            url = url_info["url"]
            for fmt in formatos_suportados:
                if fmt in url.lower():
                    self.results["formato_suportado"] = True
                    print(f"   ✅ Formato suportado: {fmt}")
                    break
        
        # 4. Detectar headers necessários
        print(f"\n[4/5] Detectando headers necessários...")
        if 'googleapis.com' in html:
            self.results["headers_necessarios"].append("Referer (para Google Cloud Storage)")
            print(f"   ℹ️ Google Cloud Storage detectado - precisa de Referer")
        
        if referer:
            self.results["headers_necessarios"].append(f"Referer: {referer}")
        
        # 5. Gerar recomendação
        print(f"\n[5/5] Gerando recomendação...")
        if self.results["formato_suportado"]:
            self.results["recomendacao"] = "✅ EXTRACTOR VAI FUNCIONAR!"
            if len(self.results["urls_encontradas"]) == 0:
                self.results["recomendacao"] += "\n   ⚠️ Mas precisa de WebView (JavaScript necessário)"
        else:
            self.results["recomendacao"] = "❌ EXTRACTOR PODE NÃO FUNCIONAR"
            if not self.results["url_acessivel"]:
                self.results["recomendacao"] += "\n   - URL não está acessível"
            if not self.results["encontrou_video"]:
                self.results["recomendacao"] += "\n   - Não encontrou vídeo no HTML (pode precisar de JS)"
        
        return self.results
    
    def gerar_codigo_kotlin(self):
        """Gera código Kotlin base para o extractor"""
        if not self.results["encontrou_video"]:
            return "// Não foi possível gerar código - nenhuma URL encontrada"
        
        urls = self.results["urls_encontradas"]
        exemplo_url = urls[0]["url"] if urls else ""
        
        codigo = f'''class MeuExtractor : ExtractorApi() {{
    override val name = "MeuExtractor"
    override val mainUrl = "{urlparse(exemplo_url).netloc}"
    override val requiresReferer = true
    
    override suspend fun getUrl(
        url: String,
        referer: String?,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ) {{
        val response = app.get(url, headers = mapOf(
            "User-Agent" to "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        ))
        
        // Padrões encontrados no teste:
'''
        for i, url_info in enumerate(urls[:3], 1):
            pattern = url_info["url"].split('/')[-1] if '/' in url_info["url"] else url_info["url"]
            codigo += f'''        // {i}. Tipo: {url_info["tipo"]}
        // Exemplo: {url_info["url"][:60]}...
'''
        
        codigo += '''    }
}'''
        return codigo

def main():
    if len(sys.argv) < 2:
        print("Uso: python validar-extractor.py <URL_DO_EXTRACTOR> [REFERER]")
        print("\nExemplos:")
        print("  python validar-extractor.py 'https://playerembedapi.link/?v=4PHWs34H0'")
        print("  python validar-extractor.py 'https://megaembed.link/#3wnuij' 'https://playerthree.online/'")
        sys.exit(1)
    
    url = sys.argv[1]
    referer = sys.argv[2] if len(sys.argv) > 2 else None
    
    validator = ExtractorValidator()
    resultados = validator.validar(url, referer)
    
    # Relatório final
    print(f"\n{'='*60}")
    print(f"📊 RELATÓRIO FINAL")
    print(f"{'='*60}")
    print(f"URL Acessível: {'✅' if resultados['url_acessivel'] else '❌'}")
    print(f"Encontrou Vídeo: {'✅' if resultados['encontrou_video'] else '❌'}")
    print(f"Formato Suportado: {'✅' if resultados['formato_suportado'] else '❌'}")
    print(f"\n📝 RECOMENDAÇÃO:")
    print(resultados['recomendacao'])
    
    if resultados['urls_encontradas']:
        print(f"\n🔗 URLs ENCONTRADAS ({len(resultados['urls_encontradas'])}):")
        for url_info in resultados['urls_encontradas'][:5]:
            print(f"   - [{url_info['tipo']}] {url_info['url'][:70]}...")
    
    # Gerar código Kotlin
    print(f"\n{'='*60}")
    print(f"📝 CÓDIGO KOTLIN BASE (para referência)")
    print(f"{'='*60}")
    print(validator.gerar_codigo_kotlin())
    
    # Salvar resultados
    with open('validacao_resultado.json', 'w') as f:
        json.dump(resultados, f, indent=2)
    print(f"\n💾 Resultados salvos em: validacao_resultado.json")

if __name__ == "__main__":
    main()
