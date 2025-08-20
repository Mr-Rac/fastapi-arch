# fastapi-arch

A scalable and clean FastAPI-based services.

### Init venv

```shell
  uv venv
  source .venv/bin/activate
```

### Install requirements.txt

```shell
  uv add -r requirements.txt
  uv sync
```

### Start Server

```shell
  uv run python main.py
```

### Export requirements.txt

```shell
  uv export --no-hashes --no-header --no-annotate --no-dev --format requirements.txt > requirements.txt
```
