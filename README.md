# AI Financial Coach Agent

Secure, investor-ready MVP for personalized financial coaching using LangGraph multi-agent orchestration, tabular RAG over canonical Pandas data, Ozero-style fine-grained authorization, Hugging Face reasoning, Llama Guard moderation, and a Streamlit dashboard.

## What is included

- Multi-agent workflow built with LangGraph
- File ingestion pipeline using PyPDF2, Pandas, and LangChain loaders
- Schema-aware tabular RAG with minimal authorized row injection
- Deterministic debt, savings, and budget calculations in Python
- Streamlit dashboard with metrics, charts, tables, action plan, and audit trail
- Architecture, prompts, FGA model, and n8n workflow documentation

## Repository structure

- [app.py](/C:/Users/iNNOVATEQ/Documents/New%20project/app.py)
- [run_webhooks.py](/C:/Users/iNNOVATEQ/Documents/New%20project/run_webhooks.py)
- [src/financial_coach](/C:/Users/iNNOVATEQ/Documents/New%20project/src/financial_coach)
- [docs/architecture.md](/C:/Users/iNNOVATEQ/Documents/New%20project/docs/architecture.md)
- [docs/n8n.md](/C:/Users/iNNOVATEQ/Documents/New%20project/docs/n8n.md)
- [docs/prompts.md](/C:/Users/iNNOVATEQ/Documents/New%20project/docs/prompts.md)
- [data/sample](/C:/Users/iNNOVATEQ/Documents/New%20project/data/sample)
- [workflows](/C:/Users/iNNOVATEQ/Documents/New%20project/workflows)

## Run locally

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

### Run webhook endpoints

```powershell
.venv\Scripts\Activate.ps1
python run_webhooks.py
```

### Run with Docker Compose

```powershell
docker compose up --build
```

## Demo flow

1. Launch Streamlit.
2. Keep the default `demo-user-001` user or enter another scoped user id.
3. Run the workflow with built-in sample data or upload `income.csv`, `expenses.csv`, `debts.csv`, and `assets.csv`.
4. Review the action plan, budget opportunities, authorized tables, and audit trail.

## Security model

- Every canonical row carries `user_id` and `scope`.
- Table and row checks are executed before retrieval, calculations, and explanation.
- Unauthorized rows are removed before LangGraph agents receive context.
- The narrative explanation is moderated before display/export.

## Implementation notes

- The MVP uses a lightweight Ozero FGA adapter and Hugging Face reasoning facade so the architecture is production-aligned while remaining runnable locally.
- `yfinance` enriches the plan with market context and falls back safely when live data is unavailable.
- The explanation layer is intentionally separated from the calculator layer to keep math deterministic and auditable.
- `n8n` workflows can call the webhook server for ingestion, analysis, audit reads, and notification callbacks.

## Delivery checklist mapping

- Architecture: [docs/architecture.md](/C:/Users/iNNOVATEQ/Documents/New%20project/docs/architecture.md)
- Prompts: [docs/prompts.md](/C:/Users/iNNOVATEQ/Documents/New%20project/docs/prompts.md)
- Dashboard implementation: [app.py](/C:/Users/iNNOVATEQ/Documents/New%20project/app.py)
- Agent graph: [graph.py](/C:/Users/iNNOVATEQ/Documents/New%20project/src/financial_coach/graph.py)
- Authorization model: [auth.py](/C:/Users/iNNOVATEQ/Documents/New%20project/src/financial_coach/auth.py)
