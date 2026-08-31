# 🛒 Agentic E-Commerce Assistant

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=flat&logo=postgresql)
![LangChain](https://img.shields.io/badge/LangGraph-1C3C3C?style=flat)
![MCP](https://img.shields.io/badge/Model_Context_Protocol-purple?style=flat)

A virtual e-commerce assistant powered by a state-of-the-art multi-agent architecture. This project demonstrates how to orchestrate multiple LLMs (Large Language Models) in a production environment, solving complex problems such as *Agent Chaining*, *Recency Bias*, and context loss.

## Key Features

- **Multi-Agent Architecture (LangGraph):** Isolated specialized agents (`Supervisor`, `Sales`, `Payment`, `Support`) ensuring accuracy and separation of concerns.
- **Decoupled Tool Integration (MCP):** Uses the *Model Context Protocol* (via FastMCP) to isolate database logic from the agents' reasoning.
- **Persistent & Stateful Memory:** Leverages `AsyncPostgresSaver` to save the graph state (Checkpointer) and conversation history directly into PostgreSQL.
- **Guardrails Engineering:** Deterministic control flows implemented in Python to prevent infinite loops and LLM hallucinations.
- **Anti-Hallucination Protocol (Echo Trick):** Advanced prompt engineering techniques used to inject context into the agent's short-term memory, ensuring accurate argument parsing during tool calls.
- **Real-Time Streaming (SSE):** A FastAPI backend that streams the agents' "thought process" and messages simultaneously to an elegant Streamlit UI.

## System Architecture

The project adopts an AI-oriented microservices architecture:

1. **Database:** PostgreSQL via Docker (stores both store data and LangGraph checkpoints).
2. **MCP Server:** A FastMCP server exposing database functions as callable tools for the AI.
3. **Backend API:** FastAPI orchestrating LangGraph, injecting dependencies, and serving *Server-Sent Events* (SSE).
4. **Frontend UI:** Streamlit consuming the API, rendering the AI's thought process, and managing multiple chat sessions.

## Project Structure

```text
agentic-ai-studies/
├── src/
│   ├── agents/            # Prompts and logic for agents (Sales, Support, Payment, Supervisor)
│   ├── api/               # FastAPI Backend
│   │   ├── v1/endpoints/  # API Routes (e.g., SSE Chat Stream)
│   │   └── db.py          # DB Connections for the UI sessions
│   ├── core/              # Global configurations (Pydantic Settings)
│   ├── graph/             # StateGraph definition (LangGraph workflow)
│   └── mcp_servers/       # Database tools wrapped in the Model Context Protocol
├── ui/
│   ├── app.py             # Main Streamlit application
│   ├── api_client.py      # HTTPX client to consume the FastAPI endpoints
│   └── components/        # Isolated UI components (Sidebar, Thought process)
├── main.py                # Entrypoint to start Uvicorn/FastAPI
├── docker-compose.yml     # PostgreSQL orchestration
└── requirements.txt       # Project dependencies
```

## How to Run
Prerequisites
Docker and Docker Compose

Python 3.10+

An API Key for an LLM model (e.g., NVIDIA NIM, Groq, OpenAI) configured in the .env file.

1. Spin up the Database
```
docker compose up -d --build
```

2. Start the MCP Server (Tools)
In a new terminal, start the server that bridges the AI and the database:

```
python -m src.mcp_servers.store_db_mcp_server
```

3. Start the Backend API (FastAPI)
In another terminal, start the LangGraph orchestrator:
```
python main.py
```

4. Start the User Interface (Streamlit)
In a final terminal, launch the UI:

```Bash
cd ui
streamlit run app.py
```

## Demo Flow
To test the system's capabilities, try the following flow in the chat:

"I want to buy a Slim Jeans size 42. My CPF is 111.222.333-00."

The system will detect that you are not registered. Thanks to the persistent memory, it will retain your purchase intent and CPF.

Reply with your name and phone number. The system will autonomously register you, check the stock, and create the order.

"I want to pay for my order via PIX."

The Supervisor will semantically route the context to the Financial Agent, which will fetch the pending order from memory and process the transaction.

## Technologies Used
**LangGraph:** Multi-agent orchestration and state management.

**FastAPI:** Asynchronous backend and SSE streaming.

**Streamlit:** Frontend UI.

**Model Context Protocol (FastMCP):** Tool calling standardization.

**PostgreSQL + psycopg3:** Relational database and asynchronous checkpointer.