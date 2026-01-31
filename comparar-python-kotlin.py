#!/usr/bin/env python3
"""
Comparador Python vs Kotlin para Extractors
Mostra lado a lado como converter lógica Python para Kotlin
"""

import requests
import re
import json
import base64

class PythonToKotlinComparator:
    """Compara implementação Python com Kotlin equivalente"""
    
    def __init__(self):
        self.comparisons = []
    
    def teste_http(self, url, referer=None):
        """Compara requisição HTTP"""
        print("\n" + "="*70)
        print("🌐 TESTE 1: Requisição HTTP")
        print("="*70)
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        if referer:
            headers['Referer'] = referer
        
        try:
            response = requests.get(url, headers=headers, timeout=15)
            
            print(f"\n🐍 PYTHON:")
            print(f"   import requests")
            print(f"   response = requests.get('{url}', headers={headers}, timeout=15)")
            print(f"   html = response.text  # {len(response.text)} chars")
            print(f"   status = response.status_code  # {response.status_code}")
            
            print(f"\n🤖 KOTLIN EQUIVALENTE:")
            print(f"   val response = app.get(")
            print(f"       url = \"{url}\",")
            print(f"       headers = mapOf(")
            for k, v in headers.items():
                print(f"           \"{k}\" to \"{v}\"")
            print(f"       )")
            print(f"   )")
            print(f"   val html = response.text  // {len(response.text)} chars")
            print(f"   val status = response.code  // {response.status_code}")
            
            return response.text
        except Exception as e:
            print(f"❌ Erro: {e}")
            return None
    
    def teste_regex(self, html, pattern, description):
        """Compara regex Python vs Kotlin"""
        print(f"\n" + "="*70)
        print(f"🔍 TESTE: {description}")
        print("="*70)
        
        print(f"\n🐍 PYTHON:")
        print(f"   import re")
        print(f"   pattern = r'{pattern}'")
        print(f"   match = re.search(pattern, html)")
        print(f"   if match:")
        print(f"       valor = match.group(1)")
        
        match = re.search(pattern, html, re.IGNORECASE)
        if match:
            print(f"\n   ✅ Resultado: {match.group(1)[:50]}...")
        else:
            print(f"\n   ❌ Não encontrado")
        
        print(f"\n🤖 KOTLIN EQUIVALENTE:")
        print(f"   val pattern = Regex(\"\"\"{pattern}\"\"\")")
        print(f"   val match = pattern.find(html)")
        print(f"   val valor = match?.groupValues?.get(1)")
        
        if match:
            print(f"\n   ✅ Resultado seria: {match.group(1)[:50]}...")
        else:
            print(f"\n   ❌ Não encontraria")
        
        return match.group(1) if match else None
    
    def teste_json(self, json_str):
        """Compara parsing JSON"""
        print(f"\n" + "="*70)
        print(f"📦 TESTE: Parsing JSON")
        print("="*70)
        
        print(f"\n🐍 PYTHON:")
        print(f"   import json")
        print(f"   data = json.loads(json_str)")
        print(f"   valor = data['chave']")
        
        try:
            data = json.loads(json_str)
            print(f"\n   ✅ JSON válido com {len(data)} campos")
        except:
            print(f"\n   ❌ JSON inválido")
        
        print(f"\n🤖 KOTLIN EQUIVALENTE:")
        print(f"   val mapper = JsonHelper.mapper  // ObjectMapper")
        print(f"   val data = mapper.readTree(json_str)")
        print(f"   val valor = data.get(\"chave\").asText()")
    
    def teste_base64(self, b64_string):
        """Compara decodificação Base64"""
        print(f"\n" + "="*70)
        print(f"🔐 TESTE: Decodificação Base64")
        print("="*70)
        
        print(f"\n🐍 PYTHON:")
        print(f"   import base64")
        print(f"   decoded = base64.b64decode(b64_string)")
        print(f"   text = decoded.decode('utf-8')")
        
        try:
            decoded = base64.b64decode(b64_string)
            print(f"\n   ✅ Decodificado: {len(decoded)} bytes")
            print(f"   Texto: {decoded[:100].decode('utf-8', errors='ignore')}...")
        except:
            print(f"\n   ❌ Base64 inválido")
        
        print(f"\n🤖 KOTLIN EQUIVALENTE:")
        print(f"   import android.util.Base64")
        print(f"   val decoded = Base64.decode(b64_string, Base64.DEFAULT)")
        print(f"   val text = String(decoded, Charsets.UTF_8)")
    
    def analisar_playerembedapi(self, url):
        """Análise completa do PlayerEmbedAPI"""
        print("\n" + "="*70)
        print(f"🎯 ANÁLISE COMPLETA: PlayerEmbedAPI")
        print(f"URL: {url}")
        print("="*70)
        
        # 1. HTTP
        html = self.teste_http(url, referer="https://playerthree.online")
        if not html:
            return
        
        # 2. Procurar base64 (padrão do PlayerEmbedAPI)
        b64_pattern = r'const datas = "([A-Za-z0-9+/=]+)"'
        b64_data = self.teste_regex(html, b64_pattern, "Extração Base64 'datas'")
        
        if b64_data:
            self.teste_base64(b64_data)
            
            decoded = base64.b64decode(b64_data)
            json_str = decoded.decode('utf-8', errors='ignore')
            
            try:
                data = json.loads(json_str)
                print(f"\n📋 Campos encontrados no JSON:")
                for key in data.keys():
                    print(f"   - {key}: {str(data[key])[:50]}...")
            except:
                pass
        
        # 3. Procurar URL diretas
        print(f"\n" + "="*70)
        print("🔗 URLs DE VÍDEO DIRETAS:")
        print("="*70)
        
        video_patterns = [
            (r'(https?://[^"\s<>]+\.m3u8[^"\s<>]*)', 'M3U8'),
            (r'(https?://[^"\s<>]+\.mp4[^"\s<>]*)', 'MP4'),
            (r'(https?://storage\.googleapis\.com/[^"\s<>]+)', 'GCS'),
            (r'(https?://[^"\s<>]*sssrr\.org[^"\s<>]*)', 'SSSRR'),
        ]
        
        for pattern, tipo in video_patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            if matches:
                print(f"\n   [{tipo}] {len(matches)} encontradas:")
                for m in matches[:3]:
                    print(f"      - {m[:70]}...")
    
    def analisar_megaembed(self, video_id):
        """Análise completa do MegaEmbed"""
        url = f"https://megaembed.link/#{video_id}"
        
        print("\n" + "="*70)
        print(f"🎯 ANÁLISE COMPLETA: MegaEmbed")
        print(f"URL: {url}")
        print("="*70)
        
        # 1. Testar API
        api_url = f"https://megaembed.link/api/v1/info?id={video_id}"
        print(f"\n📡 Testando API: {api_url}")
        
        try:
            response = requests.get(api_url, headers={
                'User-Agent': 'Mozilla/5.0',
                'Referer': url,
                'Origin': 'https://megaembed.link'
            }, timeout=10)
            
            print(f"   Status: {response.status_code}")
            print(f"   Resposta: {response.text[:200]}...")
            
            # Verificar se é JSON ou criptografado
            try:
                data = response.json()
                print(f"   ✅ API retorna JSON válido")
                if 'url' in data:
                    print(f"   🎬 URL direta: {data['url'][:80]}...")
            except:
                print(f"   ⚠️ API retorna dados criptografados ou não-JSON")
                print(f"   💡 Necessita de WebView para decriptar")
                
        except Exception as e:
            print(f"   ❌ Erro na API: {e}")

def main():
    print("="*70)
    print("🔄 COMPARADOR PYTHON vs KOTLIN PARA EXTRACTORS")
    print("="*70)
    
    comparador = PythonToKotlinComparator()
    
    # Exemplo 1: PlayerEmbedAPI
    print("\n\n" + "="*70)
    print("EXEMPLO 1: PlayerEmbedAPI")
    print("="*70)
    comparador.analisar_playerembedapi("https://playerembedapi.link/?v=4PHWs34H0")
    
    # Exemplo 2: MegaEmbed
    print("\n\n" + "="*70)
    print("EXEMPLO 2: MegaEmbed")
    print("="*70)
    comparador.analisar_megaembed("3wnuij")
    
    # Resumo
    print("\n\n" + "="*70)
    print("📊 RESUMO DA CONVERSÃO")
    print("="*70)
    print("""
🐍 PYTHON → 🤖 KOTLIN

requests.get() → app.get()
response.text → response.text
response.json() → parseJson<JsonNode>(response.text)
re.search() → Regex().find()
base64.b64decode() → Base64.decode()
json.loads() → mapper.readTree()

⚡ DICAS:
- Python é melhor para prototipar e testar
- Kotlin precisa lidar com coroutines (suspend functions)
- No Kotlin, use 'runCatching { }' para tratamento de erros
- Sempre use 'newExtractorLink()' ao invés de 'ExtractorLink()'
""")

if __name__ == "__main__":
    main()
