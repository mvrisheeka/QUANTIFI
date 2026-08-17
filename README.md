# QUANTIFI: AI-Powered Stock Analysis System

## Overview
QUANTIFI is an AI-driven stock analysis platform that enables users to track stock market trends, analyze portfolios, and make informed investment decisions. The system integrates real-time stock market data, portfolio analytics, an AI chatbot, and a demonstrative quantum optimization pipeline using Qiskit.

... (rest of README unchanged) ...

## Quantum Portfolio Optimizer
The application includes a demonstrative QAOA pipeline implemented with Qiskit and qiskit-optimization. Important notes:

- The QAOA pipeline provided in the repository constructs a small QUBO/Ising problem and uses QAOA (via qiskit.algorithms and qiskit_optimization) to solve a binary-selection version of the portfolio optimization problem.
- By default the optimizer runs on AerSimulator (local simulation). Running on real IBM hardware or Qiskit Runtime requires IBM credentials and additional configuration.
- The earlier "sampling" heuristic was renamed to `sampling_heuristic` for clarity; the QAOA pipeline is the new default when the quantum optimizer button is used. For large portfolios the code will fall back to a classical heuristic to avoid impractical simulation costs.

(See quantum_optimizer.py for implementation details and limitations.)
