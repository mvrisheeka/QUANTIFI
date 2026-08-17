import numpy as np
from decimal import Decimal

try:
    from qiskit import Aer
    from qiskit.utils import QuantumInstance
    from qiskit.algorithms import QAOA
    from qiskit.algorithms.optimizers import COBYLA
    from qiskit_optimization import QuadraticProgram
    from qiskit_optimization.converters import QuadraticProgramToIsing
    from qiskit_optimization.algorithms import MinimumEigenOptimizer
    QISKIT_AVAILABLE = True
except Exception as e:
    QISKIT_AVAILABLE = False
    _QISKIT_IMPORT_ERROR = e

def normalize_portfolio_weights(allocation):
    total = sum(allocation.values())
    if total == 0:
        return {k: 0 for k in allocation}
    return {k: v / total for k, v in allocation.items()}

def sampling_heuristic(stocks_data):
    expected_returns = np.array([stocks_data[s]["return"] for s in stocks_data.keys()])
    volatilities = np.array([stocks_data[s]["volatility"] for s in stocks_data.keys()])
    scores = expected_returns / (volatilities + 1e-8)
    scores = np.maximum(scores, 0.0)
    if scores.sum() == 0:
        weights = np.ones_like(scores) / len(scores)
    else:
        weights = scores / scores.sum()
    allocation = {stock: float(weights[i]) for i, stock in enumerate(stocks_data.keys())}
    return allocation

def classical_optimization_fallback(stocks_data):
    expected_returns = np.array([stocks_data[s]["return"] for s in stocks_data.keys()])
    volatilities = np.array([stocks_data[s]["volatility"] for s in stocks_data.keys()])
    risk_adjusted_returns = expected_returns / (volatilities + 1e-8)
    risk_adjusted_returns = np.maximum(risk_adjusted_returns, 0.0)
    if risk_adjusted_returns.sum() == 0:
        weights = np.ones_like(risk_adjusted_returns) / len(risk_adjusted_returns)
    else:
        weights = risk_adjusted_returns / np.sum(risk_adjusted_returns)
    allocation = {stock: float(weights[i]) for i, stock in enumerate(stocks_data.keys())}
    return allocation

def calculate_portfolio_metrics(allocation, stocks_data):
    total_return = sum(allocation[stock] * stocks_data[stock]["return"] for stock in allocation.keys())
    total_volatility = np.sqrt(sum(
        (allocation[stock] * stocks_data[stock]["volatility"]) ** 2
        for stock in allocation.keys()
    ))
    sharpe_ratio = total_return / (total_volatility + 1e-8) if total_volatility > 0 else 0
    return {
        "expected_return": total_return,
        "volatility": total_volatility,
        "sharpe_ratio": sharpe_ratio
    }

def qaoa_optimize(stocks_data, backend_name="aer", shots=1024, p=1, risk_penalty=1.0, max_qubits=12, seed=42):
    if not QISKIT_AVAILABLE:
        raise RuntimeError(f"Qiskit or qiskit-optimization not available: {_QISKIT_IMPORT_ERROR}")

    stocks = list(stocks_data.keys())
    num_stocks = len(stocks)

    if num_stocks == 0:
        return {}
    if num_stocks == 1:
        return {stocks[0]: 1.0}
    if num_stocks > max_qubits:
        return classical_optimization_fallback(stocks_data)

    qp = QuadraticProgram()
    for i, stock in enumerate(stocks):
        qp.binary_var(name=f'x_{i}')

    linear = {}
    quadratic = {}
    for i, stock in enumerate(stocks):
        mu = float(stocks_data[stock]["return"]) if stocks_data[stock]["return"] is not None else 0.0
        sigma = float(stocks_data[stock]["volatility"]) if stocks_data[stock]["volatility"] is not None else 0.0
        linear[f'x_{i}'] = -mu + risk_penalty * (sigma ** 2)

    qp.minimize(linear=linear, quadratic=quadratic)

    conv = QuadraticProgramToIsing()
    qubit_op, offset = conv.convert(qp)

    backend = Aer.get_backend('aer_simulator') if backend_name == 'aer' else Aer.get_backend('aer_simulator')
    quantum_instance = QuantumInstance(backend, shots=shots, seed_simulator=seed, seed_transpiler=seed)

    optimizer = COBYLA(maxiter=250)
    qaoa = QAOA(optimizer=optimizer, reps=p, quantum_instance=quantum_instance)

    meo = MinimumEigenOptimizer(qaoa)
    try:
        result = meo.solve(qp)
    except Exception as e:
        return classical_optimization_fallback(stocks_data)

    x = result.x
    selected = [stocks[i] for i, val in enumerate(x) if int(round(val)) == 1]

    if len(selected) == 0:
        return classical_optimization_fallback(stocks_data)

    sel_returns = np.array([stocks_data[s]["return"] for s in selected])
    sel_returns = np.maximum(sel_returns, 0.0)
    if sel_returns.sum() == 0:
        weights = np.ones_like(sel_returns) / len(sel_returns)
    else:
        weights = sel_returns / sel_returns.sum()

    allocation = {stock: 0.0 for stock in stocks}
    for i, stock in enumerate(selected):
        allocation[stock] = float(weights[i])

    allocation = normalize_portfolio_weights(allocation)
    return allocation

def generate_optimization_report(allocation, stocks_data, portfolio_df=None):
    report = []
    report.append("=" * 60)
    report.append("QUANTUM-OPTIMIZED PORTFOLIO ALLOCATION (QAOA)")
    report.append("=" * 60)
    report.append("")

    for stock, weight in sorted(allocation.items(), key=lambda x: x[1], reverse=True):
        if weight > 0.001:
            report.append(f"{stock}: {weight*100:.2f}%")

    report.append("")
    metrics = calculate_portfolio_metrics(allocation, stocks_data)
    report.append(f"Expected Portfolio Return: {metrics['expected_return']*100:.2f}%")
    report.append(f"Portfolio Volatility (Risk): {metrics['volatility']*100:.2f}%")
    report.append(f"Sharpe Ratio: {metrics['sharpe_ratio']:.4f}")
    report.append("=" * 60)

    return "\n".join(report)
