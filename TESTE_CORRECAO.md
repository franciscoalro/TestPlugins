# ✅ CORREÇÃO APLICADA: Download de Plugins

**Status:** CORREÇÃO ENVIADA PARA GITHUB 🚀

As correções foram aplicadas com sucesso nos arquivos de configuração do repositório `TestPlugins`. 

## 🛠️ O QUE FOI CORRIGIDO

1.  **URLs do Repositório:** Todas as referências a `CloudstreamRepo` foram alteradas para `TestPlugins` no `plugins.json` e `repo.json`.
2.  **Tamanho de Arquivo Inválido:** O `fileSize` do MaxSeries foi corrigido de `0` para `653406` bytes no `providers.json`.
3.  **Versão Sincronizada:** A versão do MaxSeries foi alinhada para `256` em ambos os arquivos JSON.
4.  **URLs de Download:** Agora apontam corretamente para `raw.githubusercontent.com/.../TestPlugins/...`

---

## 📲 COMO TESTAR NO CLOUDSTREAM

1.  Abra o **Cloudstream**.
2.  Vá em **Settings (Configurações)** > **Extensions (Extensões)**.
3.  Clique em **+ Add Repository (+ Adicionar Repositório)**.
4.  Insira o nome (ex: `BRCloudStream`) e a URL do repositório:
    ```
    https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/repo.json
    ```
5.  Clique em **Add (Adicionar)**.
6.  Vá para a lista de plugins e procure por **MaxSeries**, **AnimesOnlineCC**, etc.
7.  Clique em **Install (Instalar)**.

> **Nota:** Se você já tinha o repositório adicionado, pode ser necessário remover e adicionar novamente, ou limpar o cache do aplicativo para que ele puxe o JSON atualizado.

---

**Se o download iniciar e concluir com sucesso, o problema está resolvido!** 🎉
