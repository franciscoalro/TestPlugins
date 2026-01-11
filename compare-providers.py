#!/usr/bin/env python3
"""
Comparar estruturas dos providers AnimesOnlineCC vs MaxSeries
"""

def compare_providers():
    print("🔍 COMPARAÇÃO: AnimesOnlineCC vs MaxSeries")
    print("=" * 50)
    
    print("\n📋 DIFERENÇAS PRINCIPAIS:")
    print("-" * 30)
    
    print("1. SELETOR DE CONTAINER:")
    print("   AnimesOnlineCC: 'div.items article.item'")
    print("   MaxSeries:      'article.item'")
    print("   ❓ MaxSeries pode estar perdendo o container div.items")
    
    print("\n2. FUNÇÃO toSearchResult:")
    print("   AnimesOnlineCC: AnimeSearchResponse")
    print("   MaxSeries:      MovieSearchResponse (newMovieSearchResponse)")
    print("   ❓ Pode ser problema de tipo de resposta")
    
    print("\n3. TRATAMENTO DE URL:")
    print("   AnimesOnlineCC: fixUrl(href)")
    print("   MaxSeries:      if (href.startsWith('http')) href else mainUrl+href")
    print("   ❓ MaxSeries pode ter problema com fixUrl")
    
    print("\n4. TRATAMENTO DE ERRO:")
    print("   AnimesOnlineCC: try/catch com logs detalhados")
    print("   MaxSeries:      sem tratamento de erro")
    print("   ❓ MaxSeries pode estar falhando silenciosamente")
    
    print("\n5. LOGS DE DEBUG:")
    print("   AnimesOnlineCC: Log.d() extensivo")
    print("   MaxSeries:      println() básico")
    print("   ❓ MaxSeries difícil de debuggar")
    
    print("\n💡 CORREÇÕES SUGERIDAS PARA MAXSERIES:")
    print("-" * 40)
    print("1. Adicionar 'div.items' no seletor")
    print("2. Usar fixUrl() ao invés de concatenação manual")
    print("3. Adicionar try/catch com logs")
    print("4. Usar Log.d() ao invés de println()")
    print("5. Verificar se precisa de newAnimeSearchResponse")

if __name__ == "__main__":
    compare_providers()