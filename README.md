# Enterprise AI Platform

A production-oriented AI workspace for securely managing documents, searching knowledge, and interacting with document-aware AI.

The platform combines a FastAPI backend with a modern React frontend and provides authentication, document management, semantic search, RAG-based conversations, chat history, and an extensible AI architecture.

---

## ✨ Features

- 🔐 Secure user authentication
- 📄 Document upload and management
- 🧠 AI-powered document understanding
- 🔎 Semantic document search
- 💬 RAG-based AI conversations
- 📝 Persistent chat history
- 👤 User-specific workspace isolation
- 🗂️ Document metadata and processing
- 🧩 Modular backend architecture
- ⚡ Modern React frontend
- 🧪 Backend unit and integration tests
- 🐳 Docker-ready backend
- 🗄️ PostgreSQL + Alembic database migrations
- 🔌 Extensible AI/agent architecture

---

## 🏗️ Architecture

```text
                         ┌──────────────────────┐
                         │      React UI        │
                         │      Frontend        │
                         └──────────┬───────────┘
                                    │
                                    │ HTTP / REST
                                    ▼
                         ┌──────────────────────┐
                         │       FastAPI        │
                         │       Backend        │
                         └──────────┬───────────┘
                                    │
                 ┌──────────────────┼──────────────────┐
                 │                  │                  │
                 ▼                  ▼                  ▼
          ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
          │ PostgreSQL  │    │ Vector Store│    │     AI      │
          │   Database  │    │  / Embeddings│   │   Services  │
          └─────────────┘    └─────────────┘    └─────────────┘
                                    │                  │
                                    └────────┬─────────┘
                                             ▼
                                      ┌─────────────┐
                                      │     RAG     │
                                      │   Pipeline  │
                                      └─────────────┘