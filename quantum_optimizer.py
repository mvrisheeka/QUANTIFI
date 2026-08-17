import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_algorithms import QAOA, NumPyMinimizer
from qiskit_algorithms.optimizers import COBYLA
from qiskit_aer import AerSimulator
from qiskit_ibm_runtime import QiskitRuntimeService
import pandas as pd
from decimal import Decimal

def normalize_portfolio_weights(allocation):
    total = sum(allocation.values())
    if total == 0:
        return {k: 0 for k in allocation}
    return {k: v / total for k, v in allocation.items()}

def quantum_portfolio_optimization(stocks_data):
    num_stocks = len(stocks_data)
    
    if num_stocks == 0:
        return {}
    
    if num_stocks == 1:
        stock = list(stocks_data.keys())[0]
        return {stock: 1.0}
    
    expected_returns = np.array([stocks_data[s]["return"] for s in stocks_data.keys()])
    volatilities = np.array([stocks_data[s]["volatility"] for s in stocks_data.keys()])
    
    if num_stocks <= 3:
        return classical_optimization_fallback(stocks_data)
    
    qreg = QuantumRegister(num_stocks)
    creg = ClassicalRegister(num_stocks)
    qc = QuantumCircuit(qreg, creg)
    
    for i in range(num_stocks):
        qc.h(qreg[i])
    
    depth = 3
    for layer in range(depth):
        for i in range(num_stocks):
            angle = np.pi * expected_returns[i] / (np.max(expected_returns) + 1e-8)
            qc.rz(angle, qreg[i])
        
        for i in range(num_stocks - 1):
            qc.cx(qreg[i], qreg[i + 1])
    
    qc.measure(qreg, creg)
    
    simulator = AerSimulator()
    job = simulator.run(qc, shots=1024)
    result = job.result()
    counts = result.get_counts(qc)
    
    allocation = {stock: 0.0 for stock in stocks_data.keys()}
    total_counts = sum(counts.values())
    
    for bitstring, count in counts.items():
        for i, bit in enumerate(reversed(bitstring)):
            if bit == '1':
                stock = list(stocks_data.keys())[i]
                allocation[stock] += count / total_counts
    
    allocation = normalize_portfolio_weights(allocation)
    
    return allocation

def classical_optimization_fallback(stocks_data):
    expected_returns = np.array([stocks_data[s]["return"] for s in stocks_data.keys()])
    volatilities = np.array([stocks_data[s]["volatility"] for s in stocks_data.keys()])
    
    risk_adjusted_returns = expected_returns / (volatilities + 1e-8)
    
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

def generate_optimization_report(allocation, stocks_data, portfolio_df):
    report = []
    report.append("=" * 60)
    report.append("QUANTUM-OPTIMIZED PORTFOLIO ALLOCATION")
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
