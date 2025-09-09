# fastapi-product-playground-learn — Products API (Learning Playground)

A small FastAPI playground for learning product/catalog APIs — demo routes for products, sellers and auth. This repository is explicitly a learning project; feel free to experiment, open issues, and submit small PRs.

This repository contains a small FastAPI project (Products API). The project includes a project-local virtual environment at `env/` — please install dependencies into that interpreter so the editor and runtime use the same Python environment.

## Prerequisites

- macOS / Linux or any POSIX shell
- Python 3.11+ (a system Python or Conda is fine)

## Create and use the project virtualenv (recommended)

From the project root (where `env/` and `requirements.txt` live):

```bash
# create a virtual environment if you don't have one
python -m venv env

# install dependencies explicitly into the env python (guaranteed target)
./env/bin/python -m pip install --upgrade pip setuptools wheel
./env/bin/python -m pip install -r requirements.txt
```

Why this exact command?

- Using `./env/bin/python -m pip` runs pip for that specific Python binary and installs packages into `env/`.
- Avoid running plain `pip install` unless you have activated the correct virtualenv first — plain `pip` can point to system or Conda Python and install packages into the wrong environment.

## Verify installation

```bash
./env/bin/python -V
./env/bin/python -m pip show passlib    # example package
./env/bin/python -m pip check           # detect dependency conflicts
```

## Run the application (use the env interpreter)

```bash
# run uvicorn using the env python so runtime and editor match
./env/bin/python -m uvicorn product.main:app --reload
```

## Pin dependencies

After you confirm everything works, freeze exact versions so others reproduce the same environment:

```bash
./env/bin/python -m pip freeze > requirements.txt
```

## VS Code tips

- Select the interpreter that points to `env/bin/python`: Cmd+Shift+P → "Python: Select Interpreter" → choose `/.../my_project/env/bin/python`.
- Then Cmd+Shift+P → "Python: Restart Language Server". If imports are still flagged, reload the window.

## Troubleshooting

- If `pip` installs to a different Python, always run `./env/bin/python -m pip install ...` or activate the env first:

```bash
source ./env/bin/activate
python -m pip install -r requirements.txt
deactivate
```

- If you see dependency conflicts after install, run:

```bash
./env/bin/python -m pip check
```

- For JWT/token verification problems, ensure the secret and encoding you paste into verification tools (jwt.io) exactly match how your app constructs the key (hex, base64 or plain text).

## Security notes

- Do not hard-code secrets (e.g., `SECRET_KEY`) in source for production. Use environment variables or a secrets manager.
- For database schema changes use migrations (Alembic) rather than `models.Base.metadata.create_all(...)` in production.

---

If you want, I can commit this README for you or add a short `CONTRIBUTING.md` with the same setup steps.
