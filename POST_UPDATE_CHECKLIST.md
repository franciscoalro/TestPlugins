# ✅ Checklist Pós-Atualização

## 🔍 Verificações Técnicas

### 1. Build Status
- [ ] ✅ GitHub Actions passou sem erros
- [ ] ✅ Artifacts (.cs3) foram gerados
- [ ] ✅ Sem warnings de compilação

### 2. Arquivos Atualizados
- [ ] ✅ `MaxSeries/src/main/kotlin/.../MaxSeriesProvider.kt` - Sintaxe newExtractorLink corrigida
- [ ] ✅ `MaxSeries/build.gradle.kts` - Versão 7 → 8
- [ ] ✅ `plugins.json` - Descrição e versão atualizadas

### 3. CloudstreamRepo
- [ ] 🔄 Arquivos .cs3 copiados para CloudstreamRepo
- [ ] 🔄 plugins.json atualizado no CloudstreamRepo
- [ ] 🔄 Commit e push realizados

## 🧪 Testes de Funcionalidade

### MaxSeries v8
- [ ] 🔄 Plugin carrega no CloudStream v9.0
- [ ] 🔄 Busca de séries funciona
- [ ] 🔄 Listagem de episódios funciona
- [ ] 🔄 Links de vídeo são extraídos
- [ ] 🔄 Reprodução funciona sem erros

### AnimesOnlineCC v6
- [ ] 🔄 Plugin continua funcionando
- [ ] 🔄 Busca de animes funciona
- [ ] 🔄 Links de vídeo funcionam

## 🌐 Verificações de Distribuição

### URLs de Acesso
- [ ] 🔄 https://raw.githubusercontent.com/franciscoalro/CloudstreamRepo/main/plugins.json
- [ ] 🔄 https://github.com/franciscoalro/CloudstreamRepo/releases (se usar releases)
- [ ] 🔄 Links diretos dos .cs3 funcionam

### CloudStream App
- [ ] 🔄 Repositório aparece na lista
- [ ] 🔄 Plugins aparecem para instalação
- [ ] 🔄 Versões corretas são mostradas
- [ ] 🔄 Instalação funciona sem erros

## 🐛 Problemas Conhecidos Resolvidos

### ✅ Corrigidos na v8
- [x] ❌ `No parameter with name 'referer' found`
- [x] ❌ `No parameter with name 'quality' found`
- [x] ❌ Incompatibilidade com CloudStream v9.0

### 🔍 Monitorar
- [ ] Performance de extração de links
- [ ] Compatibilidade com diferentes hosts
- [ ] Estabilidade geral do plugin

## 📊 Métricas de Sucesso

### Antes (v7)
- ❌ Build falhando
- ❌ Incompatível com CloudStream v9.0
- ❌ Erros de compilação

### Depois (v8)
- ✅ Build passando
- ✅ Compatível com CloudStream v9.0
- ✅ Sem erros de compilação
- ✅ Funcionalidade mantida

## 🚀 Comandos Úteis

### Verificar Build
```bash
# Ver último build
https://github.com/franciscoalro/TestPlugins/actions

# Baixar artifacts
gh run download --repo franciscoalro/TestPlugins -n "Built plugins"
```

### Atualizar CloudstreamRepo
```powershell
# Usar script automatizado
.\auto-update-repo.ps1

# Ou manualmente
cp *.cs3 ../CloudstreamRepo/
cp plugins.json ../CloudstreamRepo/
cd ../CloudstreamRepo
git add .
git commit -m "Update plugins - MaxSeries v8"
git push
```

### Testar Localmente
```bash
# Instalar no CloudStream
# 1. Adicionar repositório: https://raw.githubusercontent.com/franciscoalro/CloudstreamRepo/main/plugins.json
# 2. Instalar MaxSeries v8
# 3. Testar funcionalidades
```

---

**Status Atual**: 🔄 Em andamento
**Última Atualização**: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
**Responsável**: franciscoalro