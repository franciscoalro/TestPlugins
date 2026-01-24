# 🚀 MaxSeries v160 - Regex Universal

## 📅 Data: 22/01/2026 22:45

---

## 🔧 CORREÇÃO DEFINITIVA (Broad Regex)

### 🕵️‍♂️ O Problema
Observamos nos logs que URLs legítimas de vídeo (ex: `https://stzm.marvellaholdings.sbs/v4/.../seg.woff2`) estavam passando despercebidas por causa de pequenas variações no regex anterior (validação estrita de host ou ID).

### ✅ A Solução (v160)
Simplificação radical do Regex de captura.
**Regra única:** Se a URL contém `/v4/`, ELA É CAPTURADA.

- **Antes:** `https?://[^/]+/v4/[a-z0-9]{3}/...` (Complexo)
- **Agora:** `.*/v4/.*` (Infalível)

Isso garante que QUALQUER link de vídeo (woff2, m3u8, txt) gerado pelo MegaEmbed seja interceptado imediatamente.

---

## 🏎️ Performance
- Script JS simplificado para menor overhead.
- Interceptação instantânea no momento do fetch.

---

## 🧪 ATUALIZAÇÃO RECOMENDADA
Versão obrigatória para correta reprodução de lançamentos recentes (MegaEmbed V8 com novos domínios dinâmicos).
