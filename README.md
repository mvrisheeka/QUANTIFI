# QUANTIFI: AI-Powered Stock Analysis System

## Overview
QUANTIFI is an AI-driven stock analysis platform that enables users to track stock market trends, analyze portfolios, and make informed investment decisions. The system integrates real-time stock market data, quantum-powered portfolio optimization, and AI-assisted financial guidance.

## Features
- **User Authentication**: Secure login and signup system.
- **Stock Trading**: Buy and sell stocks with real-time price updates.
- **Portfolio Analysis**: View and manage stock holdings with detailed analytics.
- **Quantum Portfolio Optimizer**: Uses Quantum Approximate Optimization Algorithm (QAOA) on Qiskit to find optimal asset allocation.
- **SIP Investment**: Systematic investment planning with scheduled stock purchases.
- **AI Chatbot**: AI-powered assistant to answer financial queries.
- **Cryptocurrency Tracking**: Live cryptocurrency price updates.

## Technologies Used
- **Frontend**: Streamlit (Python-based UI framework)
- **Backend**: Python with Qiskit (Quantum Computing Framework)
- **Database**: MySQL (for user and stock data management)
- **APIs**: Yahoo Finance (for stock data)
- **Quantum Computing**: 
  - Qiskit 0.43.2 (Quantum circuit framework)
  - Qiskit-Aer 0.13.1 (Quantum simulator)
  - Qiskit-IBM-Runtime 0.15.0 (Runtime services)

## Quantum Portfolio Optimizer
The application features a cutting-edge **QAOA-based portfolio optimizer** that:
- Constructs quantum circuits with parameterized gates
- Optimizes portfolio weights using quantum superposition
- Analyzes risk-return tradeoffs at quantum level
- Provides recommendations for up to 8+ stocks
- Compares quantum-optimized allocation with current holdings
- Calculates Sharpe ratios and volatility metrics

### How QAOA Works in QUANTIFI
1. **Quantum State Preparation**: Initializes quantum superposition of all portfolio combinations
2. **Problem Encoding**: Encodes stock returns and volatility into rotation angles
3. **Quantum Ansatz**: Applies QAOA ansatz with configurable depth
4. **Measurement**: Samples from quantum probability distribution
5. **Classical Post-Processing**: Normalizes results and calculates performance metrics

## Installation & Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/mvrisheeka/QUANTIFI.git
   cd QUANTIFI
   ```
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up the database (MySQL):
   - Create a database and configure `db_config.py`
   - Run the SQL scripts to initialize tables
4. Start the application:
   ```bash
   streamlit run app.py
   ```

## Usage
- Launch the app and log in or sign up.
- Navigate through the sidebar menu to access:
  - **Trading**: Buy and sell stocks with real-time pricing
  - **Portfolio Analysis**: View holdings with profit/loss tracking
  - **Quantum Optimizer**: Run QAOA to get optimized asset allocation
  - **SIP Investments**: Set up systematic investment plans
  - **AI Chatbot**: Get financial advice from AI assistant
  - **Crypto Prices**: Track cryptocurrency markets

## Quantum Optimization Example
After adding stocks to your portfolio, use the Quantum Optimizer to:
1. Calculate historical returns and volatility for each stock
2. Feed data into Qiskit quantum circuits
3. Run QAOA optimization on quantum simulator
4. Receive recommendations for optimal rebalancing
5. Compare with current allocation visually

## Project Structure
```
QUANTIFI/
├── app.py                 # Main Streamlit application
├── quantum_optimizer.py   # QAOA-based portfolio optimization
├── portfolio.py           # Portfolio analysis and visualization
├── trading.py             # Trading logic and utilities
├── chatbot.py             # AI chatbot interface
├── crypto.py              # Cryptocurrency tracking
├── db_config.py           # Database configuration
├── requirements.txt       # Python dependencies
└── trading_platform.sql   # Database schema
```

## Dependencies
- streamlit
- yfinance
- pandas
- plotly
- requests
- mysql-connector-python
- python-dotenv
- qiskit==0.43.2
- qiskit-aer==0.13.1
- qiskit-ibm-runtime==0.15.0
- numpy
- scipy

## Contributors
- **Vrisheeka Mulakala, Nanda Gopal, Gunda Rama Praneetha, Piyali Choudhury, Sree Chetana, Ameya Bhosekar, Sriram, Ankit Kumar Sahu, Agam Bhatia, Shrey Jha**

## License
This project is licensed under the MIT License.

## Performance Notes
- Quantum optimizer works best with 3-8 stocks
- For single or two stocks, classical optimization fallback is used
- Qiskit simulator runs locally with 1024 shots per optimization
- Results are cached for improved performance during repeated optimizations

## Future Enhancements
- Integration with IBM Quantum Hardware
- Multi-objective optimization with constraints
- Real-time portfolio rebalancing alerts
- Enhanced quantum circuit architectures (VQE, etc.)
- Machine learning-enhanced classical optimization fallback
