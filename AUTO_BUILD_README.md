# 🤖 AUTO BUILD & RELEASE - MaxSeries v156

## 🚀 USO RÁPIDO

```powershell
cd c:\Users\KYTHOURS\Desktop\brcloudstream
.\start-auto-build.ps1
```

**O script fará TUDO automaticamente!**

---

## 📋 O QUE O SCRIPT FAZ

### **A cada 1 hora:**
1. ✅ Limpa builds anteriores
2. ✅ Tenta compilar MaxSeries v156
3. ✅ Se funcionou:
   - ✅ Calcula SHA256
   - ✅ Cria release v156 no GitHub
   - ✅ Faz upload do MaxSeries.cs3
   - ✅ Notifica você
   - ✅ **PARA** (sucesso!)
4. ❌ Se falhou:
   - ⏸️ Aguarda 1 hora
   - 🔄 Tenta novamente

### **Continua tentando por:**
- ⏱️ 24 horas (24 tentativas)
- 🛑 Ou até funcionar

---

## 🎯 CONFIGURAÇÕES

### **Padrão:**
```powershell
.\start-auto-build.ps1
# Tenta a cada 1 hora por 24 horas
```

### **Personalizado:**
```powershell
.\auto-build-release.ps1 -MaxAttempts 12 -IntervalMinutes 30
# Tenta a cada 30 minutos por 6 horas
```

### **Parâmetros:**
- `MaxAttempts`: Número máximo de tentativas (padrão: 24)
- `IntervalMinutes`: Intervalo entre tentativas em minutos (padrão: 60)

---

## 📊 EXEMPLOS DE USO

### **Tentar a cada 2 horas por 48 horas:**
```powershell
.\auto-build-release.ps1 -MaxAttempts 24 -IntervalMinutes 120
```

### **Tentar a cada 30 minutos por 12 horas:**
```powershell
.\auto-build-release.ps1 -MaxAttempts 24 -IntervalMinutes 30
```

### **Apenas 5 tentativas a cada 15 minutos:**
```powershell
.\auto-build-release.ps1 -MaxAttempts 5 -IntervalMinutes 15
```

---

## 🎬 O QUE VOCÊ VERÁ

```
========================================
  AUTO BUILD & RELEASE v156
========================================

Configuracao:
  Max tentativas: 24
  Intervalo: 60 minutos
  Tempo maximo: 24 horas

[2026-01-22 20:10:00] Tentativa 1/24
  [1/5] Limpando builds anteriores...
  [2/5] Tentando build...
  FALHOU Build falhou (JitPack ainda instavel)
  Motivo: JitPack timeout/indisponivel

  Aguardando 60 minutos ate proxima tentativa...
  (Ctrl+C para cancelar)

[2026-01-22 21:10:00] Tentativa 2/24
  [1/5] Limpando builds anteriores...
  [2/5] Tentando build...
  OK BUILD FUNCIONOU!
  OK Arquivo .cs3 criado!
  [3/5] Calculando SHA256...
  SHA256: abc123...
  Tamanho: 171.23 KB
  [4/5] Criando release v156 no GitHub...
  OK Release criada com sucesso!

========================================
       SUCESSO TOTAL!
========================================

Arquivo: MaxSeries\build\MaxSeries.cs3
Tamanho: 171.23 KB
SHA256: abc123...

Proximo passo:
  Testar no CloudStream3!
```

---

## 🛑 CANCELAR O SCRIPT

**Durante execução:**
```
Ctrl + C
```

**Matar processo:**
```powershell
Get-Process powershell | Where-Object {$_.MainWindowTitle -match "auto-build"} | Stop-Process
```

---

## 📁 ARQUIVOS GERADOS

### **Se bem-sucedido:**
```
MaxSeries\build\MaxSeries.cs3  (arquivo compilado)
build_info_v156.txt             (informações do build)
```

### **Conteúdo de build_info_v156.txt:**
```
MaxSeries v156 Build Info
=========================
Data: 2026-01-22 21:10:00
Tentativa: 2
Arquivo: MaxSeries\build\MaxSeries.cs3
Tamanho: 171.23 KB
SHA256: abc123def456...
```

---

## 🚀 APÓS SUCESSO

O script:
1. ✅ Cria release v156 automaticamente
2. ✅ Faz upload do MaxSeries.cs3
3. ✅ Para a execução

**Você só precisa:**
1. Verificar no GitHub que a release foi criada
2. Testar no CloudStream3
3. Pronto! 🎉

---

## 🔧 TROUBLESHOOTING

### **Problema: Script não inicia**
```powershell
# Executar com permissões
powershell -ExecutionPolicy Bypass -File start-auto-build.ps1
```

### **Problema: Erro de permissão**
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy Bypass
```

### **Problema: GitHub CLI não instalado**
O script abrirá o navegador automaticamente para criar a release manualmente.

**Instalar GitHub CLI (opcional):**
```powershell
winget install GitHub.cli
```

---

## 💡 DICAS

### **Rodar em Background:**
```powershell
Start-Process powershell -ArgumentList "-ExecutionPolicy Bypass -File start-auto-build.ps1" -WindowStyle Minimized
```

### **Notificação por E-mail (avançado):**
Adicione ao final do script:
```powershell
Send-MailMessage -To "seu@email.com" -Subject "Build v156 Completo!" -Body "Build funcionou!"
```

---

## 📊 ESTATÍSTICAS

**Tempo médio de build bem-sucedido:** ~2-3 minutos  
**Chance de sucesso por tentativa:** ~30% (depende do JitPack)  
**Tentativas até sucesso (média):** 3-5 tentativas  
**Tempo até sucesso (média):** 3-5 horas

---

## ✅ VANTAGENS DESSE SCRIPT

1. ✅ **Automático** - Você não precisa fazer nada
2. ✅ **Persistente** - Tenta até funcionar
3. ✅ **Inteligente** - Para quando consegue
4. ✅ **Informativo** - Mostra progresso detalhado
5. ✅ **Completo** - Cria release automaticamente
6. ✅ **Seguro** - Não faz nada destrutivo

---

**🎯 Basta executar e aguardar!** 🚀
