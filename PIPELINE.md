# PIPELINE.md — Protocolo de Pipeline G.Ac. → Tiquinho

## Comando de ativação

O pipeline é ativado quando o usuário enviar (em qualquer variação):
```
Executar pipeline análise sobre [Empresa]
```

---

## Fluxo Obrigatório

### Etapa 1 — Coleta de Fontes (SEMPRE executar primeiro)

Ao receber o comando de pipeline, **antes de qualquer análise**, perguntar:

> "Para iniciar a análise de **[Empresa]**, por favor informe as fontes:
> - URLs de acesso (portal de RI, CVM, link direto de PDF)
> - Arquivos PDF anexados
>
> Há mais de um documento ou fonte a ser considerada? (ex: DFP + Notas Explicativas separadas, múltiplos exercícios)"

Aguardar a resposta antes de continuar. Só iniciar quando o usuário confirmar que forneceu todas as fontes.

### Etapa 2 — Análise

Executar o fluxo completo definido em `SOUL.md`:
1. Extração (Companhia, Auditor, Exercício)
2. Cálculo de AV e AH
3. Redação narrativa por seção
4. Parecer e Indicadores
5. Recomendação institucional

### Etapa 3 — Geração do Arquivo

Salvar o parecer em:
```
/data/.openclaw/workspace-gac/pareceres/AAAA-MM-DD_EMPRESA_EXERCICIO.md
```

### Etapa 4 — Atualização de Memória

Atualizar `memory/EMPRESA.md` e o índice `MEMORY.md`.

### Etapa 5 — Envio do Parecer por Email

Enviar o arquivo diretamente via AgentMail (`zerix@agentmail.to`):

```bash
python3 /data/.openclaw/workspace-gac/send_parecer.py \
  --to "jrxavier@proton.me" \
  --subject "[G.Ac.] Parecer — EMPRESA — Exercício AAAA" \
  --file "/data/.openclaw/workspace-gac/pareceres/ARQUIVO.md"
```

### Etapa 6 — Notificação ao Usuário

Informar:
> "✅ Análise de **[Empresa]** concluída.
> 📄 Parecer salvo em: `/data/.openclaw/workspace-gac/pareceres/ARQUIVO.md`
> 📬 Email enviado de zerix@agentmail.to para jrxavier@proton.me com o parecer em anexo."

---

## Ativação Manual

Quando o usuário solicitar manualmente (ex: "manda o parecer da Quality por email"), G.Ac. deve:
1. Verificar se existe o parecer em `pareceres/`
2. Criar o trigger JSON normalmente
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
- **Anexo:** o arquivo `.md` do parecer
- **Dry-run:** adicionar `--dry-run` para testar sem enviar
