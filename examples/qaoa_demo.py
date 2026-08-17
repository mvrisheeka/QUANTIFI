# Minimal QAOA demo for QUANTIFI
from quantum_optimizer import qaoa_optimize

if __name__ == '__main__':
    stocks_data = {
        'A': {'return': 0.12, 'volatility': 0.20},
        'B': {'return': 0.08, 'volatility': 0.15},
        'C': {'return': 0.10, 'volatility': 0.18},
    }

    allocation = qaoa_optimize(stocks_data, shots=256, p=1, max_qubits=8)
    print('Allocation:', allocation)
