# 📱 Como Conectar ADB via WiFi

## Método 1: Depuração Sem Fio (Android 11+)

### No Celular:
1. Ir em **Configurações**
2. **Sistema** → **Opções do Desenvolvedor**
3. Ativar **Depuração sem fio**
4. Tocar em **Depuração sem fio**
5. Tocar em **Parear dispositivo com código de pareamento**
6. Anotar **IP e porta** (ex: `192.168.0.184:34307`)
7. Anotar **código de pareamento** (ex: `123456`)

### No PC:
```powershell
# Parear (primeira vez)
C:\Users\KYTHOURS\Desktop\platform-tools\adb.exe pair 192.168.0.184:34307
# Digite o código quando solicitado

# Conectar
C:\Users\KYTHOURS\Desktop\platform-tools\adb.exe connect 192.168.0.184:34307

# Verificar
C:\Users\KYTHOURS\Desktop\platform-tools\adb.exe devices
```

---

## Método 2: Via USB primeiro (Qualquer Android)

### Passo 1: Conectar USB
```powershell
# Conectar cabo USB
# Ativar "Depuração USB" no celular
# Aceitar permissão

# Verificar conexão
C:\Users\KYTHOURS\Desktop\platform-tools\adb.exe devices
```

### Passo 2: Ativar WiFi
```powershell
# Ativar ADB via WiFi na porta 5555
C:\Users\KYTHOURS\Desktop\platform-tools\adb.exe tcpip 5555

# Desconectar USB
```

### Passo 3: Conectar via WiFi
```powershell
# Descobrir IP do celular (Configurações → Sobre → Status → IP)
# Conectar
C:\Users\KYTHOURS\Desktop\platform-tools\adb.exe connect 192.168.0.XXX:5555

# Verificar
C:\Users\KYTHOURS\Desktop\platform-tools\adb.exe devices
```

---

## Verificar Conexão

```powershell
C:\Users\KYTHOURS\Desktop\platform-tools\adb.exe devices
```

**Saída esperada:**
```
List of devices attached
192.168.0.184:34307    device
```

---

## Testar MaxSeries v219

Depois de conectado, execute:
```powershell
.\test-v219-manual.ps1
```

---

## Problemas Comuns

### "cannot connect"
- Verificar se celular e PC estão na mesma rede WiFi
- Verificar se porta está correta
- Tentar desativar e ativar "Depuração sem fio"

### "unauthorized"
- Aceitar permissão no celular
- Revogar autorizações: Configurações → Opções do Desenvolvedor → Revogar autorizações de depuração USB

### "offline"
- Desconectar: `adb disconnect`
- Reconectar: `adb connect IP:PORTA`

---

## Comandos Úteis

```powershell
# Listar dispositivos
adb devices

# Conectar
adb connect IP:PORTA

# Desconectar
adb disconnect IP:PORTA

# Desconectar todos
adb disconnect

# Ver logs em tempo real
adb logcat | Select-String "MaxSeries"

# Limpar logs
adb logcat -c

# Salvar logs em arquivo
adb logcat -d > logs.txt
```
