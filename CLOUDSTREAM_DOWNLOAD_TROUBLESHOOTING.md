# Troubleshooting: Cloudstream não consegue baixar plugins

## 🔧 Correções Aplicadas

### 1. ✅ URLs Simplificados
- **Antes**: `refs/heads/main/builds/`
- **Depois**: `main/builds/`
- **Motivo**: Alguns clientes HTTP têm problemas com URLs longos

### 2. ✅ Codificação JSON Corrigida
- Removidos caracteres especiais das descrições
- Salvo com UTF-8 sem BOM
- Formato JSON validado

### 3. ✅ Tamanhos de Arquivo Atualizados
- Sincronizados os tamanhos no plugins.json com os arquivos reais
- Eliminados warnings de checksum mismatch

## 🔗 Nova URL do Repositório
```
https://raw.githubusercontent.com/franciscoalro/CloudstreamRepo/main/builds/repo.json
```

## 🛠️ Passos para Resolver no Cloudstream

### 1. Limpar Cache
1. Vá em **Configurações** > **Geral**
2. Role até **Cache** 
3. Toque em **Limpar Cache**
4. Reinicie o app

### 2. Remover e Re-adicionar Repositório
1. Vá em **Configurações** > **Extensões**
2. Encontre o repositório "BRCloudStream Repo"
3. Toque no **X** para remover
4. Toque em **Adicionar Repositório**
5. Cole a nova URL: `https://raw.githubusercontent.com/franciscoalro/CloudstreamRepo/main/builds/repo.json`

### 3. Verificar Permissões
1. Vá em **Configurações do Android** > **Apps** > **Cloudstream**
2. Toque em **Permissões**
3. Certifique-se que **Armazenamento** está permitido

### 4. Verificar Conexão
1. Teste se consegue acessar outros repositórios
2. Verifique se está conectado à internet
3. Tente usar dados móveis em vez de WiFi (ou vice-versa)

## 🔍 Diagnóstico Adicional

### Se ainda não funcionar, verifique:

#### A. Versão do Cloudstream
- Use a versão mais recente (3.5.0+)
- Versões antigas podem ter bugs de download

#### B. Logs do Android
Se você tem acesso ao ADB:
```bash
adb logcat | grep -i cloudstream
```

#### C. Teste Manual dos URLs
Teste se consegue baixar diretamente:
- https://raw.githubusercontent.com/franciscoalro/CloudstreamRepo/main/builds/MaxSeries.cs3

## 🚨 Problemas Conhecidos

### 1. Checksum Mismatch
- **Sintoma**: Plugin aparece mas não instala
- **Causa**: Tamanho incorreto no plugins.json
- **Status**: ✅ CORRIGIDO

### 2. URLs Inacessíveis
- **Sintoma**: "Failed to download" ou timeout
- **Causa**: URLs com refs/heads/ podem causar problemas
- **Status**: ✅ CORRIGIDO

### 3. Codificação de Caracteres
- **Sintoma**: Nomes com caracteres estranhos
- **Causa**: UTF-8 com BOM ou caracteres especiais
- **Status**: ✅ CORRIGIDO

## 📱 Teste no Cloudstream

### Resultado Esperado:
1. Repositório aparece como "BRCloudStream Repo"
2. Lista mostra 11 plugins disponíveis
3. Cada plugin pode ser baixado e instalado
4. Não há erros de checksum ou download

### Se funcionar:
- ✅ MaxSeries (638 KB)
- ✅ AnimesOnlineCC (27 KB)  
- ✅ Doramas (27 KB)
- ✅ E todos os outros...

## 🔄 Próximos Passos

Se o problema persistir:
1. Capture logs do Android (ADB)
2. Teste com outro dispositivo
3. Verifique se não há bloqueio de rede/firewall
4. Considere usar um repositório espelho

## 📞 Suporte

Se nada funcionar, forneça:
- Versão do Cloudstream
- Versão do Android
- Logs de erro (se disponível)
- Screenshots do problema