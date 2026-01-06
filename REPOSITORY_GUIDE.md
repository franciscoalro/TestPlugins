# 🌐 Repositório de Extensões - Guia Completo

## 🎯 O que é um Repositório de Extensões?

É uma forma **muito mais fácil** de instalar e atualizar plugins no Cloudstream! Ao invés de baixar arquivos `.cs3` manualmente, você adiciona uma URL no app e ele instala/atualiza automaticamente.

---

## 🚀 Como Usar (Método Simples)

### **Passo 1: Adicionar o Repositório no Cloudstream**

1. Abra o **Cloudstream**
2. Vá em **⚙️ Configurações → Extensões**
3. Toque nos **3 pontinhos** (⋮) no canto superior direito
4. Selecione **"Adicionar repositório"**
5. Cole esta URL:
   ```
   https://franciscoalro.github.io/TestPlugins/repo.json
   ```
6. Toque em **"Adicionar"**

### **Passo 2: Instalar a Extensão**

1. Ainda em **Extensões**, role até encontrar **"AnimesOnlineCC"**
2. Toque em **"Baixar"** ou **"Instalar"**
3. Aguarde o download
4. **Pronto!** ✅

---

## 🔄 Atualizações Automáticas

Quando você atualizar o código e fazer push:
1. GitHub Actions compila automaticamente
2. Cria uma nova release
3. Atualiza o `plugins.json`
4. O Cloudstream detecta e oferece atualização!

---

## ⚙️ Configuração Inicial (Você Precisa Fazer Uma Vez)

### **1. Ativar GitHub Pages**

1. Acesse: https://github.com/franciscoalro/TestPlugins/settings/pages
2. Em **"Source"**, selecione: **"Deploy from a branch"**
3. Em **"Branch"**, selecione: **"gh-pages"** e pasta **"/ (root)"**
4. Clique em **"Save"**

### **2. Criar a Primeira Release**

Depois que o GitHub Pages estiver ativo:

```bash
# No seu terminal local:
git tag v1.0
git push origin v1.0
```

Isso vai:
- Compilar o plugin
- Criar uma release no GitHub
- Disponibilizar o `.cs3` para download
- Publicar o `repo.json` e `plugins.json` no GitHub Pages

---

## 📋 Estrutura de Arquivos

```
TestPlugins/
├── repo.json              # Configuração do repositório
├── plugins.json           # Lista de plugins disponíveis
└── .github/workflows/
    └── build.yml          # Automação (build + release + deploy)
```

### **repo.json**
```json
{
    "name": "AnimesOnlineCC Repository",
    "description": "Repositório de extensões para animes",
    "manifestVersion": 1,
    "pluginLists": [
        "https://franciscoalro.github.io/TestPlugins/plugins.json"
    ]
}
```

### **plugins.json**
```json
[
    {
        "name": "AnimesOnlineCC",
        "description": "Assista animes online grátis em HD",
        "version": 1,
        "url": "https://github.com/franciscoalro/TestPlugins/releases/download/v1.0/AnimesOnlineCC-v1.cs3"
    }
]
```

---

## 🔄 Como Atualizar o Plugin

### **Método 1: Atualização de Versão (Recomendado)**

1. Edite `AnimesOnlineCC/build.gradle.kts`:
   ```kotlin
   version = 2  // Incremente o número
   ```

2. Commit e crie uma nova tag:
   ```bash
   git add .
   git commit -m "v2.0: Adicionado suporte a legendas"
   git tag v2.0
   git push origin main
   git push origin v2.0
   ```

3. GitHub Actions faz o resto automaticamente!

### **Método 2: Atualização Simples**

Apenas faça push para `main`:
```bash
git add .
git commit -m "Fix: Correção de bugs"
git push origin main
```

O plugin será recompilado, mas sem criar nova release.

---

## 🌐 URLs Importantes

### **URL do Repositório (para adicionar no Cloudstream):**
```
https://franciscoalro.github.io/TestPlugins/repo.json
```

### **URL da Lista de Plugins:**
```
https://franciscoalro.github.io/TestPlugins/plugins.json
```

### **URL do Plugin (download direto):**
```
https://github.com/franciscoalro/TestPlugins/releases/download/v1.0/AnimesOnlineCC-v1.cs3
```

---

## 🐛 Troubleshooting

### **"Repositório não encontrado" no Cloudstream**
- ✅ Verifique se o GitHub Pages está ativado
- ✅ Aguarde 5-10 minutos após ativar o GitHub Pages
- ✅ Teste a URL no navegador: https://franciscoalro.github.io/TestPlugins/repo.json

### **Plugin não aparece na lista**
- ✅ Verifique se o `plugins.json` está correto
- ✅ Certifique-se de que a release foi criada
- ✅ Atualize a lista de repositórios no Cloudstream

### **Erro ao baixar o plugin**
- ✅ Verifique se a tag foi criada corretamente
- ✅ Confirme que o arquivo `.cs3` existe na release
- ✅ Teste o link de download manualmente

---

## 📊 Comparação: Manual vs Repositório

| Método | Manual | Repositório |
|--------|--------|-------------|
| **Instalação** | Baixar .cs3 + Instalar manualmente | Adicionar URL uma vez |
| **Atualizações** | Baixar novamente + Reinstalar | Automático (notificação no app) |
| **Múltiplos Plugins** | Um por um | Todos de uma vez |
| **Facilidade** | ⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 🎊 Vantagens do Repositório

- ✅ **Instalação com 1 clique**
- ✅ **Atualizações automáticas**
- ✅ **Gerenciamento centralizado**
- ✅ **Compartilhamento fácil** (só passar a URL)
- ✅ **Múltiplos plugins** em um só lugar

---

## 📝 Próximos Passos

1. ✅ Ativar GitHub Pages (faça agora!)
2. ✅ Criar tag v1.0 e fazer push
3. ✅ Testar a URL do repositório no navegador
4. ✅ Adicionar no Cloudstream
5. ✅ Aproveitar! 🎉

---

**URL para adicionar no Cloudstream:**
```
https://franciscoalro.github.io/TestPlugins/repo.json
```

**Copie e cole no app!** 📋
