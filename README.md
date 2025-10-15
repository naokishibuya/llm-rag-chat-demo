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
```

`ollama list` to verify the installation.

`sudo systemctl restart ollama` if running as a service, or `ollama restart` if running it manually.

## Run the Backend

Run the FastAPI server:

```bash
uvicorn main:app --reload
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
