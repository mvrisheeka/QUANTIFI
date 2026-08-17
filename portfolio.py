import streamlit as st
import pandas as pd
import yfinance as yf
import db_config
import plotly.express as px
import plotly.graph_objects as go
import quantum_optimizer
import numpy as np

def get_portfolio_data(user_id):
    conn = db_config.get_db_connection() 
    cursor = conn.cursor()
    
    cursor.execute("SELECT stock_symbol, quantity, avg_price FROM portfolio WHERE user_id = %s", (user_id,))
    data = cursor.fetchall()  
    cursor.close()
    conn.close()
    
    if data:
        return pd.DataFrame(data, columns=["Stock", "Quantity", "Avg. Price"])
    else:
        return pd.DataFrame(columns=["Stock", "Quantity", "Avg. Price"]) 

def fetch_stock_prices(stocks):
    prices = {}
    for stock in stocks:
        try:
            data = yf.Ticker(stock + ".BO").history(period="1d")
            if not data.empty:
                prices[stock] = data["Close"].iloc[-1]
        except Exception as e:
            print(f"Error fetching stock data for {stock}: {e}")
    return prices

def calculate_stock_metrics(stock_symbol, period="6mo"):
    try:
        hist = yf.Ticker(stock_symbol + ".BO").history(period=period)
        if hist.empty:
            return {"return": 0.05, "volatility": 0.15}
        
        returns = hist["Close"].pct_change().dropna()
        avg_return = returns.mean() * 252
        volatility = returns.std() * np.sqrt(252)
        
        return {
            "return": max(0.001, avg_return),
            "volatility": max(0.01, volatility)
        }
    except Exception as e:
        print(f"Error calculating metrics for {stock_symbol}: {e}")
        return {"return": 0.05, "volatility": 0.15}

def portfolio_analysis():
    st.markdown("<h1 style='text-align: center; color: white;'> Portfolio Analysis</h1>", unsafe_allow_html=True)
    user_id = st.session_state.get("user_id")  
    if not user_id:
        st.error(" Please log in to view your portfolio.") 
        return

    portfolio = get_portfolio_data(user_id)
    if portfolio.empty:
        st.warning(" Your portfolio is empty! Start investing to see insights.")  
        return
    
    stock_prices = fetch_stock_prices(portfolio["Stock"].tolist())
    portfolio["Latest Price"] = portfolio["Stock"].apply(lambda stock: stock_prices.get(stock, None))  
 
    portfolio["Investment Value"] = portfolio["Latest Price"] * portfolio["Quantity"]
    total_value = portfolio["Investment Value"].sum()

    if total_value == 0:
        st.error("Total investment value is zero, cannot compute allocation.") 
        return
    portfolio["Allocation (%)"] = (portfolio["Investment Value"] / total_value) * 100
    portfolio["Profit/Loss"] = (portfolio["Latest Price"] - portfolio["Avg. Price"]) * portfolio["Quantity"]

    def highlight_loss(val):
        return f"color: {'green' if val > 0 else 'red'}; font-weight: bold" 

    st.markdown(" Your Portfolio Summary")
    styled_df = portfolio.style.applymap(highlight_loss, subset=["Profit/Loss"]).format(
        {"Latest Price": "₹{:.2f}", "Avg. Price": "₹{:.2f}", "Investment Value": "₹{:.2f}", "Profit/Loss": "₹{:.2f}", "Allocation (%)": "{:.2f}%"})
    st.dataframe(styled_df)

    fig_pie = px.pie(
        portfolio, values="Investment Value", names="Stock",
        title="Portfolio Allocation", hole=0.4,
        color_discrete_sequence=px.colors.sequential.Blues
    )
    st.plotly_chart(fig_pie, use_container_width=True)  

    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        x=portfolio["Stock"],
        y=portfolio["Profit/Loss"],
        marker=dict(color=portfolio["Profit/Loss"].apply(lambda x: "green" if x > 0 else "red")),
        name="Profit/Loss"
    ))
    fig_bar.update_layout(
        title="Profit/Loss Per Stock", 
        xaxis_title="Stock", yaxis_title="Profit/Loss (₹)",
        template="plotly_dark"
    )
    st.plotly_chart(fig_bar, use_container_width=True)  

    st.markdown(" Cumulative Returns Over Time")
    fig_line = go.Figure()
    for stock in portfolio["Stock"]:
        stock_data = yf.Ticker(stock + ".BO").history(period="6mo")["Close"]
        stock_data = (stock_data / stock_data.iloc[0]) * 100 
        fig_line.add_trace(go.Scatter(x=stock_data.index, y=stock_data, mode="lines", name=stock))

    fig_line.update_layout(
        title="Cumulative Returns Over 6 Months",
        xaxis_title="Date",
        yaxis_title="Normalized Price",
        template="plotly_dark"
    )
    st.plotly_chart(fig_line, use_container_width=True) 

    st.markdown("Expected Returns & Risk")
    stock_returns = {stock: yf.Ticker(stock + ".BO").history(period="6mo")["Close"].pct_change().mean() for stock in portfolio["Stock"]}
    avg_return = sum(stock_returns.values()) / len(stock_returns) 
    avg_risk = sum(yf.Ticker(stock + ".BO").history(period="6mo")["Close"].pct_change().std() for stock in portfolio["Stock"]) / len(stock_returns)  

    st.write(f" *Expected Returns:* {avg_return * 100:.2f}%")  
    st.write(f" *Portfolio Risk (Volatility):* {avg_risk * 100:.2f}%")

    st.markdown("---")
    st.markdown("<h2 style='text-align: center; color: #00d4ff;'>🔬 Quantum Portfolio Optimizer (QAOA)</h2>", unsafe_allow_html=True)
    
    if st.button("⚛️ Optimize Portfolio with Quantum Algorithm", key="quantum_opt"):
        with st.spinner("Running quantum optimization on your portfolio..."):
            stocks_list = portfolio["Stock"].tolist()
            
            stocks_data = {}
            for stock in stocks_list:
                metrics = calculate_stock_metrics(stock)
                stocks_data[stock] = metrics

            # Use the new QAOA pipeline by default; it falls back to classical when necessary
            try:
                optimized_allocation = quantum_optimizer.qaoa_optimize(stocks_data, shots=1024, p=1, max_qubits=12)
            except Exception as e:
                st.error(f"Quantum optimization failed: {e}")
                optimized_allocation = quantum_optimizer.classical_optimization_fallback(stocks_data)

            report = quantum_optimizer.generate_optimization_report(
                optimized_allocation, stocks_data, portfolio
            )

            st.success("Quantum optimization complete!")
            st.text(report)

            opt_df = pd.DataFrame([
                {"Stock": stock, "Quantum Weight": f"{weight*100:.2f}%", "Current Weight": f"{portfolio[portfolio['Stock']==stock]['Allocation (%)'].values[0]:.2f}%"}
                for stock, weight in optimized_allocation.items() if weight > 0.001
            ])

            st.markdown("**Recommended vs Current Allocation:**")
            st.dataframe(opt_df)

            fig_comparison = go.Figure(data=[
                go.Bar(name='Current Allocation', x=list(optimized_allocation.keys()), 
                       y=[portfolio[portfolio['Stock']==s]['Allocation (%)'].values[0] if s in portfolio['Stock'].values else 0 for s in optimized_allocation.keys()]),
                go.Bar(name='Quantum Optimized', x=list(optimized_allocation.keys()), 
                       y=[optimized_allocation[s]*100 for s in optimized_allocation.keys()])
            ])
            fig_comparison.update_layout(
                title="Current vs Quantum-Optimized Allocation",
                barmode='group',
                template="plotly_dark",
                xaxis_title="Stock",
                yaxis_title="Allocation (%)"
            )
            st.plotly_chart(fig_comparison, use_container_width=True)
