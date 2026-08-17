# QUANTIFI: AI-Powered Stock Analysis & Quantum Portfolio Optimizer

QUANTIFI is a Streamlit-based interactive application that helps users track stocks, manage portfolios, run portfolio analysis, and experiment with a demonstrative quantum portfolio optimizer (QAOA) implemented with Qiskit. It is intended as a research/demo platform for combining classical financial analytics with quantum-inspired optimization techniques.

## Features

- Trading interface (buy/sell) backed by a simple MySQL portfolio store
- Portfolio analysis and visualizations (allocation pie, profit/loss bar, cumulative returns)
- Quantum Portfolio Optimizer (QAOA) implemented with Qiskit / qiskit-optimization and a classical fallback
- SIP (Systematic Investment Plan) tracking
- Basic AI chatbot and cryptocurrency price viewer
- Example SQL schema to bootstrap the database (trading_platform.sql)

## Stack

- Language: Python 3.9+ (tested)
- Framework / runtime: Streamlit (web UI)
- Notable libraries: yfinance (market data), plotly (visualizations), qiskit / qiskit-optimization (quantum optimizer), mysql-connector-python (DB)

## Repository layout

Top-level files and directories of interest:

```
app.py                 # Streamlit app entry point (UI + navigation)
portfolio.py           # Portfolio analysis views and helpers
quantum_optimizer.py   # QAOA implementation and classical fallback
trading.py             # Trading helpers (buy/sell) using yfinance and DB
db_config.py           # MySQL connection and user management utilities
trading_platform.sql   # SQL schema / example data for initializing DB
requirements.txt       # Python dependencies
examples/              # Example usage / data (if present)
tests/                 # Tests (if any)
.devcontainer/         # Devcontainer config
README.md              # This file
```

How it fits together: app.py is the Streamlit entry point and imports the domain modules (portfolio, trading, quantum_optimizer, chatbot, crypto). Portfolio and trading modules use db_config to persist user and portfolio state in MySQL. The quantum optimizer reads stock metrics computed in portfolio.py and runs QAOA (or a classical fallback) via qiskit-optimization.

## Quick start — run locally

1. Clone the repository

```bash
git clone https://github.com/mvrisheeka/QUANTIFI.git
cd QUANTIFI
```

2. Create a virtual environment and install dependencies

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

3. Database setup

This project uses a MySQL-compatible database. Create a database and run the provided SQL schema to create the tables:

```bash
# using mysql CLI or any client
mysql -u root -p
CREATE DATABASE trading_platform;
USE trading_platform;
SOURCE trading_platform.sql;
```

Note: trading_platform.sql includes example CREATE TABLE statements (users, portfolio, sip, etc.). Adjust names and types to match your MySQL server and user privileges.

4. Environment variables

Create a `.env` file in the project root (the project uses python-dotenv) with at least the database connection settings:

```
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_NAME=trading_platform
```

Optional (for Qiskit runtime / IBM hardware):

```
IBMQ_API_TOKEN=your_ibm_token
```

5. Run the app

```bash
streamlit run app.py
```

Open http://localhost:8501 in your browser (Streamlit will print the URL).

## Running the Quantum Optimizer

- The quantum optimizer is implemented in `quantum_optimizer.py`. It uses qiskit and qiskit-optimization when available. By default the app runs a local Aer simulator.
- For real IBM backend/runtime execution you must configure your IBMQ credentials and install `qiskit-ibm-runtime` and follow Qiskit's authentication steps. When Qiskit is not available or the problem exceeds the allowed qubit limit, the code falls back to a classical heuristic.

## Notes & limitations

- Market data is fetched from Yahoo Finance (yfinance) and the app assumes BSE tickers suffixed with `.BO` (e.g., `RELIANCE.BO`). Confirm ticker naming for your desired exchanges.
- The trading flow in this demo is simplified and does not implement order validation, cash balances, or concurrency protections for production use.
- Secrets (DB passwords, API tokens) must never be committed to the repository. Keep them in `.env` or a secrets manager.

## Development

- There's a `.devcontainer` directory for contributing with a reproducible development container.
- Tests (if any) live in the `tests/` directory.

## Contributing

Contributions, bug reports and pull requests are welcome. If you open a PR, please include a short description of the change and any setup steps to reproduce.

## License

No license specified in this repository. Add a LICENSE file if you want to make the project open-source.

## Further reading / next steps

- Improve authentication and session management (password hashing, password reset)
- Add cash balance / transaction history and order matching
- Extend quantum optimizer to support more sophisticated risk models and portfolio constraints
