"""Extended RAGAS evaluation with LLM judge support."""

import json
from pathlib import Path
from typing import Any

from loguru import logger


def create_extended_eval_dataset() -> list[dict[str, Any]]:
    """Create 50+ question evaluation dataset.
    
    Returns:
        List of evaluation examples with question, ground_truth, and expected contexts.
    """
    return [
        # Machine Learning - 10 questions
        {"question": "What are the three types of machine learning?", "ground_truth": "Supervised learning, unsupervised learning, and reinforcement learning.", "expected_source": "machine_learning.md"},
        {"question": "What is supervised learning?", "ground_truth": "Supervised learning is when the algorithm learns from labeled training data and makes predictions based on that data.", "expected_source": "machine_learning.md"},
        {"question": "What is unsupervised learning?", "ground_truth": "Unsupervised learning is when the algorithm finds patterns in unlabeled data without guidance.", "expected_source": "machine_learning.md"},
        {"question": "What is reinforcement learning?", "ground_truth": "Reinforcement learning is when the algorithm learns through trial and error, receiving rewards or penalties for actions.", "expected_source": "machine_learning.md"},
        {"question": "What are features in machine learning?", "ground_truth": "Features are input variables used to make predictions, such as age or income.", "expected_source": "machine_learning.md"},
        {"question": "What are labels in machine learning?", "ground_truth": "Labels are output variables we want to predict.", "expected_source": "machine_learning.md"},
        {"question": "What is a decision tree?", "ground_truth": "Decision trees are tree-like models where each internal node represents a test on an attribute, each branch represents the outcome, and each leaf node represents a class label.", "expected_source": "machine_learning.md"},
        {"question": "What are support vector machines?", "ground_truth": "SVMs are supervised learning models used for classification and regression that work by finding the hyperplane that best separates different classes.", "expected_source": "machine_learning.md"},
        {"question": "What are some applications of machine learning?", "ground_truth": "Email spam filtering, image recognition, medical diagnosis, fraud detection, recommendation systems, and self-driving cars.", "expected_source": "machine_learning.md"},
        {"question": "How do I get started with machine learning?", "ground_truth": "Learn Python programming, understand basic statistics and linear algebra, practice with libraries like scikit-learn, TensorFlow, or PyTorch.", "expected_source": "machine_learning.md"},
        
        # Deep Learning - 12 questions
        {"question": "What is deep learning?", "ground_truth": "Deep learning is a subset of machine learning that uses neural networks with many layers to analyze data.", "expected_source": "deep_learning.md"},
        {"question": "What is a neural network perceptron?", "ground_truth": "A perceptron is the simplest form of a neural network with input layer, weights, and activation function.", "expected_source": "deep_learning.md"},
        {"question": "What is the ReLU activation function?", "ground_truth": "ReLU (Rectified Linear Unit) is defined as f(x) = max(0, x), the most popular activation function.", "expected_source": "deep_learning.md"},
        {"question": "What is the sigmoid activation function?", "ground_truth": "Sigmoid outputs between 0 and 1, used in binary classification, can cause vanishing gradients.", "expected_source": "deep_learning.md"},
        {"question": "What is softmax?", "ground_truth": "Softmax converts outputs to probability distribution where all outputs sum to 1, used in multi-class classification.", "expected_source": "deep_learning.md"},
        {"question": "What are CNNs?", "ground_truth": "Convolutional Neural Networks are designed for processing grid-like data like images, using convolutional and pooling layers.", "expected_source": "deep_learning.md"},
        {"question": "What are RNNs?", "ground_truth": "Recurrent Neural Networks are designed for sequential data, maintaining hidden state across time steps.", "expected_source": "deep_learning.md"},
        {"question": "What is LSTM?", "ground_truth": "Long Short-Term Memory is an advanced RNN that solves vanishing gradient problem with memory cells and gates.", "expected_source": "deep_learning.md"},
        {"question": "What are transformers?", "ground_truth": "Transformers are modern architecture based on self-attention, enabling parallel processing and capturing long-range dependencies.", "expected_source": "deep_learning.md"},
        {"question": "What is dropout regularization?", "ground_truth": "Dropout randomly disables neurons during training to prevent overfitting.", "expected_source": "deep_learning.md"},
        {"question": "What is TensorFlow?", "ground_truth": "TensorFlow is Google's open-source deep learning framework, production-ready with TensorBoard for visualization.", "expected_source": "deep_learning.md"},
        {"question": "What is PyTorch?", "ground_truth": "PyTorch is Meta's research-friendly deep learning framework with dynamic computational graphs.", "expected_source": "deep_learning.md"},
        
        # Python - 10 questions
        {"question": "Why is Python popular?", "ground_truth": "Python is easy to learn, versatile, has a large ecosystem, and strong community support.", "expected_source": "python_guide.md"},
        {"question": "How do you define a function in Python?", "ground_truth": "Functions are defined using the 'def' keyword, followed by function name and parameters.", "expected_source": "python_guide.md"},
        {"question": "What are Python data types?", "ground_truth": "Numbers (int, float), strings, lists, and dictionaries.", "expected_source": "python_guide.md"},
        {"question": "How do you create a Python class?", "ground_truth": "Use the 'class' keyword with __init__ method for initialization and self for instance attributes.", "expected_source": "python_guide.md"},
        {"question": "What is NumPy?", "ground_truth": "NumPy is a library for numerical computing with arrays.", "expected_source": "python_guide.md"},
        {"question": "What is Pandas?", "ground_truth": "Pandas is a library for data manipulation and analysis.", "expected_source": "python_guide.md"},
        {"question": "What is Django?", "ground_truth": "Django is a full-featured web framework for Python.", "expected_source": "python_guide.md"},
        {"question": "What is Flask?", "ground_truth": "Flask is a lightweight web framework for Python.", "expected_source": "python_guide.md"},
        {"question": "What is PEP 8?", "ground_truth": "PEP 8 is the Python style guide for writing clean, readable code.", "expected_source": "python_guide.md"},
        {"question": "How do you use virtual environments?", "ground_truth": "Use virtualenv or conda to create isolated Python environments.", "expected_source": "python_guide.md"},
        
        # NLP - 12 questions
        {"question": "What is NLP?", "ground_truth": "Natural Language Processing is a branch of AI that helps computers understand human language.", "expected_source": "nlp_fundamentals.md"},
        {"question": "What is tokenization?", "ground_truth": "Tokenization is breaking text into individual units (tokens) like words or sentences.", "expected_source": "nlp_fundamentals.md"},
        {"question": "What is Named Entity Recognition?", "ground_truth": "NER is identifying and classifying named entities like person names, organizations, and locations.", "expected_source": "nlp_fundamentals.md"},
        {"question": "What is Part-of-Speech tagging?", "ground_truth": "POS tagging labels words with their grammatical category like nouns, verbs, adjectives.", "expected_source": "nlp_fundamentals.md"},
        {"question": "What is text preprocessing?", "ground_truth": "Lowercasing, removing punctuation, removing stop words, stemming, and lemmatization.", "expected_source": "nlp_fundamentals.md"},
        {"question": "What is Word2Vec?", "ground_truth": "Word2Vec is a Google model that learns word associations from text, with similar words having similar vectors.", "expected_source": "nlp_fundamentals.md"},
        {"question": "What is GloVe?", "ground_truth": "GloVe (Global Vectors) combines matrix factorization with local context for word representations.", "expected_source": "nlp_fundamentals.md"},
        {"question": "What are BERT embeddings?", "ground_truth": "BERT embeddings are context-aware, pre-trained on massive text data, state-of-the-art for many NLP tasks.", "expected_source": "nlp_fundamentals.md"},
        {"question": "What is spaCy?", "ground_truth": "spaCy is an industrial-strength NLP library that is fast and efficient.", "expected_source": "nlp_fundamentals.md"},
        {"question": "What is NLTK?", "ground_truth": "NLTK (Natural Language Toolkit) is comprehensive text processing library for education and research.", "expected_source": "nlp_fundamentals.md"},
        {"question": "What is Hugging Face Transformers?", "ground_truth": "Hugging Face Transformers provides modern transformer models like BERT, GPT, RoBERTa with easy-to-use API.", "expected_source": "nlp_fundamentals.md"},
        {"question": "What are challenges in NLP?", "ground_truth": "Ambiguity, context dependence, sarcasm/irony detection, low-resource languages, and model bias.", "expected_source": "nlp_fundamentals.md"},
        
        # Data Science - 8 questions
        {"question": "What is the CRISP-DM framework?", "ground_truth": "CRISP-DM has six phases: Business Understanding, Data Understanding, Data Preparation, Modeling, Evaluation, Deployment.", "expected_source": "data_science_workflow.md"},
        {"question": "What is exploratory data analysis?", "ground_truth": "EDA includes summary statistics, distribution analysis, correlation analysis, and outlier detection.", "expected_source": "data_science_workflow.md"},
        {"question": "What is feature engineering?", "ground_truth": "Creating meaningful features from raw data like one-hot encoding, binning, and time-based features.", "expected_source": "data_science_workflow.md"},
        {"question": "What is Matplotlib?", "ground_truth": "Matplotlib is a basic Python plotting library for data visualization.", "expected_source": "data_science_workflow.md"},
        {"question": "What is Seaborn?", "ground_truth": "Seaborn is a statistical visualization library built on Matplotlib.", "expected_source": "data_science_workflow.md"},
        {"question": "What is XGBoost?", "ground_truth": "XGBoost is a gradient boosting library for machine learning.", "expected_source": "data_science_workflow.md"},
        {"question": "What metrics are used for classification?", "ground_truth": "Accuracy, Precision, Recall, F1-score, ROC-AUC, and confusion matrix.", "expected_source": "data_science_workflow.md"},
        {"question": "What is the role of a data scientist vs ML engineer?", "ground_truth": "Data scientists build predictive models; ML engineers deploy ML systems at scale.", "expected_source": "data_science_workflow.md"},
    ]


def evaluate_with_llm(
    search_engine,
    llm_client,
    eval_data: list[dict[str, Any]],
    top_k: int = 5,
) -> dict[str, Any]:
    """Evaluate RAG with LLM as judge (RAGAS-style).
    
    Args:
        search_engine: Search engine to evaluate
        llm_client: LLM client for generating answers and judging
        eval_data: Evaluation dataset
        top_k: Number of results to retrieve
        
    Returns:
        Evaluation results with metrics
    """
    results = []
    
    for example in eval_data:
        question = example["question"]
        ground_truth = example["ground_truth"]
        expected_source = example["expected_source"]
        
        # Retrieve contexts
        search_results = search_engine.search(query=question, top_k=top_k)
        contexts = [r.content for r in search_results]
        sources = [Path(r.source).name if r.source else "" for r in search_results]
        
        # Generate answer using LLM
        context_text = "\n\n".join(contexts)
        generation_prompt = f"""Based on the following context, answer the question concisely.

Context:
{context_text}

Question: {question}

Answer:"""
        
        try:
            answer = llm_client.generate(generation_prompt, temperature=0.1, max_tokens=200)
        except Exception as e:
            answer = f"Error: {e}"
        
        # Judge faithfulness (is answer grounded in context?)
        faithfulness_prompt = f"""Judge if the answer is fully supported by the context.

Context:
{context_text}

Answer: {answer}

Rate faithfulness from 0 to 1 (1 = fully grounded). Reply with just a number."""
        
        try:
            faithfulness = float(llm_client.generate(faithfulness_prompt, temperature=0, max_tokens=10))
        except:
            faithfulness = 0.5
        
        # Judge answer relevancy (does answer address the question?)
        relevancy_prompt = f"""Judge if the answer addresses the question.

Question: {question}
Answer: {answer}

Rate relevancy from 0 to 1 (1 = fully addresses question). Reply with just a number."""
        
        try:
            relevancy = float(llm_client.generate(relevancy_prompt, temperature=0, max_tokens=10))
        except:
            relevancy = 0.5
        
        # Context precision (was expected source retrieved?)
        hit = expected_source in sources
        hit_position = sources.index(expected_source) + 1 if hit else 0
        context_precision = 1.0 / hit_position if hit else 0.0
        
        results.append({
            "question": question,
            "answer": answer,
            "ground_truth": ground_truth,
            "contexts": contexts[:2],  # Store first 2 for brevity
            "expected_source": expected_source,
            "hit": hit,
            "faithfulness": faithfulness,
            "answer_relevancy": relevancy,
            "context_precision": context_precision,
        })
    
    # Aggregate metrics
    n = len(results)
    metrics = {
        "hit_rate": sum(1 for r in results if r["hit"]) / n,
        "avg_faithfulness": sum(r["faithfulness"] for r in results) / n,
        "avg_answer_relevancy": sum(r["answer_relevancy"] for r in results) / n,
        "avg_context_precision": sum(r["context_precision"] for r in results) / n,
        "num_queries": n,
    }
    
    return {"metrics": metrics, "details": results}


# For backwards compatibility
create_eval_dataset = create_extended_eval_dataset
