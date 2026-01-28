# 🔍 Verificar Conexão ADB WiFi

## ❌ Problema Atual

```
cannot connect to 100.124.161.4:42685: Uma tentativa de conexão falhou
```

## 🔧 Soluções

### 1. Verificar IP e Porta no Dispositivo

No Android:
1. Abrir app de depuração WiFi (ex: Wireless ADB)
2. Verificar IP e porta mostrados
3. Confirmar que está no formato: `XXX.XXX.XXX.XXX:XXXXX`

### 2. Verificar Mesma Rede

- PC e Android devem estar na **mesma rede WiFi**
- Verificar se não está em rede de convidados
- Desativar VPN se estiver usando

### 3. Testar Ping

```powershell
ping 100.124.161.4
```

Se não responder:
- Dispositivos não estão na mesma rede
- Firewall bloqueando
- IP mudou

### 4. Verificar Firewall

Windows pode estar bloqueando ADB:

1. Painel de Controle → Firewall
2. Configurações Avançadas
3. Regras de Entrada
4. Procurar "adb"
5. Habilitar se estiver desabilitado

### 5. Reiniciar ADB Server

```powershell
C:\Users\KYTHOURS\Desktop\platform-tools\adb.exe kill-server
C:\Users\KYTHOURS\Desktop\platform-tools\adb.exe start-server
C:\Users\KYTHOURS\Desktop\platform-tools\adb.exe connect 100.124.161.4:42685
```

### 6. Usar USB Temporariamente

Se WiFi não funcionar:

1. Conectar cabo USB
2. Habilitar depuração USB no Android
3. Executar:
   ```powershell
   C:\Users\KYTHOURS\Desktop\platform-tools\adb.exe devices
   ```

## 🎯 Teste Rápido

```powershell
# 1. Verificar se ADB funciona
C:\Users\KYTHOURS\Desktop\platform-tools\adb.exe version

# 2. Listar dispositivos conectados
C:\Users\KYTHOURS\Desktop\platform-tools\adb.exe devices

# 3. Tentar conectar
C:\Users\KYTHOURS\Desktop\platform-tools\adb.exe connect 100.124.161.4:42685
```

## 📱 No Android

### Habilitar Depuração WiFi

1. Configurações → Sobre o telefone
2. Tocar 7x em "Número da versão"
3. Voltar → Opções do desenvolvedor
4. Habilitar "Depuração USB"
5. Habilitar "Depuração sem fio" (se disponível)

### Apps Recomendados

- **Wireless ADB**: Mostra IP e porta
- **ADB WiFi**: Ativa depuração WiFi
- **Developer Options**: Acesso rápido

## 🔄 Alternativa: Executar Script Manualmente

Se ADB WiFi não funcionar, você pode:

1. Conectar via USB
2. Executar script normalmente
3. Ou capturar logs manualmente:

```powershell
# Limpar logs
C:\Users\KYTHOURS\Desktop\platform-tools\adb.exe logcat -c

# Clicar em PlayerEmbedAPI no app

# Capturar logs
C:\Users\KYTHOURS\Desktop\platform-tools\adb.exe logcat -d > playerembedapi_error.txt
```

## 💡 Dica

Se IP mudou, verifique no app de depuração WiFi qual é o novo IP e tente novamente.

---

**Próxima ação**: Verificar IP no dispositivo e tentar conectar novamente
