#!/usr/bin/env python3
"""
rag.py — Wrapper CLI do financial-rag para uso pelo G.Ac.
Delega para o projeto /data/.openclaw/workspace/financial-rag/

Uso:
    python3 rag.py ingest <caminho_pdf>
    python3 rag.py query "<pergunta>" [--collection <nome>] [--top-k <n>]
    python3 rag.py list
"""

import sys
import os
import argparse

# Adiciona o projeto financial-rag ao path
RAG_PATH = "/data/.openclaw/workspace/financial-rag"
sys.path.insert(0, RAG_PATH)

# Define DATA_DIR apontando para o projeto base
os.environ.setdefault("DATA_DIR", f"{RAG_PATH}/data")
os.environ.setdefault(
    "EMBEDDING_MODEL",
    "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
)

# Silencia warnings de HuggingFace
os.environ.setdefault("TRANSFORMERS_VERBOSITY", "error")
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")


def cmd_ingest(pdf_path: str) -> None:
    from src.ingest import extract_chunks
    from src.vectorstore import index_chunks

    path_obj = __import__("pathlib").Path(pdf_path)
    if not path_obj.exists():
        print(f"❌ Arquivo não encontrado: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    chunks = extract_chunks(path_obj)
    coll_name = index_chunks(chunks)
    print(f"\n✅ Documento indexado.")
    print(f"   Coleção: {coll_name}")
    print(f"   Chunks: {len(chunks)}")
    print(f"\n   Use nas queries: --collection {coll_name}")


def cmd_query(question: str, collection: str | None, top_k: int) -> None:
    from src.query import query_local, get_available_collections

    if not collection:
        collections = get_available_collections()
        if not collections:
            print("❌ Nenhum documento indexado. Rode primeiro: rag.py ingest <pdf>", file=sys.stderr)
            sys.exit(1)
        collection = collections[-1]  # usa o mais recente
        if len(collections) > 1:
            print(f"ℹ️  Múltiplas coleções disponíveis. Usando a mais recente: {collection}")
            print(f"   Disponíveis: {', '.join(collections)}\n")

    result = query_local(question, collection, top_k=top_k)

    print("\n" + "=" * 70)
    print(f"🔎 QUERY: {question}")
    print("=" * 70)

    if not result["chunks"]:
        print("Nenhum trecho relevante encontrado.")
        return

    for i, chunk in enumerate(result["chunks"], 1):
        meta = chunk["metadata"]
        print(f"\n[{i}] Página {meta.get('page', '?')} | Seção: {meta.get('section', '?')} | Tipo: {meta.get('chunk_type', '?')}")
        print("-" * 60)
        print(chunk["text"])

    print("\n" + "=" * 70)
    print(f"Total de chunks: {len(result['chunks'])}")


def cmd_list() -> None:
    from src.vectorstore import list_collections, _get_client

    collections = list_collections()
    if not collections:
        print("📭 Nenhum documento indexado.")
        return

    client = _get_client()
    print(f"\n📚 Documentos indexados ({len(collections)}):\n")
    for name in collections:
        coll = client.get_collection(name)
        count = coll.count()
        sample = coll.get(limit=1, include=["metadatas"])
        doc_name = sample["metadatas"][0].get("doc_name", "?") if sample["metadatas"] else "?"
        print(f"  • {name}")
        print(f"    Documento: {doc_name}")
        print(f"    Chunks: {count}\n")


def main():
    parser = argparse.ArgumentParser(
        description="financial-rag — wrapper para G.Ac.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # ingest
    p_ingest = subparsers.add_parser("ingest", help="Indexa um PDF")
    p_ingest.add_argument("pdf", help="Caminho para o arquivo PDF")

    # query
    p_query = subparsers.add_parser("query", help="Consulta o documento indexado")
    p_query.add_argument("question", help="Pergunta em linguagem natural")
    p_query.add_argument("--collection", "-c", help="Nome da coleção (padrão: mais recente)")
    p_query.add_argument("--top-k", "-k", type=int, default=8, help="Chunks a retornar (padrão: 8)")

    # list
    subparsers.add_parser("list", help="Lista documentos indexados")

    args = parser.parse_args()

    if args.command == "ingest":
        cmd_ingest(args.pdf)
    elif args.command == "query":
        cmd_query(args.question, args.collection, args.top_k)
    elif args.command == "list":
        cmd_list()


if __name__ == "__main__":
    main()
