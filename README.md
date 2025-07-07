# LLM RAG Chat Demo

A full-stack demo of Retrieval-Augmented Generation (RAG) chat powered by LlamaIndex, LangChain, FastAPI, and React.

This project demonstrates how to build a chatbot that retrieves relevant document context from a vector database and generates coherent answers using an LLM.

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
```

## Run the Backend

Run the FastAPI server:

```bash
uvicorn main:app --reload
```

Then, open your web browser and navigate to `http://localhost:8000/docs` to interact with the API.

## Setup the Frontend

Install Node + npm (if not already installed)

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
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

This will open the application in your default web browser at `http://localhost:3000`.
