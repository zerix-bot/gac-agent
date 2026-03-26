# PIPELINE.md — Protocolo de Pipeline G.Ac.

## Comando de ativação

O pipeline é ativado quando o usuário enviar (em qualquer variação):
```
Executar pipeline análise sobre [Empresa]
```

---

## Fluxo Obrigatório

### Etapa 0 — Verificação do RAG (SEMPRE executar primeiro)

Antes de qualquer outra coisa, verificar se o documento já está indexado:

```bash
python3 /data/.openclaw/workspace-gac/skills/financial-rag/rag.py list
```

**Cenário A — documento já indexado:**
> Informar ao usuário: "Documento da [Empresa] encontrado no RAG (coleção: `doc_XXXX`). Posso iniciar a análise sem necessidade de novo upload."
> Anotar o nome da coleção e pular para a **Etapa 2**.

**Cenário B — documento não indexado:**
> Prosseguir para a **Etapa 1** (coleta de fontes).

---

### Etapa 1 — Coleta de Fontes (somente se doc não indexado)

Perguntar ao usuário:

> "Para iniciar a análise de **[Empresa]**, por favor informe as fontes:
> - URLs de acesso (portal de RI, CVM, link direto de PDF)
> - Arquivos PDF anexados
>
> Há mais de um documento ou fonte a ser considerada? (ex: DFP + Notas Explicativas separadas, múltiplos exercícios)"

Aguardar a resposta antes de continuar.

**Após receber o PDF/URL — indexar imediatamente:**

```bash
python3 /data/.openclaw/workspace-gac/skills/financial-rag/rag.py ingest <caminho_pdf>
```

Anotar o nome da coleção retornada. Usá-lo em todas as queries da Etapa 2.

---

### Etapa 2 — Análise via RAG

Executar o fluxo completo definido em `SOUL.md`, **substituindo leitura bruta por queries direcionadas ao RAG**.

Para cada seção da análise, consultar o RAG antes de redigir:

```bash
# Identificação
python3 /data/.openclaw/workspace-gac/skills/financial-rag/rag.py query "Razão social, auditor independente e data de encerramento do exercício" --collection doc_XXXX --top-k 4

# Balanço — Ativo
python3 /data/.openclaw/workspace-gac/skills/financial-rag/rag.py query "Ativo total, circulante e não circulante" --collection doc_XXXX --top-k 8
python3 /data/.openclaw/workspace-gac/skills/financial-rag/rag.py query "Ativo imobilizado, intangível e investimentos" --collection doc_XXXX --top-k 6

# Balanço — Passivo e PL
python3 /data/.openclaw/workspace-gac/skills/financial-rag/rag.py query "Passivo circulante, não circulante e patrimônio líquido" --collection doc_XXXX --top-k 8
python3 /data/.openclaw/workspace-gac/skills/financial-rag/rag.py query "Empréstimos, financiamentos e dívida de longo prazo" --collection doc_XXXX --top-k 6

# DRE
python3 /data/.openclaw/workspace-gac/skills/financial-rag/rag.py query "Receita líquida, lucro bruto e resultado líquido" --collection doc_XXXX --top-k 8
python3 /data/.openclaw/workspace-gac/skills/financial-rag/rag.py query "Despesas financeiras, resultado financeiro e EBIT" --collection doc_XXXX --top-k 6

# Fluxo de Caixa
python3 /data/.openclaw/workspace-gac/skills/financial-rag/rag.py query "Fluxo de caixa das atividades operacionais, investimentos e financiamentos" --collection doc_XXXX --top-k 6

# Notas Explicativas
python3 /data/.openclaw/workspace-gac/skills/financial-rag/rag.py query "Recuperação judicial, going concern e continuidade operacional" --collection doc_XXXX --top-k 6
python3 /data/.openclaw/workspace-gac/skills/financial-rag/rag.py query "Estoques, tributos a recuperar e créditos" --collection doc_XXXX --top-k 5

# Auditoria
python3 /data/.openclaw/workspace-gac/skills/financial-rag/rag.py query "Auditor independente, opinião de auditoria e parágrafos de ênfase" --collection doc_XXXX --top-k 5
```

Os trechos retornados indicam **página e seção** — usar para citar _"conforme página X, seção Y"_ e _"conforme Nota Explicativa nº X"_.

**Subetapas de análise (conforme SOUL.md):**
1. Extração (Companhia, Auditor, Exercício)
2. Cálculo de AV e AH
3. Redação narrativa por seção
4. Parecer e Indicadores
5. Recomendação institucional

---

### Etapa 3 — Geração do Arquivo

Salvar o parecer em:
```
/data/.openclaw/workspace-gac/pareceres/AAAA-MM-DD_EMPRESA_EXERCICIO.md
```

---

### Etapa 4 — Atualização de Memória

Atualizar `memory/EMPRESA.md` com:
- Nome da coleção RAG: `doc_XXXX`
- Indicadores calculados
- Achados relevantes
- Caminho do parecer gerado

Atualizar o índice em `MEMORY.md`.

---

### Etapa 5 — Envio do Parecer por Email

```bash
python3 /data/.openclaw/workspace-gac/send_parecer.py \
  --to "jrxavier@proton.me" \
  --subject "[G.Ac.] Parecer — EMPRESA — Exercício AAAA" \
  --file "/data/.openclaw/workspace-gac/pareceres/ARQUIVO.md"
```

---

### Etapa 6 — Notificação ao Usuário

> "✅ Análise de **[Empresa]** concluída.
> 📄 Parecer salvo em: `/data/.openclaw/workspace-gac/pareceres/ARQUIVO.md`
> 📬 Email enviado de zerix@agentmail.to para jrxavier@proton.me com o parecer em anexo."

---

## Consultas Pontuais (sem pipeline completo)

Quando o usuário fizer perguntas diretas sobre uma empresa (ex: "qual a receita da Padtec?"), o G.Ac. deve:

1. Rodar `rag.py list` para verificar se há documento indexado
2. Se sim: usar `rag.py query` para recuperar o trecho e responder com citação de página/seção
3. Se não: solicitar o documento ao usuário

---

## Ativação Manual de Email

Quando o usuário solicitar manualmente (ex: "manda o parecer da Quality por email"), G.Ac. deve:
1. Verificar se existe o parecer em `pareceres/`
2. Executar o script de envio
3. Avisar o usuário

---

## Script de envio

```bash
python3 /data/.openclaw/workspace-gac/send_parecer.py \
  --to "jrxavier@proton.me" \
  --subject "[G.Ac.] Parecer — EMPRESA — AAAA" \
  --file "/data/.openclaw/workspace-gac/pareceres/ARQUIVO.md"
```

- **De:** zerix@agentmail.to
- **Para:** jrxavier@proton.me
- **Dry-run:** adicionar `--dry-run` para testar sem enviar
