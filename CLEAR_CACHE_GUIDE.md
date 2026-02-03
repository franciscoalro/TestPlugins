# Guia: Limpar Cache no CloudStream

## ✅ Cache limpo no servidor!

Os URLs agora incluem `?v=202602011312` para forçar o download fresco.

---

## 📱 Como Limpar Cache no CloudStream App

### Método 1: Atualizar Repositório (Recomendado)
1. Abra o CloudStream
2. Vá em **Configurações** → **Extensões** → **Repositórios**
3. Segure no repositório `BRCloudStream Repo`
4. Toque em **Atualizar** ou **Remover** e adicione novamente
5. URL atualizada:
   ```
   https://raw.githubusercontent.com/franciscoalro/CloudstreamRepo/main/repo.json?v=202602011312
   ```

### Método 2: Limpar Cache do App
1. Abra **Configurações** do Android
2. Vá em **Aplicativos** → **CloudStream**
3. Toque em **Armazenamento**
4. Toque em **Limpar Cache** (não limpa dados!)

### Método 3: Forçar Parada e Reiniciar
1. Nas configurações do Android, force a parada do CloudStream
2. Abra novamente
3. O app buscará dados frescos

### Método 4: URL Alternativa (GitHub Pages)
Se o raw.githubusercontent continuar em cache, use GitHub Pages:
```
https://franciscoalro.github.io/TestPlugins/repo.json
```

---

## 🔧 Verificar se o Cache foi Limpo

Teste estes URLs no navegador:

1. **Repo**: https://raw.githubusercontent.com/franciscoalro/CloudstreamRepo/main/repo.json?v=202602011312
2. **Plugins**: https://raw.githubusercontent.com/franciscoalro/CloudstreamRepo/main/builds/plugins.json?v=202602011312
3. **MaxSeries JAR**: https://raw.githubusercontent.com/franciscoalro/CloudstreamRepo/main/builds/MaxSeries.jar?v=202602011312

Se abrir sem erro 404, está funcionando!

---

## 🔄 Forçar Nova Limpeza

Se precisar limpar novamente:
```powershell
.\clear-cache-and-redeploy.ps1 -CacheBustReason "Nova tentativa"
```
