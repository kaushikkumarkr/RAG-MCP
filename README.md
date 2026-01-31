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
    %% 🎨 Styles
    %% ==========================================
    classDef client fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#0d47a1
    classDef core fill:#fff3e0,stroke:#e65100,stroke-width:3px,color:#bf360c
    classDef engine fill:#ffffff,stroke:#e65100,stroke-width:2px,color:#e65100
    classDef storage fill:#f3e5f5,stroke:#4a148c,stroke-width:2px,color:#4a148c
    classDef external fill:#f1f8e9,stroke:#33691e,stroke-width:2px,stroke-dasharray: 5 5,color:#33691e

    %% ==========================================
    %%  Layer 1: User & Clients
    %% ==========================================
    subgraph ClientLayer ["🖥️ Client Environment"]
        direction TB
        Claude(["🤖 Claude Desktop"]) ::: client
        Cursor(["⚡ Cursor / IDE"]) ::: client
    end

    %% ==========================================
    %%  Layer 2: Nexus Core
    %% ==========================================
    subgraph Nexus ["🔥 NEXUS SERVER"]
        direction TB
        
        Router{"🚦 MCP ROUTER"} ::: core

        subgraph Memory ["🧠 Memory Engine"]
            MemStore["📝 Fact Store"] ::: engine
            Context["🏗️ Context Manager"] ::: engine
            Preferences["👤 User Prefs"] ::: engine
        end

        subgraph RAG ["🔍 RAG Engine"]
            Hybrid["🔎 Hybrid Search"] ::: engine
            Rerank["⚖️ Cross-Encoder"] ::: engine
        end

        subgraph Ingest ["⚡ Data Pipeline"]
            Watcher["👀 File Watcher"] ::: engine
            Chunker["✂️ Semantic Chunker"] ::: engine
            Embedder["🧠 Local Embedder"] ::: engine
        end
    end

    %% ==========================================
    %%  Layer 3: Storage
    %% ==========================================
    subgraph StorageLayer ["💾 Persistence (~/.nexus)"]
        direction TB
        VectorDB[("🧱 Qdrant (Vectors)")] ::: storage
        SQLite[("🗃️ SQLite (Metadata)")] ::: storage
    end

    %% ==========================================
    %%  Layer 4: External
    %% ==========================================
    subgraph External ["🌐 External MCPs"]
        Github["GitHub MCP"] ::: external
        Notion["Notion MCP"] ::: external
    end

    %% ==========================================
    %%  FLOWS & MAPPINGS (The "Everything")
    %% ==========================================
    
    %% 1. Connection
    Claude <==> Router
    Cursor <==> Router

    %% 2. Tool Routing (The "Everything")
    Router -- "remember / recall / forget" --> MemStore
    Router -- "get_project_context" --> Context
    Router -- "get_user_preferences" --> Preferences
    
    Router -- "search_knowledge / list_sources" --> Hybrid
    Router -- "get_stats" --> SQLite
    
    Router -- "add_note / ingest_content" --> Embedder
    
    %% 3. Internal Logistics
    Hybrid --> Rerank
    Watcher --> Chunker --> Embedder

    %% 4. Persistence
    MemStore <--> SQLite
    Context <--> SQLite
    Preferences <--> SQLite
    
    Hybrid <--> VectorDB
    Embedder --> VectorDB
    Embedder --> SQLite

    %% 5. Orchestration (Content Injection)
    Github -.-> Router
    Notion -.-> Router
```

**Built with:** Python 3.11 • Qdrant • Sentence-Transformers • RAGAS
