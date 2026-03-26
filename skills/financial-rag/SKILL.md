---
name: financial-rag
description: Indexação semântica e busca híbrida (BM25 + vetorial) sobre PDFs financeiros (DFP, ITR, DRE). Use sempre que receber um PDF financeiro para indexar e consultar seções específicas com precisão.
---

# Skill: financial-rag

Indexação semântica e busca híbrida (BM25 + vetorial) sobre PDFs financeiros.
Usa o projeto `/data/.openclaw/workspace/financial-rag/` como engine.

## Quando usar

Use esta skill **sempre que receber um PDF financeiro** (DFP, ITR, relatório de auditoria).
Em vez de ler o PDF inteiro de uma vez, indexe-o e consulte por seção — mais preciso e eficiente.

**Fluxo obrigatório ao receber PDF:**
1. Indexar o documento com `rag ingest`
2. Usar `rag query` para recuperar seções relevantes antes de redigir cada parte da análise

---

## CLI Wrapper

O wrapper está em `/data/.openclaw/workspace-gac/skills/financial-rag/rag.py`.
Todos os comandos abaixo são chamados via:

```bash
python3 /data/.openclaw/workspace-gac/skills/financial-rag/rag.py <comando> [args]
```

---

## Comandos

### 1. Indexar um PDF

```bash
python3 /data/.openclaw/workspace-gac/skills/financial-rag/rag.py ingest <caminho_pdf>
```

**Saída:** nome da coleção gerada (usar nos próximos comandos).

**Exemplo:**
```bash
python3 /data/.openclaw/workspace-gac/skills/financial-rag/rag.py ingest /tmp/padtec-dfp-2025.pdf
# → Coleção: doc_bd714301c540
```

---

### 2. Consultar o documento indexado

```bash
python3 /data/.openclaw/workspace-gac/skills/financial-rag/rag.py query "<pergunta>" [--collection <nome>] [--top-k <n>]
```

- `--collection` — coleção retornada pelo ingest (obrigatório se houver múltiplos docs indexados)
- `--top-k` — número de chunks a retornar (padrão: 8 — maior que o default do projeto base para análise financeira)

**Retorno:** trechos com página, seção e tipo (texto/tabela).

**Exemplos de queries para análise financeira:**
```bash
# Ativo e passivo
python3 rag.py query "Ativo total, circulante e não circulante" --top-k 8
python3 rag.py query "Passivo circulante e não circulante" --top-k 8

# DRE
python3 rag.py query "Receita líquida, lucro bruto e resultado líquido" --top-k 8
python3 rag.py query "Despesas financeiras e resultado financeiro" --top-k 8

# Fluxo de caixa
python3 rag.py query "Fluxo de caixa das atividades operacionais" --top-k 6

# Notas explicativas
python3 rag.py query "Dívida de longo prazo e empréstimos" --top-k 6
python3 rag.py query "Recuperação judicial e going concern" --top-k 6
python3 rag.py query "Auditor independente e opinião de auditoria" --top-k 4

# Indicadores
python3 rag.py query "Patrimônio líquido e capital social" --top-k 6
python3 rag.py query "Estoques e ativo realizável" --top-k 6
```

---

### 3. Listar documentos indexados

```bash
python3 /data/.openclaw/workspace-gac/skills/financial-rag/rag.py list
```

---

## Integração com o Pipeline G.Ac.

### Etapa 0 — antes de qualquer análise

```bash
# 1. Indexar
python3 /data/.openclaw/workspace-gac/skills/financial-rag/rag.py ingest <pdf>
# Anote o nome da coleção retornada

# 2. Confirmar indexação
python3 /data/.openclaw/workspace-gac/skills/financial-rag/rag.py list
```

### Durante a análise — substituir leitura bruta por queries direcionadas

Para cada seção da análise (Balanço, DRE, Fluxo de Caixa, Notas), fazer a query correspondente e usar os trechos retornados como base documental.

**Exemplo — análise do Ativo:**
```bash
python3 rag.py query "Ativo total, circulante e não circulante" --collection doc_XXXX --top-k 8
python3 rag.py query "Ativo imobilizado e intangível" --collection doc_XXXX --top-k 6
python3 rag.py query "Depósitos judiciais e tributos a recuperar" --collection doc_XXXX --top-k 4
```

Cada trecho retornado traz: **texto, página e seção** — usar para citar _"conforme página X, seção Y"_.

---

## Notas Técnicas

- **Engine:** `/data/.openclaw/workspace/financial-rag/` (projeto compartilhado)
- **Vector store:** ChromaDB em `/data/.openclaw/workspace/financial-rag/data/chroma_db/`
- **Embeddings:** `paraphrase-multilingual-mpnet-base-v2` (PT-BR, offline)
- **Busca:** BM25 + vetorial com Reciprocal Rank Fusion
- **Re-indexação:** segura e idempotente — o mesmo PDF não gera duplicatas
- **Sem API key:** funciona 100% local

---

## Troubleshooting

**Modelo ainda não baixado (primeira vez):**
O modelo de embeddings (~400MB) é baixado automaticamente na primeira execução do ingest.
Pode demorar alguns minutos. As execuções seguintes são rápidas.

**Coleção não encontrada:**
Rode `list` para ver as coleções disponíveis e use o nome correto em `--collection`.

**Chunks irrelevantes retornados:**
Refinar a query — ser mais específico. Ex: em vez de "dívidas", usar "empréstimos e financiamentos de longo prazo notas explicativas".
