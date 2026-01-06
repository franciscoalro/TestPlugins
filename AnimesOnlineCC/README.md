# AnimesOnlineCC Provider para Cloudstream

## 📺 Sobre
Plugin para o Cloudstream3 que permite assistir animes do site **Animes Online CC** (https://animesonlinecc.to/).

## ✨ Funcionalidades Implementadas

### 1. **Página Inicial (Home)**
- Exibe animes recentes
- Categorias: Ação, Aventura, Comédia
- Paginação automática

### 2. **Busca**
- Busca por nome do anime
- Resultados com poster e título

### 3. **Detalhes do Anime**
- Título completo
- Poster/Capa
- Descrição/Sinopse
- Gêneros
- Lista completa de episódios

### 4. **Reprodução**
- Extração automática de links de vídeo
- Suporte a múltiplos players
- Compatível com extractors do Cloudstream

## 🔧 Estrutura Técnica

### Seletores CSS Utilizados
```kotlin
// Lista de animes
"div.items article.item"

// Título
"h3"

// Link do anime
"a"

// Poster
"img"

// Lista de episódios
"ul.episodios li"

// Player de vídeo
"iframe"
```

### Fluxo de Dados
1. **Home/Busca** → Extrai cards de anime
2. **Detalhes** → Extrai informações + lista de episódios
3. **Episódio** → Extrai iframe do player
4. **Extractor** → Processa o link final do vídeo

## 📦 Como Compilar

### Windows
```bash
.\gradlew.bat AnimesOnlineCC:make
```

### Linux/Mac
```bash
./gradlew AnimesOnlineCC:make
```

O arquivo `.cs3` será gerado em `AnimesOnlineCC/build/`

## 📲 Como Instalar

1. Compile o plugin usando o comando acima
2. Copie o arquivo `.cs3` para o seu dispositivo Android
3. No Cloudstream, vá em **Configurações → Extensões**
4. Clique em **Instalar extensão local**
5. Selecione o arquivo `.cs3`

## 🐛 Troubleshooting

### Plugin não aparece após instalação
- Verifique se concedeu permissão de "Todos os arquivos" ao app
- Reinicie o Cloudstream

### Vídeos não carregam
- O site pode ter mudado a estrutura HTML
- Verifique se o extractor do player está disponível no Cloudstream

### Erro de compilação
- Certifique-se de ter o JDK 8 ou superior instalado
- Execute `.\gradlew.bat clean` antes de compilar novamente

## 📝 Notas de Desenvolvimento

### Possíveis Melhorias Futuras
- [ ] Adicionar mais categorias na home
- [ ] Implementar filtro por ano/status
- [ ] Adicionar suporte a favoritos
- [ ] Melhorar extração de metadados (rating, ano, estúdio)
- [ ] Adicionar suporte a legendas externas

### Estrutura do Site (Última verificação: 2026-01-05)
- **Home:** Lista de animes em cards
- **Busca:** `/?s=query`
- **Anime:** `/anime/nome-do-anime/`
- **Episódio:** `/episodio/nome-episodio-X/`
- **Player:** Iframe embutido (geralmente Blogger ou similares)

## 📄 Licença
Este plugin é fornecido "como está" para fins educacionais. O desenvolvedor não se responsabiliza pelo uso indevido.

## 🤝 Contribuições
Sinta-se livre para melhorar este código e adicionar novas funcionalidades!
