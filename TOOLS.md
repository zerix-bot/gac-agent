# TOOLS.md - G.Ac. Tools

## Escopo de Ferramentas

G.Ac. opera sobre documentos fornecidos pelo usuário — diretamente como arquivo anexo **ou via URL**. As ferramentas principais são:

---

## Obtenção de Documentos via URL

Quando o usuário fornecer uma URL, o G.Ac. deve:

### 1. URL de página web (CVM, RI, portal de empresa)
Usar **Firecrawl** para scraping do conteúdo:
```bash
python3 -c "
from firecrawl import FirecrawlApp
app = FirecrawlApp(api_key='$FIRECRAWL_API_KEY')
result = app.scrape('URL_AQUI', formats=['markdown'])
print(result['markdown'])
"
```

### 2. URL direta de PDF
Fazer download e processar com a ferramenta `pdf`:
```bash
# Download do arquivo
curl -L -o /tmp/documento_gac.pdf "URL_DO_PDF"
```
Em seguida, usar a ferramenta `pdf` para leitura e extração do conteúdo.

### 3. Fluxo de decisão ao receber URL
1. Verificar se a URL termina em `.pdf` ou redireciona para PDF
2. Se **PDF direto** → baixar e usar ferramenta `pdf`
3. Se **página web** → usar Firecrawl para extrair markdown
4. Se a página contiver links para PDFs (ex: CVM ENET) → baixar o PDF referenciado e processar

---

## Email — AgentMail

G.Ac. envia emails diretamente via **AgentMail** (`zerix@agentmail.to`).

```bash
python3 /data/.openclaw/workspace-gac/send_parecer.py \
  --to "jrxavier@proton.me" \
  --subject "[G.Ac.] Parecer — EMPRESA — AAAA" \
  --file "/caminho/do/parecer.md"
```

- API Key: `$AGENTMAIL_API_KEY` (já configurada no ambiente)
- Inbox: `zerix@agentmail.to`
- Destinatário padrão: `jrxavier@proton.me`

---

## Análise de Documentos

### ⭐ financial-rag (PADRÃO para PDFs)

Skill de RAG semântico — **usar sempre que receber um PDF financeiro**.
Mais preciso que leitura bruta: indexa o documento e permite queries por seção.

```bash
# 1. Indexar o PDF (fazer primeiro, sempre)
python3 /data/.openclaw/workspace-gac/skills/financial-rag/rag.py ingest <caminho_pdf>

# 2. Consultar seções específicas durante a análise
python3 /data/.openclaw/workspace-gac/skills/financial-rag/rag.py query "Ativo total e circulante" --collection doc_XXXX --top-k 8

# 3. Ver documentos já indexados
python3 /data/.openclaw/workspace-gac/skills/financial-rag/rag.py list
```

Consulte `skills/financial-rag/SKILL.md` para lista completa de queries recomendadas por seção.

### Outros

- **pdf** (ferramenta nativa): fallback se o financial-rag não estiver disponível
- **Firecrawl**: Scraping de páginas web com documentos ou tabelas financeiras
- **Planilhas/Tabelas**: Processamento de dados numéricos para cálculo de AV e AH

## Cálculos Obrigatórios

**Análise Vertical (AV%)**
- Ativo/Passivo: conta ÷ Total do Ativo × 100
- DRE: conta ÷ Receita Líquida × 100

**Análise Horizontal (AH%)**
- (Saldo Atual − Saldo Anterior) ÷ |Saldo Anterior| × 100

**Indicadores de Liquidez**
- Corrente: AC ÷ PC
- Seca: (AC − Estoques) ÷ PC
- Geral: (AC + RLP) ÷ (PC + PNC)

**Indicadores de Estrutura de Capital**
- Endividamento Geral: PT ÷ AT
- Imobilização do PL: AP ÷ PL
- Cobertura de Juros: EBIT ÷ Despesas Financeiras

## Padrão de Citação

Sempre referenciar: _"conforme Nota Explicativa nº X"_
