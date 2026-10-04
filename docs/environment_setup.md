# Environment Setup (macOS)

## 1. Tools
| Tool | Version | Install |
|---|---|---|
| Homebrew | latest | https://brew.sh |
| Python | 3.12 | `brew install python@3.12` |
| PostgreSQL | 16 | **Option A** Docker Desktop + `docker-compose.yml` · **Option B** Postgres.app · **Option C** `brew install postgresql@16` |
| Node.js | LTS | `brew install nvm && nvm install --lts` |
| Git | latest | `xcode-select --install` |
| DB GUI | any | pgAdmin 4 or DBeaver |
| Editor | VS Code | Python, Jupyter, Ruff, SQLTools (+PostgreSQL driver), ESLint, Tailwind CSS IntelliSense |
| Power BI Desktop | latest | **Windows only**. Use a lab PC, a Windows VM (Parallels/UTM), or Power BI Service web (AGENTS.md §12) |

## 2. Python environment
```bash
cd "/Users/pranav/Project Folder/Adarzsh"
python3.12 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

### `requirements.txt` (starting point; pin exact versions with `pip freeze` after the first install)
```
# data / analysis
pandas>=2.2
numpy>=1.26
scipy>=1.13
statsmodels>=0.14
pyarrow>=16            # parquet
matplotlib>=3.8
seaborn>=0.13
jupyterlab>=4

# ML
scikit-learn>=1.6
joblib>=1.4
imbalanced-learn>=0.12  # optional SMOTE comparison
shap>=0.45              # optional per-patient explanations
# xgboost>=2.0          # optional

# database
sqlalchemy>=2.0
psycopg[binary]>=3.1
python-dotenv>=1.0

# API
fastapi>=0.115
uvicorn[standard]>=0.30
pydantic>=2.7
pydantic-settings>=2.3
python-multipart>=0.0.9  # CSV upload for /predict/batch

# quality
pytest>=8
httpx>=0.27
ruff>=0.5
```

### `pyproject.toml` (minimal)
```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "readmission"
version = "0.1.0"
requires-python = ">=3.12"

[tool.setuptools.packages.find]
where = ["src"]

[tool.ruff]
line-length = 100
```

## 3. PostgreSQL

### Option A — Docker (`docker-compose.yml`)
```yaml
services:
  db:
    image: postgres:16
    container_name: readmission-db
    environment:
      POSTGRES_USER: readmit
      POSTGRES_PASSWORD: readmit
      POSTGRES_DB: readmission_db
    ports: ["5432:5432"]
    volumes: ["pgdata:/var/lib/postgresql/data"]
volumes:
  pgdata:
```
`docker compose up -d` → `docker compose ps`

### Option B — Postgres.app
Start the server, then:
```bash
psql -c "CREATE ROLE readmit LOGIN PASSWORD 'readmit';"
psql -c "CREATE DATABASE readmission_db OWNER readmit;"
```

### `.env.example`
```
DATABASE_URL=postgresql+psycopg://readmit:readmit@localhost:5432/readmission_db
MODEL_DIR=models
API_CORS_ORIGINS=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## 4. Frontend (only once the design references arrive, task P7-06)
```bash
npx create-next-app@latest frontend --ts --tailwind --app --src-dir --eslint
cd frontend && npm install && npm install -D openapi-typescript
npx openapi-typescript http://localhost:8000/openapi.json -o src/lib/api-types.ts
```

## 5. Verify
```bash
python -c "import sklearn, pandas, fastapi; print(sklearn.__version__, pandas.__version__)"
psql "postgresql://readmit:readmit@localhost:5432/readmission_db" -c "select 1"
```
