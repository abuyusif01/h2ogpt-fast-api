# RestAPI For Local Inference (H2ogpt)

Extend H2ogpt Gradio-API to RestFul FastAPI.

## Table of Contents

- [RestAPI For Local Inference (H2ogpt)](#restapi-for-local-inference-h2ogpt)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [How to use it](#how-to-use-it)
    - [H2ogpt for Local Inference (Limited document Q/A capability)](#h2ogpt-for-local-inference-limited-document-qa-capability)
    - [H2ogpt RestFul API](#h2ogpt-restful-api)
      - [Requirements](#requirements)
      - [Installation](#installation)

## Features

1. Chat with on disk files (there's an endpoint to upload docs, and retrieve whats being uploaded, so u can select which doc to ingest)
2. Chat with user created pipelines (via mongodb pipelines)
3. Chat with Urls
4. Chat with Publications, We use OpenDoaj API and SciHub to download the papers
5. Local inference using llamaCpp

## How to use it

### H2ogpt for Local Inference (Limited document Q/A capability)

Create a fresh Python 3.10 environment and run the following:

Need this for llama-cpp-python to build

```bash
CMAKE_ARGS="-DLLAMA_BLAS=ON -DLLAMA_BLAS_VENDOR=OpenBLAS"
```

clone [h2ogpt](https://github.com/h2oai/h2ogpt.git) repo and install dependencies

```bash
git clone https://github.com/h2oai/h2ogpt.git
cd h2ogpt

pip install -r requirements.txt
pip install -r reqs_optional/requirements_optional_langchain.txt

pip uninstall llama_cpp_python llama_cpp_python_cuda -y
pip install -r reqs_optional/requirements_optional_llamacpp_gpt4all.txt --no-cache-dir

pip install -r reqs_optional/requirements_optional_langchain.urls.txt
pip install -r reqs_optional/requirements_optional_langchain.gpllike.txt
```

Run H2ogpt with user auth, and API auth enabled

```sh
python generate.py --base_model=TheBloke/Mistral-7B-Instruct-v0.2-GGUF \
--user_path=/tmp/h2ogpt \
--langchain_mode=UserData \
--langchain_modes="['UserData', 'LLM']" \
--prompt_type=mistral \
--auth_access=closed \
--auth="[('test', 'test')]" \
--h2ogpt_api_keys="['test-api-keys-1234']" \
--max_seq_len=4096
```

Next, go to your browser by visiting http://127.0.0.1:7860 or http://localhost:7860. Login with `test:test`

### H2ogpt RestFul API

#### Requirements

1. Docker compose
2. Docker [buildx](https://docs.docker.com/reference/cli/docker/buildx/)
3. poetry

#### Installation

Create and source a fresh Python 3.12 environment then run the following:

```bash
# clone repo
git clone https://github.com/abuyusif01/h2ogpt-fast-api
cd h2ogpt-fast-api/app

# install poetry and write lock file
pip install poetry
poetry install --no-root

# run compose
docker compose up --build
```

Next, go to your browser by visiting http://127.0.0.1:8000/docs
