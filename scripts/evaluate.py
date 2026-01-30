
import asyncio
import sys
import os
from pathlib import Path
import pandas as pd
from datasets import Dataset

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from nexus.config import load_config
from nexus.rag.hybrid import HybridSearchEngine
from nexus.rag.embedder import Embedder
from nexus.rag.bm25 import BM25Index
from nexus.storage.metadata import MetadataStore
from nexus.storage.vectors import VectorStore

# RAGAS Imports
try:
    from ragas import evaluate
    from ragas.metrics import (
        context_precision,
        context_recall,
        context_relevancy,
    )
except ImportError:
    print("❌ RAGAS not installed. Please run: pip install ragas")
    sys.exit(1)

# Sample Ground Truth Dataset (Small for demo)
TEST_DATA = [
    {
        "question": "What libraries are used for the Financial Dashboard?",
        "ground_truth": "React and Python are used for the Financial Dashboard.",
        "search_term": "Financial Dashboard"
    },
    {
        "question": "What is the chunk size configuration?",
        "ground_truth": "The default chunk size is 512 characters.",
        "search_term": "chunk size"
    },
    {
        "question": "How do I add a source directory?",
        "ground_truth": "Use the command `nexus add-source <path>`.",
        "search_term": "add-source"
    }
]

async def run_evaluation():
    print("📊 Starting Nexus RAG Evaluation...")
    
    # 1. Initialize Engine
    config = load_config()
    embedder = Embedder(model_name=config.embedding.model)
    metadata_store = MetadataStore(config.storage.metadata_db)
    vector_store = VectorStore(
        collection_name=config.storage.collection_name,
        path=config.storage.qdrant_path,
        embedding_dim=embedder.dimension,
    )
    bm25_index = BM25Index(metadata_store)
    bm25_index.build_index()
    
    engine = HybridSearchEngine(embedder, metadata_store, vector_store, bm25_index)
    
    # 2. Collect Retrieval Results
    data_points = {
        "question": [],
        "contexts": [],
        "ground_truth": []
    }
    
    print("\n🔍 Retrieving Contexts for Test Set...")
    for item in TEST_DATA:
        results = engine.search(item["question"], top_k=3)
        contexts = [r.content for r in results]
        
        data_points["question"].append(item["question"])
        data_points["contexts"].append(contexts)
        data_points["ground_truth"].append(item["ground_truth"])
        
        print(f"   - Q: {item['question']}")
        print(f"     Found {len(contexts)} contexts.")

    # 3. Prepare Dataset for RAGAS
    dataset = Dataset.from_dict(data_points)
    
    # 4. Run Evaluation
    # Note: RAGAS typically requires an OpenAI Key for the 'Critic' LLM.
    # If not present, this might fail or we need to configure a local judge.
    if not os.environ.get("OPENAI_API_KEY"):
        print("\n⚠️  No OPENAI_API_KEY found. Skipping detailed RAGAS/LLM-based metrics.")
        print("ℹ️  Calculating Retrieval Metrics based on Reranker Scores (Proxy)...")
        
        # Fallback: Calculate mean reranker score
        total_score = 0
        count = 0
        for item in TEST_DATA:
            results = engine.search(item["question"], top_k=3)
            if results:
                total_score += results[0].relevance_score
                count += 1
        
        print(f"\n📈 Mean Top-1 Relevance Score (Cross-Encoder): {total_score/count:.4f}")
        return

    print("\n🧐 Running RAGAS Metrics (Context Precision/Recall)...")
    results = evaluate(
        dataset=dataset,
        metrics=[
            context_precision,
            context_relevancy,
            context_recall
        ],
    )
    
    print("\n🏆 Evaluation Results:")
    print(results)
    
    # Save results
    df = results.to_pandas()
    df.to_csv("evaluation_results.csv")
    print("\n✅ Results saved to evaluation_results.csv")

if __name__ == "__main__":
    asyncio.run(run_evaluation())
