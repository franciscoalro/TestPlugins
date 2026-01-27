# ✅ Como Verificar se MaxSeries v217 Atualizou Corretamente

## 🔍 Passo 1: Verificar Versão no App

1. Abra o **Cloudstream**
2. Vá em **Configurações** (⚙️)
3. Clique em **Extensões** ou **Extensions**
4. Procure **MaxSeries** na lista
5. Clique em **MaxSeries**
6. **Verifique a versão:**
   - ✅ Deve mostrar: **v217** ou **217**
   - ❌ Se mostrar v216 ou menos: precisa atualizar

---

## 🧪 Passo 2: Testar Cache (Prova que Funcionou)

### Teste Simples:
1. Abra uma **série qualquer** no MaxSeries
2. Selecione um **episódio**
3. Aguarde carregar (primeira vez = pode demorar)
4. **Volte** para a lista de episódios
5. Abra o **MESMO episódio** novamente
6. **Resultado esperado:**
   - ✅ Carrega **INSTANTANEAMENTE** (< 1 segundo)
   - ✅ Não mostra "Carregando..." novamente
   - ✅ Fontes aparecem imediatamente

### Se Não Funcionar:
- ❌ Ainda demora para carregar = cache não está funcionando
- ❌ Mostra "Carregando..." novamente = versão antiga
- **Solução:** Reinstale o MaxSeries (veja abaixo)

---

## 🎯 Passo 3: Testar MegaEmbed

1. Abra um episódio que tenha **MegaEmbed** como fonte
2. Clique na fonte **MegaEmbed**
3. **Resultado esperado:**
   - ✅ Abre o player
   - ✅ Mostra overlays/ads (normal)
   - ✅ Após 3 cliques, vídeo reproduz
   - ❌ Se não aparecer nada = MegaEmbed não funcionou

---

## ⚡ Passo 4: Testar Velocidade

1. Navegue entre **vários episódios** diferentes
2. Observe a velocidade de carregamento
3. **Resultado esperado:**
   - ✅ Muito mais rápido que antes
   - ✅ Fontes aparecem em < 2 segundos
   - ✅ Navegação fluida

---

## 🔧 Se Não Atualizou: Reinstalar

### Método 1: Forçar Atualização
1. Configurações → Extensões
2. Puxe a tela para baixo (refresh)
3. Clique em "Atualizar" no MaxSeries
4. Aguarde download
5. Reinicie o app

### Método 2: Reinstalação Completa
1. **Remover MaxSeries:**
   - Configurações → Extensões
   - Clique em MaxSeries
   - Clique em "Desinstalar"

2. **Limpar cache do Cloudstream:**
   - Configurações do Android
   - Apps → Cloudstream
   - Armazenamento → Limpar cache

3. **Adicionar repositório:**
   - Abra Cloudstream
   - Configurações → Extensões
   - Clique no "+" (adicionar)
   - Cole:
     ```
     https://raw.githubusercontent.com/franciscoalro/TestPlugins/builds/plugins.json
     ```
   - Clique em "Adicionar"

4. **Instalar MaxSeries:**
   - Procure "MaxSeries"
   - Clique em "Instalar"
   - Aguarde download

5. **Reiniciar:**
   - Feche completamente o Cloudstream
   - Abra novamente

---

## 📊 Checklist de Verificação

Use este checklist para confirmar que tudo está funcionando:

- [ ] Versão mostra **v217** nas extensões
- [ ] Cache funciona (episódio carrega instantaneamente na 2ª vez)
- [ ] MegaEmbed aparece como fonte
- [ ] Navegação está mais rápida
- [ ] Fontes carregam em < 2 segundos
- [ ] Não há erros de "Serialization"

**Se todos os itens estão ✅ = Atualização bem-sucedida!**

---

## 🐛 Problemas Comuns

### Problema 1: Versão não muda
**Sintoma:** Ainda mostra v216 ou menos

**Solução:**
1. Remova MaxSeries
2. Limpe cache do Cloudstream
3. Reinstale do zero

### Problema 2: Cache não funciona
**Sintoma:** Episódio demora para carregar toda vez

**Solução:**
1. Verifique se é realmente v217
2. Reinicie o Cloudstream
3. Teste novamente

### Problema 3: MegaEmbed não aparece
**Sintoma:** Não vê MegaEmbed nas fontes

**Solução:**
1. Teste com outro episódio
2. Alguns episódios podem não ter MegaEmbed
3. Verifique se PlayerEmbedAPI ou MyVidPlay aparecem

### Problema 4: Erro ao instalar
**Sintoma:** "Falha ao instalar extensão"

**Solução:**
1. Verifique conexão com internet
2. Tente novamente em alguns minutos
3. Limpe cache do Cloudstream
4. Reinstale

---

## 📱 Logs ADB (Avançado)

Se você tem ADB instalado, pode verificar os logs:

```bash
C:\adb\platform-tools\adb.exe logcat | Select-String -Pattern "MaxSeries|Cache|MegaEmbed"
```

**Logs esperados (v217 funcionando):**
```
D/PersistentVideoCache: ✅ Cache HIT (5ms) - hit rate: 100%
D/MaxSeries-Cache: 🎯 Cache HIT
D/MegaEmbedV9: 🎯 [SPY] ALVO DETECTADO
D/WebViewPool: ⚡ Reusando WebView do pool
```

**Logs de erro (v217 NÃO funcionando):**
```
E/MaxSeriesProvider: kotlinx.serialization.SerializationException
```

---

## ✅ Confirmação Final

**Se você consegue:**
1. ✅ Ver v217 nas extensões
2. ✅ Episódio carrega instantaneamente na 2ª vez
3. ✅ MegaEmbed aparece como fonte
4. ✅ Navegação está mais rápida

**= MaxSeries v217 está funcionando perfeitamente! 🎉**

---

## 📞 Suporte

Se nada funcionar:
1. Capture logs ADB
2. Tire screenshot da versão nas extensões
3. Descreva o problema detalhadamente
4. Reporte no GitHub

---

**Data:** 26/01/2026 23:55  
**Versão:** v217  
**Status:** ✅ DISPONÍVEL PARA DOWNLOAD
