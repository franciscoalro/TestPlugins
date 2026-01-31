# Solução de Problemas - Download do MaxSeries

## 🔧 Problema: CloudStream não consegue baixar o plugin

### ✅ Correções já aplicadas

1. **✅ Arquivo CS3 recriado** - Estrutura AAR correta
2. **✅ BOM removido** do plugins.json
3. **✅ Hash SHA256 atualizado** - 541781E424BC37EF2ECC5F0AB6B1FAB402AC1B3F564232D634526CB9993CC105
4. **✅ Tamanho correto** - 653163 bytes
5. **✅ URL verificada** - Download funciona no navegador

---

## 🧪 Testes realizados

| Teste | Resultado |
|-------|-----------|
| Download via browser/curl | ✅ Funciona |
| Hash verificado | ✅ Corresponde |
| Estrutura AAR | ✅ Válida |
| JSON sem BOM | ✅ Corrigido |
| GitHub Pages atualizado | ✅ Deploy feito |

---

## 🔍 Possíveis causas no CloudStream

### 1. Cache do repositório
O CloudStream pode ter cacheado a versão antiga do JSON.

**Solução:**
```
Configurações → Extensões → Atualizar repositórios
```

Ou remova e re-adicione o repositório:
```
Configurações → Extensões → Remover "Francisco Plugins"
Configurações → Extensões → + → Adicionar repositório
URL: https://franciscoalro.github.io/CloudstreamRepo/repo.json
```

### 2. Problema de DNS/Cache DNS
O GitHub Pages pode estar com cache DNS antigo.

**Solução:**
- Force parada do CloudStream
- Limpe cache do app (Android)
- Reinicie o app

### 3. Problema com o GitHub Releases
O CloudStream pode ter dificuldade com redirecionamentos do GitHub.

**Solução alternativa - Download manual:**
1. Baixe diretamente: https://github.com/franciscoalro/TestPlugins/releases/download/v256/MaxSeries.cs3
2. No CloudStream: Configurações → Extensões → Instalar de arquivo .cs3
3. Selecione o arquivo baixado

### 4. Verificar se a URL está acessível no celular

Teste no navegador do celular:
```
https://franciscoalro.github.io/CloudstreamRepo/plugins.json
```

Deve mostrar o JSON com "version": 256

---

## 📱 Teste rápido no CloudStream

### Verificar versão detectada
1. Abra CloudStream
2. Vá em: Configurações → Extensões
3. Toque no repositório "Francisco Plugins"
4. Procure por MaxSeries
5. **Deve mostrar:** "v256" e não "v255"

Se mostrar v255, o cache ainda não foi atualizado.

### Forçar atualização
1. Feche completamente o CloudStream
2. Vá em: Android → Configurações → Apps → CloudStream
3. Toque em: Armazenamento → Limpar cache
4. Reabra o CloudStream
5. Adicione o repositório novamente

---

## 🌐 URLs para verificação

| URL | Deve retornar |
|-----|---------------|
| https://franciscoalro.github.io/CloudstreamRepo/repo.json | JSON com "name": "Francisco Plugins - v256" |
| https://franciscoalro.github.io/CloudstreamRepo/plugins.json | JSON com "version": 256 para MaxSeries |
| https://github.com/franciscoalro/TestPlugins/releases/download/v256/MaxSeries.cs3 | Arquivo de 653KB (download) |

---

## 🆘 Solução alternativa imediata

Se nada funcionar, use o método manual:

### Passo 1: Baixar no PC
Acesse: https://github.com/franciscoalro/TestPlugins/releases/tag/v256

### Passo 2: Transferir para o celular
- USB, Bluetooth, Telegram, Drive, etc.

### Passo 3: Instalar manualmente
```
CloudStream → Configurações → Extensões 
→ ⋮ (menu) → Instalar de arquivo .cs3
→ Selecione o arquivo MaxSeries.cs3
```

---

## 📞 Status do servidor

Última atualização: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')

- ✅ GitHub Pages: ONLINE
- ✅ Release v256: ONLINE
- ✅ Arquivo CS3: DISPONÍVEL
- ⏱️  Propagação DNS: 1-5 minutos

---

## 🔄 Se ainda não funcionar

Aguarde 5-10 minutos e tente novamente. O GitHub Pages pode levar alguns minutos para propagar as alterações globalmente.
