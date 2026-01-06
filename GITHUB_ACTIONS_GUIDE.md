# 🚀 Guia Rápido - GitHub Actions Build

## ✅ Workflow Configurado!

O GitHub Actions está pronto para compilar seu plugin automaticamente.

---

## 📋 Checklist de Verificação

### 1. **Confirmar que o código foi enviado:**
```bash
git status
git log --oneline -1
```

### 2. **Acessar GitHub Actions:**
- Vá para: `https://github.com/SEU_USUARIO/SEU_REPO/actions`
- Você verá o workflow "Build Plugin" rodando

### 3. **Monitorar o Build:**
- Clique no workflow em execução
- Acompanhe cada etapa:
  - ✅ Checkout
  - ✅ Setup JDK 17
  - ✅ Grant execute permission
  - ✅ Build with Gradle ← **Etapa crítica**
  - ✅ Upload Plugin

### 4. **Baixar o Plugin (.cs3):**

**Se o build for bem-sucedido:**
1. Na página do workflow, role até o final
2. Procure a seção **"Artifacts"**
3. Clique em **"AnimesOnlineCC-Plugin"**
4. Baixe o arquivo ZIP
5. Extraia o arquivo `.cs3`

**Se o build falhar:**
- Clique em "Build with Gradle" para ver o erro
- Copie o log e me envie para análise

---

## 🎯 Próximos Passos Após Download

### 1. **Transferir para Android:**
- Conecte seu celular ao PC via USB
- Copie o arquivo `.cs3` para a pasta Downloads do celular

### 2. **Instalar no Cloudstream:**
1. Abra o Cloudstream
2. Vá em **Configurações → Extensões**
3. Clique em **"+"** ou **"Instalar extensão local"**
4. Navegue até o arquivo `.cs3`
5. Confirme a instalação

### 3. **Testar o Plugin:**
1. Volte para a tela inicial
2. Procure por "Animes Online CC" nas fontes
3. Teste a busca: digite "Naruto"
4. Clique em um anime e veja os episódios
5. Tente reproduzir um episódio

---

## 🐛 Troubleshooting

### **Build falha com erro do JitPack:**
- O GitHub Actions também depende do JitPack
- Se falhar, aguarde algumas horas e tente novamente
- Use o botão "Re-run all jobs" para tentar de novo

### **Arquivo .cs3 não aparece nos Artifacts:**
- Verifique se o build completou com sucesso (✅ verde)
- O arquivo só é gerado se o build for bem-sucedido

### **Plugin não instala no Cloudstream:**
- Verifique se concedeu permissão "Todos os arquivos" ao app
- Tente reiniciar o Cloudstream
- Verifique se o arquivo não está corrompido (tamanho > 0 KB)

---

## 📊 Status Esperado

### **Build Bem-Sucedido:**
```
✅ Checkout
✅ Setup JDK 17
✅ Grant execute permission
✅ Build with Gradle (2-5 minutos)
✅ Upload Plugin
```

### **Artifacts Disponíveis:**
```
📦 AnimesOnlineCC-Plugin.zip
  └── AnimesOnlineCC-v1.cs3 (≈50-200 KB)
```

---

## 🔄 Forçar Novo Build

Se precisar compilar novamente:

```bash
# Fazer uma mudança mínima
git commit --allow-empty -m "Trigger build"
git push
```

Ou use o botão **"Run workflow"** na aba Actions do GitHub.

---

## ✨ Dica Pro

Adicione um badge no README do seu repositório:

```markdown
![Build Status](https://github.com/SEU_USUARIO/SEU_REPO/workflows/Build%20Plugin/badge.svg)
```

---

**Boa sorte! 🎉**

Quando o build completar, você terá seu plugin pronto para usar!
