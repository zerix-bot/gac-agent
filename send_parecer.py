#!/usr/bin/env python3
"""
send_parecer.py — Envia parecer G.Ac. via AgentMail (zerix@agentmail.to)
Uso: python3 send_parecer.py --to EMAIL --subject ASSUNTO --file CAMINHO_MD [--dry-run]
"""

import argparse
import base64
import os
import sys

def main():
    parser = argparse.ArgumentParser(description="Envia parecer G.Ac. via AgentMail")
    parser.add_argument("--to", required=True, help="Destinatário")
    parser.add_argument("--subject", required=True, help="Assunto")
    parser.add_argument("--file", required=True, help="Caminho do arquivo .md")
    parser.add_argument("--dry-run", action="store_true", help="Simular sem enviar")
    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"ERRO: arquivo não encontrado: {args.file}", file=sys.stderr)
        sys.exit(1)

    api_key = os.getenv("AGENTMAIL_API_KEY", "am_us_b659045f3b81fd9a957ca68e9ae25dfdd5b769164d60296801fa0cef420005f8")
    inbox_id = "zerix@agentmail.to"

    with open(args.file, "r", encoding="utf-8") as f:
        conteudo_md = f.read()

    filename = os.path.basename(args.file)
    attachment_b64 = base64.b64encode(conteudo_md.encode("utf-8")).decode("utf-8")

    body_text = (
        f"Prezado(a) José Ricardo,\n\n"
        f"Segue em anexo o parecer técnico produzido pelo G.Ac. — "
        f"Grupo de Acompanhamento de Contas (BNDES).\n\n"
        f"O documento completo está anexado a este email.\n\n"
        f"Atenciosamente,\nG.Ac. | BNDES"
    )

    if args.dry_run:
        print("✅ DRY-RUN — email construído com sucesso (não enviado)")
        print(f"   De:      {inbox_id}")
        print(f"   Para:    {args.to}")
        print(f"   Assunto: {args.subject}")
        print(f"   Anexo:   {filename} ({len(conteudo_md)} chars)")
        return

    from agentmail import AgentMail
    client = AgentMail(api_key=api_key)

    client.inboxes.messages.send(
        inbox_id=inbox_id,
        to=args.to,
        subject=args.subject,
        text=body_text,
        attachments=[{
            "filename": filename,
            "content": attachment_b64
        }]
    )

    print(f"✅ Email enviado com sucesso!")
    print(f"   De:      {inbox_id}")
    print(f"   Para:    {args.to}")
    print(f"   Assunto: {args.subject}")
    print(f"   Anexo:   {filename}")

if __name__ == "__main__":
    main()
