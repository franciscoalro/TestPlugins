# 🚀 QUICK START - MaxSeries Pre-Release (v80)

## ⚠️ Atenção: Requer Internet
O build depende do **Android SDK 36** ou do **GitHub Actions**. Como sua SDK local está desatualizada (sem API 36) e estamos sem internet, o build falha.

**ASSIM QUE A INTERNET VOLTAR:**

## ⚡ 1. Build via GitHub (Recomendado)

```powershell
# 1. Ir para o diretório
cd C:\Users\KYTHOURS\Desktop\cloudstream-pre-release

# 2. Executar script de setup
.\setup-github.ps1
```

Isso fará o push do código e o GitHub Actions vai compilar tudo (ele já tem o SDK 36).

## 📥 2. Baixar o Plugin Compilado

1. Vá para: **https://github.com/SEU_USUARIO/SEU_REPO/actions**
2. Baixe o artifact: **maxseries-v80-aar**
3. Instale no Cloudstream Pre-Release

---

## 🛠️ Alternativa: Build Local (Dá trabalho)
Se quiser compilar localmente, você precisará baixar o **Android SDK Platform 36**:
1. Abra o Android Studio
2. SDK Manager > Android SDK > SDK Tools
3. Marque "Show Package Details"
4. Instale **Android 36 (VanillaIceCream)**
5. Tente rodar o build novamente: `.\gradlew.bat :MaxSeries:assembleRelease`

## 📚 Documentação
- Detalhes Completos: `README-MAXSERIES-BUILD.md`
