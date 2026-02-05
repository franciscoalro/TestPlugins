# Solucao: Plugin Nao Aparece no CloudStream

## Diagnostico

O build do plugin esta **100% correto**. Todos os arquivos foram validados:

- ✅ MaxSeries.cs3 (747KB) - Válido com 331 classes
- ✅ plugins.json - Válido, versao 263
- ✅ repo.json - Válido, apontando para plugins.json
- ✅ Commit da biblioteca: 8a4480dc42 (21 Jan 2026) - Atual

## Problema

O build gera um arquivo **.aar** (Android Archive) que e renomeado para **.cs3**. 
Este e o formato correto para plugins CloudStream.

## Solucoes

### 1. Verifique a URL do Repositorio

No CloudStream, adicione EXATAMENTE esta URL:

```
https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/repo.json
```

**Nao use:**
- ❌ https://github.com/franciscoalro/TestPlugins (URL do GitHub)
- ❌ https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/plugins.json (arquivo errado)
- ❌ https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/MaxSeries.cs3 (arquivo do plugin)

### 2. Limpe o Cache do CloudStream

1. Feche o CloudStream completamente
2. Vá em Configuracoes do Android > Aplicativos > CloudStream
3. Toque em "Armazenamento" > "Limpar Cache"
4. Abra o CloudStream novamente
5. Adicione o repositorio novamente

### 3. Remova e Readicione o Repositorio

1. No CloudStream, vá em Configuracoes > Extensoes
2. Encontre "MaxSeries" ou "franciscoalro/TestPlugins"
3. Toque e segure > Remover
4. Toque em "Adicionar Repositorio"
5. Cole: `https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/repo.json`
6. Toque em Adicionar

### 4. Verifique a Versao do CloudStream

O plugin requer CloudStream versao **4.x** ou superior.

1. No CloudStream, vá em Configuracoes > Sobre
2. Verifique a versao
3. Se for 3.x ou anterior, atualize o app

### 5. Verifique Conexao com Internet

1. Teste a URL no navegador do celular:
   ```
   https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/repo.json
   ```
2. Deve mostrar o conteudo JSON
3. Se nao carregar, verifique sua conexao

### 6. Verifique Permissoes do CloudStream

1. Configuracoes do Android > Aplicativos > CloudStream
2. Permissoes > Internet (deve estar ativada)
3. Permissoes > Armazenamento (deve estar ativada)

### 7. Instale Manualmente (Alternativa)

Se o repositorio nao funcionar, instale o arquivo .cs3 manualmente:

1. Baixe o arquivo:
   ```
   https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/MaxSeries.cs3
   ```
2. No CloudStream: Configuracoes > Extensoes > Instalar do arquivo
3. Selecione o arquivo baixado

## Verificacao Final

Apos seguir os passos acima, o plugin deve aparecer em:
- **Configuracoes > Extensoes** 
- Nome: **MaxSeries**
- Versao: **263**
- Descricao: "PlayerEmbedAPI Otimizado"

## Ainda com Problemas?

Verifique os logs do CloudStream:
1. Configuracoes > Desenvolvedor > Logs (se disponivel)
2. Procure por erros relacionados a "MaxSeries" ou "TestPlugins"

Ou tente:
- Reiniciar o celular
- Reinstalar o CloudStream
- Usar uma versao diferente do CloudStream (Pre-release ou Stable)

---

**Nota:** O arquivo .cs3 é um arquivo .aar (Android Archive) renomeado. 
Este é o formato correto para plugins CloudStream 3+.
