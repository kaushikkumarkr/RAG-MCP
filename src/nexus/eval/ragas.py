"""RAGAS evaluation for Nexus RAG system."""

import json
from pathlib import Path
from typing import Any

from loguru import logger


def create_eval_dataset() -> list[dict[str, Any]]:
    """Create evaluation dataset with questions and ground truth.
    
    Returns:
        List of evaluation examples with question, ground_truth, and expected contexts.
    """
    return [
        {
            "question": "What are the three types of machine learning?",
            "ground_truth": "The three types of machine learning are supervised learning (learns from labeled data), unsupervised learning (finds patterns in unlabeled data), and reinforcement learning (learns through trial and error with rewards/penalties).",
            "expected_source": "machine_learning.md",
        },
        {
            "question": "What is a neural network perceptron?",
            "ground_truth": "A perceptron is the simplest form of a neural network where the input layer receives data, weights multiply inputs, an activation function produces output, and it can solve linearly separable problems.",
            "expected_source": "deep_learning.md",
        },
        {
            "question": "What is the ReLU activation function?",
            "ground_truth": "ReLU (Rectified Linear Unit) is defined as f(x) = max(0, x). It is the most popular activation function, helps with the vanishing gradient problem, and is computationally efficient.",
            "expected_source": "deep_learning.md",
        },
        {
            "question": "What are the popular Python libraries for data science?",
            "ground_truth": "Popular Python libraries for data science include NumPy for numerical computing, Pandas for data manipulation, and Matplotlib for visualization.",
            "expected_source": "python_guide.md",
        },
        {
            "question": "What is tokenization in NLP?",
            "ground_truth": "Tokenization is breaking text into individual units (tokens). This includes word tokenization (splitting into words), sentence tokenization (splitting into sentences), and subword tokenization (used in modern transformers).",
            "expected_source": "nlp_fundamentals.md",
        },
        {
            "question": "What are the steps in the CRISP-DM framework?",
            "ground_truth": "The CRISP-DM framework has six phases: Business Understanding, Data Understanding, Data Preparation, Modeling, Evaluation, and Deployment.",
            "expected_source": "data_science_workflow.md",
        },
        {
            "question": "What is Named Entity Recognition?",
            "ground_truth": "Named Entity Recognition (NER) is identifying and classifying named entities in text, including person names, organizations, locations, and dates.",
            "expected_source": "nlp_fundamentals.md",
        },
        {
            "question": "What are transformer models in deep learning?",
            "ground_truth": "Transformers are a modern architecture based on self-attention. They enable parallel processing of sequences, capture long-range dependencies, and are the foundation for BERT, GPT, and other modern models.",
            "expected_source": "deep_learning.md",
        },
        {
            "question": "How do you define a function in Python?",
            "ground_truth": "Functions in Python are defined using the 'def' keyword, followed by the function name and parameters. They can return values and include docstrings for documentation.",
            "expected_source": "python_guide.md",
        },
        {
            "question": "What are word embeddings?",
            "ground_truth": "Word embeddings represent words as dense vectors. Popular methods include Word2Vec (by Google, learns word associations), GloVe (combines matrix factorization with local context), and BERT embeddings (context-aware, pre-trained on massive data).",
            "expected_source": "nlp_fundamentals.md",
        },
    ]


def evaluate_retrieval(
    search_engine,
    eval_data: list[dict[str, Any]],
    top_k: int = 5,
) -> dict[str, Any]:
    """Evaluate retrieval quality using context precision metrics.
    
    Args:
        search_engine: The search engine to evaluate
        eval_data: List of evaluation examples
        top_k: Number of results to retrieve
        
    Returns:
        Dictionary with evaluation metrics
    """
    results = []
    
    for example in eval_data:
        question = example["question"]
        expected_source = example["expected_source"]
        
        # Perform search
        search_results = search_engine.search(query=question, top_k=top_k)
        
        # Check if expected source is in results
        retrieved_sources = [
            Path(r.source).name if r.source else "" 
            for r in search_results
        ]
        
        # Calculate metrics
        hit = expected_source in retrieved_sources
        hit_position = retrieved_sources.index(expected_source) + 1 if hit else 0
        mrr = 1.0 / hit_position if hit else 0.0
        
        results.append({
            "question": question,
            "expected_source": expected_source,
            "retrieved_sources": retrieved_sources[:3],  # Top 3
            "hit@k": hit,
            "hit_position": hit_position,
            "mrr": mrr,
            "top_score": search_results[0].relevance_score if search_results else 0.0,
        })
    
    # Aggregate metrics
    hit_rate = sum(1 for r in results if r["hit@k"]) / len(results)
    avg_mrr = sum(r["mrr"] for r in results) / len(results)
    avg_score = sum(r["top_score"] for r in results) / len(results)
    
    return {
        "metrics": {
            "hit_rate@k": hit_rate,
            "mrr": avg_mrr,
            "avg_top_score": avg_score,
            "num_queries": len(results),
        },
        "details": results,
    }


def run_ragas_evaluation(
    search_engine,
    llm_client=None,
) -> dict[str, Any]:
    """Run full RAGAS evaluation.
    
    Args:
        search_engine: The search engine to evaluate
        llm_client: Optional LLM client for generation metrics
        
    Returns:
        Evaluation results with metrics
    """
    from datetime import datetime
    
    eval_data = create_eval_dataset()
    
    logger.info(f"Running RAGAS evaluation with {len(eval_data)} queries")
    
    # Basic retrieval evaluation (doesn't require LLM)
    retrieval_results = evaluate_retrieval(search_engine, eval_data)
    
    # Format results
    report = {
        "timestamp": datetime.now().isoformat(),
        "evaluation_type": "retrieval",
        "dataset_size": len(eval_data),
        "metrics": retrieval_results["metrics"],
        "per_query": retrieval_results["details"],
    }
    
    return report


def print_evaluation_report(report: dict[str, Any]) -> None:
    """Print evaluation report to console."""
    from rich.console import Console
    from rich.table import Table
    
    console = Console()
    
    console.print("\n[bold cyan]═══ RAGAS Evaluation Report ═══[/bold cyan]\n")
    
    # Metrics table
    metrics = Table(title="Retrieval Metrics")
    metrics.add_column("Metric", style="cyan")
    metrics.add_column("Value", style="green")
    
    m = report["metrics"]
    metrics.add_row("Hit Rate @ K", f"{m['hit_rate@k']:.1%}")
    metrics.add_row("Mean Reciprocal Rank", f"{m['mrr']:.3f}")
    metrics.add_row("Avg Top Score", f"{m['avg_top_score']:.4f}")
    metrics.add_row("Queries Evaluated", str(m["num_queries"]))
    
    console.print(metrics)
    
    # Per-query results
    console.print("\n[bold]Per-Query Results:[/bold]\n")
    
    results = Table(show_header=True)
    results.add_column("#", style="dim")
    results.add_column("Question", width=40)
    results.add_column("Expected", style="cyan")
    results.add_column("Hit?", style="green")
    results.add_column("Pos")
    
    for i, r in enumerate(report["per_query"], 1):
        hit_str = "✓" if r["hit@k"] else "✗"
        pos_str = str(r["hit_position"]) if r["hit_position"] > 0 else "-"
        expected = Path(r["expected_source"]).stem[:15]
        question = r["question"][:37] + "..." if len(r["question"]) > 40 else r["question"]
        
        results.add_row(str(i), question, expected, hit_str, pos_str)
    
    console.print(results)


if __name__ == "__main__":
    # CLI for running evaluation
    import typer
    from pathlib import Path
    
    from nexus.config import load_config
    from nexus.rag.embedder import Embedder
    from nexus.rag.hybrid import HybridSearchEngine
    from nexus.rag.bm25 import BM25Index
    from nexus.storage.metadata import MetadataStore
    from nexus.storage.vectors import VectorStore
    
    app = typer.Typer()
    
    @app.command()
    def evaluate(
        output_path: Path = typer.Option(None, "--output", "-o", help="Save results to JSON"),
    ):
        """Run RAGAS evaluation on the knowledge base."""
        from rich.console import Console
        from rich.progress import Progress, SpinnerColumn, TextColumn
        
        console = Console()
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
            task = progress.add_task("Loading embedding model...", total=None)
            
            embedder = Embedder(model_name=config.embedding.model)
            metadata_store = MetadataStore(config.storage.metadata_db)
            vector_store = VectorStore(
                collection_name=config.storage.collection_name,
                path=config.storage.qdrant_path,
                embedding_dim=embedder.dimension,
            )
            
            progress.update(task, description="Building BM25 index...")
            bm25_index = BM25Index(metadata_store)
            bm25_index.build_index()
            
            engine = HybridSearchEngine(
                embedder=embedder,
                metadata_store=metadata_store,
                vector_store=vector_store,
                bm25_index=bm25_index,
            )
            
            progress.update(task, description="Running evaluation...")
            report = run_ragas_evaluation(engine)
            
            progress.update(task, description="Done!")
        
        print_evaluation_report(report)
        
        if output_path:
            with open(output_path, "w") as f:
                json.dump(report, f, indent=2, default=str)
            console.print(f"\n[green]Results saved to {output_path}[/green]")
        
        metadata_store.close()
        vector_store.close()
    
    app()
