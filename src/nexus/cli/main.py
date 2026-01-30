"""Nexus CLI - Command Line Interface."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

app = typer.Typer(
    name="nexus",
    help="Nexus: Personal Knowledge MCP Server",
    add_completion=False,
)
console = Console()


@app.command()
def version() -> None:
    """Show version information."""
    from nexus import __version__

    console.print(f"Nexus v{__version__}")


@app.command()
def init(
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing config"),
) -> None:
    """Initialize Nexus configuration."""
    from nexus.config import create_default_config, save_config

    config_path = Path("~/.nexus/config.yaml").expanduser()
    if config_path.exists() and not force:
        console.print(f"[yellow]Config already exists at {config_path}[/yellow]")
        console.print("Use --force to overwrite")
        return

    config = create_default_config()
    save_config(config, config_path)

    # Create directories
    config.storage.qdrant_path.mkdir(parents=True, exist_ok=True)
    config.storage.metadata_db.parent.mkdir(parents=True, exist_ok=True)
    config.notes_dir.mkdir(parents=True, exist_ok=True)

    console.print(f"[green]✓ Created config at {config_path}[/green]")
    console.print(f"[green]✓ Created storage directories[/green]")
    console.print("\nNext steps:")
    console.print("  1. Add sources to config: nexus add-source <path>")
    console.print("  2. Index content: nexus index")
    console.print("  3. Start server: nexus serve")


@app.command()
def status() -> None:
    """Show Nexus status and statistics."""
    from nexus.config import load_config
    from nexus.storage.metadata import MetadataStore
    from nexus.storage.vectors import VectorStore

    config_path = Path("~/.nexus/config.yaml").expanduser()
    if not config_path.exists():
        console.print("[red]Nexus not initialized. Run 'nexus init' first.[/red]")
        raise typer.Exit(1)

    config = load_config(config_path)

    table = Table(title="Nexus Status")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Config", str(config_path))
    table.add_row("Embedding Model", config.embedding.model)
    table.add_row("Configured Sources", str(len(config.sources)))

    # Get database stats if available
    if config.storage.metadata_db.exists():
        try:
            store = MetadataStore(config.storage.metadata_db)
            stats = store.get_stats()
            table.add_row("Documents", str(stats.get("documents", 0)))
            table.add_row("Chunks", str(stats.get("chunks", 0)))
            store.close()
        except Exception:
            table.add_row("Database", "[yellow]Not accessible[/yellow]")
    else:
        table.add_row("Database", "[yellow]Not created[/yellow]")

    console.print(table)


@app.command()
def index(
    path: Optional[Path] = typer.Argument(None, help="Path to index (defaults to configured sources)"),
    recursive: bool = typer.Option(True, "--recursive/--no-recursive", "-r", help="Recursively index directories"),
) -> None:
    """Index documents into the knowledge base."""
    from nexus.config import load_config
    from nexus.ingest.pipeline import IngestionPipeline
    from nexus.ingest.chunker import TextChunker
    from nexus.rag.embedder import Embedder
    from nexus.storage.metadata import MetadataStore
    from nexus.storage.vectors import VectorStore

    config_path = Path("~/.nexus/config.yaml").expanduser()
    if not config_path.exists():
        console.print("[red]Nexus not initialized. Run 'nexus init' first.[/red]")
        raise typer.Exit(1)

    config = load_config(config_path)

    # Determine paths to index
    paths_to_index: list[Path] = []
    if path:
        paths_to_index.append(path.expanduser().resolve())
    else:
        for source in config.sources:
            paths_to_index.append(source.path.expanduser().resolve())

    if not paths_to_index:
        console.print("[yellow]No sources configured. Add a source with 'nexus add-source' or provide a path.[/yellow]")
        raise typer.Exit(1)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        # Initialize embedder
        task = progress.add_task("Loading embedding model...", total=None)
        embedder = Embedder(
            model_name=config.embedding.model,
            batch_size=config.embedding.batch_size,
        )
        _ = embedder.dimension  # Force model load
        progress.update(task, description=f"[green]✓ Loaded {config.embedding.model}[/green]")

        # Initialize stores
        progress.update(task, description="Initializing storage...")
        metadata_store = MetadataStore(config.storage.metadata_db)
        vector_store = VectorStore(
            collection_name=config.storage.collection_name,
            path=config.storage.qdrant_path,
            embedding_dim=embedder.dimension,
        )

        # Create pipeline
        pipeline = IngestionPipeline(
            embedder=embedder,
            metadata_store=metadata_store,
            vector_store=vector_store,
            chunker=TextChunker(
                chunk_size=config.chunking.chunk_size,
                chunk_overlap=config.chunking.chunk_overlap,
                min_chunk_size=config.chunking.min_chunk_size,
            ),
        )

        # Index each path
        total_docs = 0
        for index_path in paths_to_index:
            if index_path.is_file():
                progress.update(task, description=f"Indexing {index_path.name}...")
                doc = pipeline.ingest_file(index_path)
                if doc:
                    total_docs += 1
            elif index_path.is_dir():
                progress.update(task, description=f"Indexing {index_path}...")
                docs = pipeline.ingest_directory(index_path, recursive=recursive)
                total_docs += len(docs)
            else:
                console.print(f"[yellow]Skipping {index_path}: not found[/yellow]")

        progress.update(task, description=f"[green]✓ Indexed {total_docs} documents[/green]")

        # Clean up
        metadata_store.close()
        vector_store.close()

    # Show stats
    console.print()
    status()


@app.command()
def serve(
    stdio: bool = typer.Option(True, "--stdio/--no-stdio", help="Use stdio transport (for MCP)"),
) -> None:
    """Start the Nexus MCP server."""
    from nexus.config import load_config
    from nexus.tools.server import NexusServer

    config_path = Path("~/.nexus/config.yaml").expanduser()
    if not config_path.exists():
        console.print("[red]Nexus not initialized. Run 'nexus init' first.[/red]")
        raise typer.Exit(1)

    config = load_config(config_path)

    if stdio:
        console.print("[cyan]Starting Nexus MCP server (stdio)...[/cyan]", err=True)
        import asyncio
        server = NexusServer(config=config)
        try:
            asyncio.run(server.run_stdio())
        finally:
            server.close()
    else:
        console.print("[yellow]HTTP transport not yet implemented[/yellow]")


@app.command("add-source")
def add_source(
    path: Path = typer.Argument(..., help="Path to add as source"),
    source_type: str = typer.Option("markdown", "--type", "-t", help="Source type (markdown, text)"),
    watch: bool = typer.Option(True, "--watch/--no-watch", help="Watch for changes"),
) -> None:
    """Add a source directory to the configuration."""
    from nexus.config import load_config, save_config, SourceConfig

    config_path = Path("~/.nexus/config.yaml").expanduser()
    if not config_path.exists():
        console.print("[red]Nexus not initialized. Run 'nexus init' first.[/red]")
        raise typer.Exit(1)

    resolved_path = path.expanduser().resolve()
    if not resolved_path.exists():
        console.print(f"[red]Path does not exist: {resolved_path}[/red]")
        raise typer.Exit(1)

    config = load_config(config_path)

    # Check if already added
    for source in config.sources:
        if source.path.expanduser().resolve() == resolved_path:
            console.print(f"[yellow]Source already configured: {resolved_path}[/yellow]")
            return

    # Add source
    new_source = SourceConfig(
        path=resolved_path,
        type=source_type,
        watch=watch,
    )
    config.sources.append(new_source)
    save_config(config, config_path)

    console.print(f"[green]✓ Added source: {resolved_path}[/green]")
    console.print(f"Run 'nexus index' to index this source")


@app.command("list-sources")
def list_sources() -> None:
    """List configured sources."""
    from nexus.config import load_config

    config_path = Path("~/.nexus/config.yaml").expanduser()
    if not config_path.exists():
        console.print("[red]Nexus not initialized. Run 'nexus init' first.[/red]")
        raise typer.Exit(1)

    config = load_config(config_path)

    if not config.sources:
        console.print("[yellow]No sources configured. Use 'nexus add-source' to add one.[/yellow]")
        return

    table = Table(title="Configured Sources")
    table.add_column("Path", style="cyan")
    table.add_column("Type", style="green")
    table.add_column("Watch", style="yellow")

    for source in config.sources:
        table.add_row(
            str(source.path),
            source.type,
            "✓" if source.watch else "✗",
        )

    console.print(table)


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query"),
    limit: int = typer.Option(5, "--limit", "-n", help="Number of results"),
) -> None:
    """Search the knowledge base."""
    from nexus.config import load_config
    from nexus.rag.embedder import Embedder
    from nexus.rag.hybrid import HybridSearchEngine
    from nexus.rag.bm25 import BM25Index
    from nexus.storage.metadata import MetadataStore
    from nexus.storage.vectors import VectorStore

    config_path = Path("~/.nexus/config.yaml").expanduser()
    if not config_path.exists():
        console.print("[red]Nexus not initialized. Run 'nexus init' first.[/red]")
        raise typer.Exit(1)

    config = load_config(config_path)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Loading...", total=None)

        embedder = Embedder(model_name=config.embedding.model)
        metadata_store = MetadataStore(config.storage.metadata_db)
        vector_store = VectorStore(
            collection_name=config.storage.collection_name,
            path=config.storage.qdrant_path,
            embedding_dim=embedder.dimension,
        )

        bm25_index = BM25Index(metadata_store)
        bm25_index.build_index()

        engine = HybridSearchEngine(
            embedder=embedder,
            metadata_store=metadata_store,
            vector_store=vector_store,
            bm25_index=bm25_index,
        )

        progress.update(task, description="Searching...")
        results = engine.search(query=query, top_k=limit)

        progress.update(task, description="Done")

    console.print()
    if not results:
        console.print("[yellow]No results found.[/yellow]")
        return

    console.print(f"[green]Found {len(results)} results:[/green]\n")

    for i, r in enumerate(results, 1):
        console.print(f"[cyan]─── Result {i} ───[/cyan]")
        if r.title:
            console.print(f"[bold]{r.title}[/bold]")
        if r.heading:
            console.print(f"[dim]> {r.heading}[/dim]")
        console.print(f"[dim]Source: {r.source}[/dim]")
        console.print(f"Score: {r.relevance_score:.3f}")
        console.print()
        console.print(r.content[:500] + "..." if len(r.content) > 500 else r.content)
        console.print()

    metadata_store.close()
    vector_store.close()


if __name__ == "__main__":
    app()
