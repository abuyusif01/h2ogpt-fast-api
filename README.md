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
      - [Installation - Docker](#installation---docker)
  - [Todo](#todo)

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

1. [Docker compose](https://docs.docker.com/engine/install/ubuntu/)
2. Docker [buildx](https://docs.docker.com/reference/cli/docker/buildx/)

#### Installation - Docker

Clone repo

```bash
# clone repo
git clone https://github.com/abuyusif01/h2ogpt-fast-api
```

Configure environmental variables for mongodb and h2oapi docker image

```sh
# Mongodb
MONGO_USER=root
MONGO_PASS=pass
MONGO_CHAT_DB=H2OGPT_CHATS
MONGO_ITEM_DB=H2OGPT_ITEMS
MONGO_PORT=27017
MONGO_HOST=localhost

# h2ogpt
H2OGPT_API_URL=http://localhost:7860
H2OGPT_API_KEY=test-api-keys-1234
H2OGPT_MAX_WORKERS=40
H2OGPT_AUTH_USER=test
H2OGPT_AUTH_PASS=test
H2OGPT_CHUNK_SIZE=512
H2OGPT_LANGCHAIN_MODE=UserData
H2OGPT_LANGCHAIN_ACTION=Query

# FastAPI
PROJECT_NAME=H2OGPT
DOMAIN=localhost
ENVIRONMENT=local
VERBOSE=3
RES_DIR=/tmp/h2ogpt
API_V1_PREFIX=/api/v1
BACKEND_CORS_ORIGINS=http://localhost,https://localhost
```

Build docker image, and start app

```sh
docker compose up --remove-orphans --build -d
```

Next, go to your browser by visiting http://127.0.0.1:8000/docs or http://localhost:8000/docs (Swagger UI)

## Todo

1. Support streaming
2. Periodically delete pasted content in user_paste. [gh-issue](https://github.com/h2oai/h2ogpt/issues/1565)
3. Github pytest workflow
4. Allow users to supply h2ogpt_key
