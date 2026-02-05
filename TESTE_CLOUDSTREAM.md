# Teste no CloudStream3

## Links para testar

### Repositorio:
```
https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/repo.json
```

### Download direto do plugin:
```
https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/MaxSeries.cs3
```

## Verificacao dos arquivos

### repo.json
- Formato: JSON valido
- manifestVersion: 1
- pluginLists: aponta para plugins.json

### plugins.json
- Formato: Array (lista) de plugins
- Sem BOM (Byte Order Mark)
- 1 plugin: MaxSeries v264
- fileSize: 747480 bytes

### MaxSeries.cs3
- Formato: ZIP (AAR renomeado)
- Tamanho: 747480 bytes
- Contem: AndroidManifest.xml, classes.jar, R.txt, META-INF
- classes.jar: 319 classes compiladas
- Main class: com/franciscoalro/maxseries/MaxSeriesPlugin.class

## Como testar

1. Abra o CloudStream3
2. Va em Configuracoes > Extensoes
3. Toque no botao "+" (Adicionar repositorio)
4. Cole: `https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/repo.json`
5. Toque em "Adicionar"
6. O plugin "MaxSeries" deve aparecer na lista
7. Toque em "Instalar"

## Se nao funcionar

1. Verifique se o CloudStream3 tem permissao de internet
2. Tente baixar o arquivo .cs3 diretamente no navegador do celular
3. Instale manualmente: Configuracoes > Extensoes > Instalar de arquivo
4. Limpe o cache do CloudStream3 e tente novamente

## Estrutura do Plugin

O plugin segue a estrutura oficial do CloudStream3:

```
MaxSeriesPlugin.kt:
- Anotacao: @CloudstreamPlugin
- Classe: BasePlugin()
- Metodo: load()
- Registra: MaxSeriesProvider (MainAPI)
- Registra: 8 extractors (ExtractorAPI)

MaxSeriesProvider.kt:
- Extende: MainAPI()
- Propriedades: mainUrl, name, lang, hasMainPage, supportedTypes
- Metodos: getMainPage(), search(), load(), loadLinks()
```

Todas as classes estao compiladas corretamente no classes.jar.
