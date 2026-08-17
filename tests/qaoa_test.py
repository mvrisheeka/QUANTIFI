import unittest
from quantum_optimizer import qaoa_optimize

class TestQAOAOptimize(unittest.TestCase):
    def test_small_portfolio(self):
        stocks_data = {
            'A': {'return': 0.12, 'volatility': 0.20},
            'B': {'return': 0.08, 'volatility': 0.15},
            'C': {'return': 0.10, 'volatility': 0.18},
        }
        alloc = qaoa_optimize(stocks_data, shots=128, p=1, max_qubits=8)
        # allocation should sum to ~1 (allow small numeric slack)
        total = sum(alloc.values())
        self.assertAlmostEqual(total, 1.0, places=3)
        self.assertSetEqual(set(alloc.keys()), set(stocks_data.keys()))

if __name__ == '__main__':
    unittest.main()
