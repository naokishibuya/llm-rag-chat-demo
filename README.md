# LLM Tests

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

## Run RAG demo

This is a simple demo of a Retrieval-Augmented Generation (RAG) system using the Mistral model from Ollama.

```bash
python src/rag_demo.py
```

