# Nexus RAG MCP Server 🧠

<div align="center">

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![MCP](https://img.shields.io/badge/MCP-Compatible-green.svg)
![Test](https://img.shields.io/badge/tests-79%2F79%20passing-brightgreen.svg)

**The "Second Brain" for your AI Assistant.**

[Configuration](#configuration) • [Usage](#usage) • [Tools](#available-tools) • [Troubleshooting](#troubleshooting)

</div>

---

## 🚀 Overview

**Nexus** is a local **Model Context Protocol (MCP)** server that gives your AI agents (like Claude Desktop, Cursor, etc.) **Long-Term Memory** and **RAG (Retrieval-Augmented Generation)** capabilities. 

It runs on your local machine, indexes your files, and allows your AI to:
1.  **Recall** past conversations and decisions.
2.  **Search** your local codebase and notes.
3.  **Learn** your preferences over time.

---

## ⚙️ Configuration (Zero-Setup)

You don't need to manually install Nexus. Just use `uvx` to run it directly from the repository.

### 1. Claude Desktop App
To use Nexus with Claude, add the following to your config file:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "nexus": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/kaushikkumarkr/RAG-MCP",
        "nexus",
        "serve"
      ]
    }
  }
}
```

> **Note**: This requires [uv](https://docs.astral.sh/uv/) to be installed.
> Nexus will automatically initialize its database at `~/.nexus` on the first run.

### 2. Cursor / Windsurf / Other IDEs
Go to **Settings > Features > MCP** and add a new server:
- **Name**: `nexus`
- **Type**: `stdio`
- **Command**: `uvx --from git+https://github.com/kaushikkumarkr/RAG-MCP nexus serve`

---

## 💬 Usage Examples

Once connected, you can talk to your AI naturally. Nexus will automatically trigger the right tools.

### 🧠 Memory (Long-Term Storage)
> **User**: "Remember that for the 'Financial Dashboard' project, we depend on the `pandas` 2.0 library and use `pytest` for testing."
>
> **AI**: "Understood. I've saved that context for the Financial Dashboard project."
> *(Tool used: `remember`)*

---

### 🔍 Retrieval (RAG)
> **User**: "How do we handle authentication in this codebase?"
>
> **AI**: "According to `docs/auth_flow.md`, we use JWT tokens via Auth0..."
> *(Tool used: `search_knowledge`)*

---

### ⚡ Context Injection
> **User**: "I'm starting work on the backend API. Get me up to speed."
>
> **AI**: "Checking project context... Okay, for the backend API:
> 1. We use FastAPI.
> 2. The DB is Postgres.
> 3. **Warning**: Migration scripts are in `/alembic`."
> *(Tool used: `get_project_context`)*

---

## 🛠️ Available Tools

| Tool | Description | Arguments |
| :--- | :--- | :--- |
| `search_knowledge` | **Search** your local documents. | `query` (str), `limit` (int) |
| `remember` | **Store** a fact or memory. | `content` (str), `project` (str), `tags` (list) |
| `recall` | **Retrieve** memories. | `query` (str) |
| `get_project_context` | Get **full overview** of a project. | `project` (str) |
| `get_user_preferences` | Get learned **user habits**. | None |
| `ingest_content` | **Save** content from other MCPs. | `content` (str), `source` (str) |
| `add_note` | Create a markdown **note**. | `filename` (str), `content` (str) |
| `list_sources` | List indexed **files**. | None |

---

## 🛡️ Citations & Grounding

Nexus citations are **precise**. Every answer includes:
1.  **Source Path**: File path (`/docs/api.md`).
2.  **Relevance**: Confidence score (0-1).
3.  **Quote**: Exact text chunk used.

---

## ❓ Troubleshooting

### Server not starting?
Run the built-in status check to verify your database and config:
```bash
nexus status
```

### "Tool not found" error?
Ensure you have restarted your client (Claude/Cursor) after editing the config file.

### How do I see what's happening?
Nexus logs to stderr. In Claude Desktop, you can open the **Developer Console** to see the MCP logs in real-time.

---

## 🏗️ System Architecture

Nexus uses a **Dual-Layer Cognitive Architecture** that separates fast retrieval from deep understanding.

```mermaid
graph TB
    %% ==========================================
    %% 🎨 Styles & Theme
    %% ==========================================
    classDef client fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,rx:10,ry:10,color:#0d47a1
    classDef protocol fill:#fff8e1,stroke:#ff8f00,stroke-width:2px,stroke-dasharray: 5 5,color:#ff6f00
    classDef core fill:#fff3e0,stroke:#e65100,stroke-width:4px,color:#bf360c
    classDef engine fill:#ffffff,stroke:#e65100,stroke-width:2px,color:#e65100
    classDef storage fill:#f3e5f5,stroke:#4a148c,stroke-width:2px,rx:5,ry:5,color:#4a148c
    classDef external fill:#f1f8e9,stroke:#33691e,stroke-width:2px,stroke-dasharray: 5 5,color:#33691e

    %% ==========================================
    %% 🖥️ Layer 1: Client Ecosystem
    %% ==========================================
    subgraph Clients ["🖥️ Client Integration Layer"]
        direction LR
        Claude(["🤖 Claude Desktop"]) ::: client
        Cursor(["⚡ Cursor / IDE"]) ::: client
        Terminal(["💻 CLI Terminal"]) ::: client
    end

    %% ==========================================
    %% 🔌 Layer 2: Protocol & Orchestration
    %% ==========================================
    JSONRPC(("&nbsp;sockets/stdio&nbsp;<br/>JSON-RPC 2.0")) ::: protocol

    subgraph Orchestration ["🌐 Multi-MCP Orchestration"]
        direction TB
        Github(["GitHub MCP"]) ::: external
        Notion(["Notion MCP"]) ::: external
        Slack(["Slack MCP"]) ::: external
    end

    %% ==========================================
    %% 🔥 Layer 3: Nexus Core System
    %% ==========================================
    subgraph Nexus ["🔥 NEXUS SERVER (Local Process)"]
        direction TB

        Router{"🚦 Tool Router"} ::: core

        %% --- Sub-System: Cognitive Memory ---
        subgraph MemorySys ["🧠 Cognitive Engine"]
            direction TB
            MemStore["📝 Memory Store"] ::: engine
            ContextMgr["🏗️ Context Manager"] ::: engine
            UserPrefs["👤 Preference Engine"] ::: engine
        end

        %% --- Sub-System: Retrieval (RAG) ---
        subgraph RAGSys ["🔍 RAG & Search Engine"]
            direction TB
            Hybrid["🔎 Hybrid Search<br/>(Dense + Sparse)"] ::: engine
            Rerank["⚖️ Cross-Encoder<br/>Reranker"] ::: engine
            QueryExp["✨ Query Expansion"] ::: engine
            
            Hybrid --> Rerank
        end

        %% --- Sub-System: Data Operations ---
        subgraph DataOps ["⚡ Data Operations Pipeline"]
            direction TB
            Watcher["👀 File Watcher<br/>(Watchdog)"] ::: engine
            Chunker["✂️ Semantic Chunker"] ::: engine
            Embedder["🧠 Local Embedder<br/>(FastEmbed/SentenceTransformers)"] ::: engine
            
            Watcher --> Chunker --> Embedder
        end
    end

    %% ==========================================
    %% 💾 Layer 4: Persistence Layer
    %% ==========================================
    subgraph Storage ["💾 Local Persistence (~/.nexus)"]
        direction LR
        VectorDB[("🧱 Qdrant<br/>(Vector Store)")] ::: storage
        SQLite[("🗃️ SQLite<br/>(Metadata & Logs)")] ::: storage
        Config["⚙️ YAML Config"] ::: storage
    end

    %% ==========================================
    %% 🔗 Connections & Data Flow
    %% ==========================================
    
    %% Client -> Nexus
    Clients <==> JSONRPC <==> Router

    %% External MCP -> Nexus (Content Injection)
    Orchestration -.->|"ingest_content"| Router

    %% Router Dispatch
    Router -->|"remember / recall"| MemorySys
    Router -->|"search_knowledge"| RAGSys
    Router -->|"add_note / ingest"| DataOps

    %% Memory Persistence
    MemStore <--> SQLite
    ContextMgr <--> SQLite
    UserPrefs <--> SQLite

    %% RAG Flow
    RAGSys -->|"Vector Search"| VectorDB
    RAGSys -->|"Metadata Filter"| SQLite

    %% Ingestion Flow
    Embedder -->|"Upsert Vectors"| VectorDB
    Embedder -->|"Store Metadata"| SQLite

    %% Feedback Loop
    Rerank -->|"Top-K Results"| Router
```

**Built with:** Python 3.11 • Qdrant • Sentence-Transformers • RAGAS
