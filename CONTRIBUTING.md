# Contributing

This repository (`fastapi-product-playground-learn`) is a learning playground. Contributions are welcome — small PRs, suggestions, and issue reports that help others learn are especially appreciated.

## Setup (quick)

From the project root (where `env/` and `requirements.txt` live):

```bash
# create or reuse the bundled virtual environment
python -m venv env

# install dependencies into the env python (guaranteed target)
./env/bin/python -m pip install --upgrade pip setuptools wheel
./env/bin/python -m pip install -r requirements.txt
```

## Run

```bash
# run uvicorn using the env python so runtime and editor match
./env/bin/python -m uvicorn product.main:app --reload
```

## Code style

- Keep changes small and focused
- Add tests for any new logic where possible
- Follow existing project structure (`product/routers`, `product/models`, `product/schemas`)

## Opening PRs

- Use a descriptive title and short description
- Link related issue if present
- For experimental/learning changes, mark them clearly in the PR body

## Notes

- This is not production code. Do not store secrets in the repo.
- If you add dependencies, update `requirements.txt` with pinned versions (`./env/bin/python -m pip freeze > requirements.txt`).
