# LLM RAG Chat Demo

A full-stack demo of Retrieval-Augmented Generation (RAG) chat powered by LlamaIndex, LangChain, FastAPI, and React.

This project demonstrates how to build a chatbot that retrieves relevant document context from a vector database and generates coherent answers using an LLM.

## Installation

[1] Clone this repository:

```bash
git clone git@github.com:naokishibuya/llm-tests.git
```

[2] Set up a Python virtual environment and install the required packages:

```bash
cd llm-tests

python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
```

[3] Install curl if not already installed

```bash
sudo snap install curl

# or

sudo apt-get install curl
```

[4] Install Ollama CLI

[Ollama](https://github.com/ollama/ollama) is a command-line interface (CLI) for running large language models (LLMs) locally on your machine.

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Install mistral

```bash
ollama pull mistral
```

[5] Install Node + npm

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
```

## Run the Backend

Run the FastAPI server:

```bash
cd backend
uvicorn main:app --reload
```

Then, open your web browser and navigate to `http://localhost:8000/docs` to interact with the API.


## Run the Frontend

Navigate to the `frontend` directory and install the required packages:

```bash
cd frontend
npm install
```

Then, start the React development server:

```bash
npm start
```

This will open the application in your default web browser at `http://localhost:3000`.
