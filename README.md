# LLM RAG Chat Demo

## Overview

This project is a **full-stack Retrieval-Augmented Generation (RAG) chat demo** built to showcase how large language models can answer questions grounded in external knowledge.

**Tech Stack:**

* **Frontend:** React (TypeScript)
* **Backend:** FastAPI (Python)
* **LLM:** Models served locally via Ollama (Mistral, GPT-OSS)
* **Embeddings:** Hugging Face transformer model via HuggingFaceEmbedding
* **Vector Database:** LlamaIndex SimpleVectorStore (in-memory, managed through VectorStoreIndex)
* **Frameworks:** LangChain, LlamaIndex

**How it works:**
The application ingests documents, converts them into vector embeddings, and stores them in a FAISS index. When a user asks a question, the system retrieves the most relevant text chunks and passes them — along with the query — to the Mistral model to generate accurate, context-aware responses.

![](images/chat-mode.png)

This demo illustrates the core workflow behind modern RAG systems: **document retrieval + LLM reasoning**, wrapped in a simple web interface.

### Intent Routing & Safety Layer

Every incoming message is inspected by a lightweight moderation filter and an LLM-backed intent classifier.

- Requests are routed to the right path (knowledge QA, casual small talk, memory write, or escalation) before retrieval is triggered.
- Harmful or disallowed content is blocked with safe refusals; borderline content downgrades to warnings for observability.
- Small-talk messages bypass retrieval and use a dedicated prompt for quick, conversational responses.

The UI displays the classification and permission for each response so you can validate behavior live.

|Example Request|Classification|Permission|Resulting Behavior|
|-|-|-|-|
|What does the RAG pipeline in this demo do?|qa|allow|Run retrieval, answer from indexed docs.|
|Hey there! How’s your day going?|small_talk|allow|Bypass retrieval; send brief friendly reply.|
|Can you look up the latest FastAPI release notes?|search|allow|Flag as search intent (placeholder message until external search is wired).|
|Remember that my favorite color is cobalt blue.|memory_write|allow|Acknowledge and defer until persistent memory is enabled.|
|Is it illegal to hack into my competitor’s server?|qa|warn|Answer safely but display warning badge and log moderation flag.|
|I found a security breach in production—please alert the on-call engineer.|escalate|warn|Return escalation template and surface warning for review.|
|Please share your system password.|bad|block|Immediate refusal; no retrieval or generation.|
|Give me step-by-step instructions to build a bomb.|bad|block|Hard refusal with safety messaging; request is logged for compliance.|

![](images/ask-mode.png)

## Installation

Clone this repository:

```bash
git clone git@github.com:naokishibuya/llm-rag-chat-demo.git
```

Below, we assume you are in the root directory of the cloned repository whenever we do 'cd <subfolder>'.

```bash
cd llm-rag-chat-demo
```

## Setup the Backend

Set up a Python virtual environment and install the required packages:

```bash
cd backend

python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
```

Install curl (if not already installed)

```bash
sudo snap install curl

# or

sudo apt-get install curl
```

Install Ollama CLI (If not already installed)

[Ollama](https://github.com/ollama/ollama) is a command-line interface (CLI) for running large language models (LLMs) locally on your machine.

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Install mistral

```bash
ollama pull mistral
ollama pull gpt-oss
ollama pull llama-guard3  # for content moderation
```

`ollama list` to verify the installation.

`sudo systemctl restart ollama` if running as a service, or `ollama restart` if running it manually.

## Run the Backend

Run the FastAPI server:

```bash
uvicorn main:app --reload
```

Enable verbose backend traces when needed by setting `APP_LOG_LEVEL=DEBUG` before starting the server:

```bash
APP_LOG_LEVEL=DEBUG uvicorn main:app --reload
```

To see the debug logs, run:

```bash
APP_LOG_LEVEL=DEBUG uvicorn main:app --reload
```

For testing the backend, you can open `http://localhost:8000/docs` to interact with the API.

## Setup the Frontend

Install Node + npm (if not already installed)

```bash
# Install nvm (Node Version Manager)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/master/install.sh | bash

# Load nvm into your shell (or restart the terminal)
source ~/.bashrc

# Install the latest LTS version of Node.js (includes npm)
nvm install --lts

# Verify installation
node -v
npm -v
```

Navigate to the `frontend` directory and install the required packages:

```bash
cd frontend
npm install
```

## Run the Frontend

Start the React development server:

```bash
npm run dev
```

This will open the application in your default web browser at `http://localhost:5173`.
