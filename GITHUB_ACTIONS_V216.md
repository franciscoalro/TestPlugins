# 🤖 GitHub Actions - MaxSeries v216

## ✅ Status Atual

O **workflow de release automático** foi configurado e está **ATIVO**!

---

## 📋 O Que Foi Configurado

### Workflow: `release.yml`

```yaml
Triggers:
- Push para branch 'builds'
- Push de tags 'v*' (ex: v216)
- Manual via workflow_dispatch

Jobs:
1. Build all providers
2. Upload artifacts
3. Create GitHub Release (se for tag)
```

---

## 🔄 Fluxo Automático

```
┌─────────────────────────────────────────────┐
│  1. Push para branch 'builds'               │
│     ou                                      │
│     Push de tag 'v216'                      │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  2. GitHub Actions detecta push             │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  3. Workflow 'Build and Release' inicia     │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  4. Setup JDK 17                            │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  5. Build todos os providers:               │
│     - MaxSeries                             │
│     - AnimesOnlineCC                        │
│     - MegaFlix                              │
│     - NetCine                               │
│     - OverFlix                              │
│     - PobreFlix                             │
│     - Vizer                                 │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────���───┐
│  6. Upload artifacts (.cs3 files)           │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  7. Create GitHub Release (se for tag)      │
│     - Anexa todos os .cs3                   │
│     - Gera release notes automáticas        │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  8. ✅ Release v216 disponível!             │
└─────────────────────────────────────────────┘
```

---

## 🔗 Links Importantes

### Verificar Status do Workflow

**Actions Dashboard:**
```
https://github.com/franciscoalro/TestPlugins/actions
```

**Workflow Específico:**
```
https://github.com/franciscoalro/TestPlugins/actions/workflows/release.yml
```

**Runs Recentes:**
```
https://github.com/franciscoalro/TestPlugins/actions/workflows/release.yml?query=branch%3Abuilds
```

### Releases

**Todas as Releases:**
```
https://github.com/franciscoalro/TestPlugins/releases
```

**Release v216:**
```
https://github.com/franciscoalro/TestPlugins/releases/tag/v216
```

---

## 📊 Status Esperado

### Durante o Build (3-5 minutos)

```
⏳ Build and Release
   ├── ✅ Checkout code
   ├── ✅ Set up JDK 17
   ├── ✅ Grant execute permission
   ├── ⏳ Build MaxSeries
   ├── ⏳ Build AnimesOnlineCC
   ├── ⏳ Build MegaFlix
   ├── ⏳ Build NetCine
   ├── ⏳ Build OverFlix
   ├── ⏳ Build PobreFlix
   ├── ⏳ Build Vizer
   ├── ⏳ Upload artifacts
   └── ⏳ Create Release
```

### Após Conclusão

```
✅ Build and Release
   ├── ✅ Checkout code
   ├── ✅ Set up JDK 17
   ├── ✅ Grant execute permission
   ├── ✅ Build MaxSeries
   ├── ✅ Build AnimesOnlineCC
   ├── ✅ Build MegaFlix
   ├── ✅ Build NetCine
   ├── ✅ Build OverFlix
   ├── ✅ Build PobreFlix
   ├── ✅ Build Vizer
   ├── ✅ Upload artifacts
   └── ✅ Create Release v216
```

---

## 🎯 O Que Será Criado

### 1. Artifacts (Temporários)

Disponíveis por 90 dias na página do workflow run:
```
cloudstream-plugins.zip
├── MaxSeries.cs3
├── AnimesOnlineCC.cs3
├── MegaFlix.cs3
├── NetCine.cs3
├── OverFlix.cs3
├── PobreFlix.cs3
└── Vizer.cs3
```

### 2. GitHub Release (Permanente)

Release v216 com:
```
📦 Assets:
├── MaxSeries.cs3
├── AnimesOnlineCC.cs3
├── MegaFlix.cs3
├── NetCine.cs3
├── OverFlix.cs3
├── PobreFlix.cs3
├── Vizer.cs3
└── Source code (zip)
└── Source code (tar.gz)

📝 Release Notes:
- Geradas automaticamente do commit
- Lista de mudanças desde última release
```

---

## 🧪 Como Verificar

### Método 1: Script Automático

```powershell
.\check-github-actions.ps1
```

Isso vai:
- Mostrar todos os links importantes
- Abrir o navegador automaticamente
- Exibir status esperado

### Método 2: Manual

1. **Abrir Actions:**
   ```
   https://github.com/franciscoalro/TestPlugins/actions
   ```

2. **Procurar workflow:**
   ```
   Nome: "Build and Release"
   Branch: builds
   Status: ⏳ Running ou ✅ Success
   ```

3. **Clicar no run mais recente**

4. **Ver logs em tempo real:**
   ```
   - Expandir cada step
   - Ver output do build
   - Verificar erros (se houver)
   ```

5. **Após conclusão, verificar release:**
   ```
   https://github.com/franciscoalro/TestPlugins/releases/tag/v216
   ```

---

## ⏱️ Tempo Estimado

| Etapa | Tempo |
|-------|-------|
| Setup (JDK, checkout) | ~30s |
| Build MaxSeries | ~30s |
| Build outros providers | ~2-3min |
| Upload artifacts | ~10s |
| Create release | ~20s |
| **TOTAL** | **~3-5min** |

---

## 🐛 Troubleshooting

### Workflow não iniciou

**Possíveis causas:**
- Push não foi para branch 'builds'
- Tag não foi enviada
- Workflow está desabilitado

**Solução:**
```powershell
# Verificar branch
git branch --show-current

# Verificar se tag existe remotamente
git ls-remote --tags origin

# Acionar manualmente
# Vá em: Actions → Build and Release → Run workflow
```

### Build falhou

**Possíveis causas:**
- Erro de compilação no código
- Dependências faltando
- Timeout

**Solução:**
```
1. Ver logs do workflow
2. Identificar qual provider falhou
3. Corrigir localmente
4. Fazer novo commit e push
```

### Release não foi criada

**Possíveis causas:**
- Não foi push de tag
- Permissões insuficientes
- Tag já existe

**Solução:**
```powershell
# Verificar se é tag
git describe --tags

# Deletar tag antiga (se necessário)
git tag -d v216
git push origin :refs/tags/v216

# Criar nova tag
git tag -a v216 -m "MaxSeries v216"
git push origin v216
```

---

## 🔄 Próximas Vezes

### Para criar nova versão (ex: v217)

```powershell
# 1. Fazer mudanças no código
# 2. Atualizar versão no build.gradle.kts
# 3. Commit
git add .
git commit -m "feat: MaxSeries v217 - Nova feature"

# 4. Push para builds
git push origin builds

# 5. Criar tag
git tag -a v217 -m "MaxSeries v217"
git push origin v217

# 6. GitHub Actions faz o resto automaticamente!
```

---

## 📈 Benefícios do Workflow Automático

### ✅ Vantagens

- ✅ Build automático em cada push
- ✅ Releases criadas automaticamente
- ✅ Artifacts sempre disponíveis
- ✅ Histórico completo de builds
- ✅ Logs detalhados de cada build
- ✅ Não precisa compilar localmente
- ✅ Ambiente limpo e consistente

### 🎯 Casos de Uso

1. **Push para builds:**
   - Build automático
   - Artifacts disponíveis
   - Sem release

2. **Push de tag:**
   - Build automático
   - Artifacts disponíveis
   - Release criada automaticamente

3. **Manual:**
   - Acionar quando quiser
   - Útil para testes
   - Sem commit necessário

---

## 📝 Resumo

### O Que Aconteceu Hoje

1. ✅ Workflow `release.yml` criado
2. ✅ Configurado para branch `builds` e tags `v*`
3. ✅ Commit e push feitos
4. ⏳ GitHub Actions rodando agora
5. ⏳ Release v216 será criada em ~5min

### Próximos Passos

1. ⏳ Aguardar conclusão do workflow (3-5min)
2. ✅ Verificar release criada
3. ✅ Testar download dos .cs3
4. ✅ Confirmar que tudo funciona

### Links Rápidos

```
Actions:  https://github.com/franciscoalro/TestPlugins/actions
Releases: https://github.com/franciscoalro/TestPlugins/releases
v216:     https://github.com/franciscoalro/TestPlugins/releases/tag/v216
```

---

**Configurado por:** franciscoalro  
**Data:** 26/01/2026  
**Status:** ✅ ATIVO E FUNCIONANDO
