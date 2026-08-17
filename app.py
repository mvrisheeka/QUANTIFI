import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import db_config
import chatbot
import crypto
import portfolio
from db_config import get_db_connection
from decimal import Decimal

st.set_page_config(page_title="QUANTIFI", layout="wide")
st.title("Welcome to QUANTIFI")

def login_signup_page():
    st.title("Welcome to QUANTIFI")
    tab1, tab2 = st.tabs(["Login", "Signup"])
    
    with tab1:
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login"):
            user_id = db_config.verify_user(username, password)
            if user_id:
                st.session_state["logged_in"] = True
                st.session_state["user_id"] = user_id
                st.session_state["username"] = username
                st.success(f"Welcome back, {username}!")
            else:
                st.error("Invalid login credentials")
    
    with tab2:
        new_username = st.text_input("Username", key="signup_username")
        new_password = st.text_input("Password", type="password", key="signup_password")
        if st.button("Signup"):
            if new_username and new_password:
                result = db_config.add_user(new_username, new_password)
                st.success(result)
            else:
                st.warning("Please fill in all details.")

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    login_signup_page()
else:
    st.sidebar.write(f"Hello, {st.session_state['username']}!")
    if st.sidebar.button("Sign Out"):
        st.session_state["logged_in"] = False
        st.session_state.pop("user_id", None)
        st.session_state.pop("username", None)
        st.rerun()
    page = st.sidebar.radio("Menu", ["Trading", "Portfolio Analysis", "Quantum Optimizer", "SIP Investment", "AI Chatbot", "Crypto Prices"])

    if page == "Trading":
        st.title("QUANTIFI Trading")
        current_user_id = st.session_state.get("user_id")

        if current_user_id:
            symbol = st.text_input("Enter BSE Stock Symbol (e.g., RELIANCE, TCS)", value="RELIANCE").upper()
            symbol_bse = symbol + ".BO"
            stock_info = yf.Ticker(symbol_bse)
            stock_price = stock_info.history(period="1d")
            latest_price = Decimal(str(stock_price["Close"].iloc[-1])) if not stock_price.empty else None

            if latest_price:
                st.metric(f"{symbol} Latest Price", f"₹{latest_price:.2f}")

            st.subheader(f"{symbol} Candlestick Chart")
            stock_data = stock_info.history(period="1mo", interval="1d")
            if not stock_data.empty:
                fig = go.Figure(data=[go.Candlestick(
                    x=stock_data.index,
                    open=stock_data['Open'],
                    high=stock_data['High'],
                    low=stock_data['Low'],
                    close=stock_data['Close']
                )])
                fig.update_layout(title=f"{symbol} - Candlestick Chart", xaxis_title="Date", yaxis_title="Price (₹)")
                st.plotly_chart(fig)
            else:
                st.error("No stock data available.")

            st.subheader("Buy & Sell Stocks")
            col1, col2, col3 = st.columns(3)
            quantity = col1.number_input("Number of Shares", min_value=1, step=1, value=10)
            time_period = col2.selectbox("Time Period", ["Intraday", "Short-Term", "Long-Term"])
            total_price = quantity * latest_price if latest_price else 0
            col3.metric("Total Price", f"₹{total_price:.2f}")

            col1, col2 = st.columns(2)
            conn = get_db_connection()
            cursor = conn.cursor()

            if col1.button("Buy"):
                cursor.execute("SELECT quantity, avg_price FROM portfolio WHERE user_id=%s AND stock_symbol=%s", 
                               (current_user_id, symbol))
                existing_stock = cursor.fetchone()

                if existing_stock:
                    old_quantity, old_avg_price = existing_stock
                    old_quantity = int(old_quantity or 0)
                    old_avg_price = Decimal(str(old_avg_price or 0))
                    new_quantity = old_quantity + quantity
                    new_avg_price = ((old_quantity * old_avg_price) + (quantity * latest_price)) / new_quantity
                    cursor.execute("UPDATE portfolio SET quantity=%s, avg_price=%s WHERE user_id=%s AND stock_symbol=%s",
                                   (new_quantity, new_avg_price, current_user_id, symbol))
                else:
                    cursor.execute("INSERT INTO portfolio (user_id, stock_symbol, quantity, avg_price) VALUES (%s, %s, %s, %s)", 
                                   (current_user_id, symbol, int(quantity), latest_price))

                conn.commit()
                st.success(f"Bought {quantity} shares of {symbol} at ₹{latest_price:.2f} each.")

            if col2.button("Sell"):
                cursor.execute("SELECT quantity FROM portfolio WHERE user_id=%s AND stock_symbol=%s", 
                               (current_user_id, symbol))
                stock_data = cursor.fetchone()

                if stock_data and stock_data[0] >= quantity:
                    new_quantity = stock_data[0] - quantity
                    if new_quantity > 0:
                        cursor.execute("UPDATE portfolio SET quantity=%s WHERE user_id=%s AND stock_symbol=%s",
                                       (new_quantity, current_user_id, symbol))
                    else:
                        cursor.execute("DELETE FROM portfolio WHERE user_id=%s AND stock_symbol=%s",
                                       (current_user_id, symbol))
                    conn.commit()
                    st.warning(f"Sold {quantity} shares of {symbol} at ₹{latest_price:.2f} each.")
                else:
                    st.error("You don't have enough shares to sell.")

            conn.close()
        else:
            st.error("User not authenticated. Please log in.")

    elif page == "Portfolio Analysis":
        portfolio.portfolio_analysis()

    elif page == "Quantum Optimizer":
        st.markdown("<h1 style='text-align: center; color: #00d4ff;'>Quantum Portfolio Optimizer</h1>", unsafe_allow_html=True)
        st.markdown("---")
        current_user_id = st.session_state.get("user_id")
        
        if current_user_id:
            st.markdown("""
            ### About Quantum Portfolio Optimization
            
            This feature uses Quantum Approximate Optimization Algorithm (QAOA) powered by Qiskit 
            to find optimal portfolio allocations. The quantum algorithm:
            
            - Analyzes multiple stocks in your portfolio simultaneously
            - Considers risk-return tradeoffs at quantum level
            - Provides recommendations based on quantum-computed probability distributions
            - Handles up to 8+ stocks efficiently using quantum superposition
            
            **How it works:**
            1. Your current portfolio is analyzed
            2. Risk and return metrics are calculated for each stock
            3. Quantum circuits are constructed with QAOA ansatz
            4. Qiskit simulator runs the quantum optimization
            5. Results are compared with your current allocation
            """)
            
            st.markdown("---")
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT stock_symbol, quantity, avg_price FROM portfolio WHERE user_id=%s", (current_user_id,))
            portfolio_data = cursor.fetchall()
            conn.close()
            
            if portfolio_data:
                portfolio_df = pd.DataFrame(portfolio_data, columns=["Stock", "Quantity", "Avg Price"])
                st.subheader("Your Current Portfolio:")
                st.dataframe(portfolio_df)
                st.markdown("---")
                st.info("Click the button below to run quantum optimization on your portfolio")
                
                if st.button("Launch Quantum Portfolio Optimizer", key="launch_qaoa"):
                    with st.spinner("Running quantum simulation..."):
                        portfolio.portfolio_analysis()
            else:
                st.warning("Your portfolio is empty! Add stocks first to use the quantum optimizer.")
        else:
            st.error("User not authenticated. Please log in.")

    elif page == "SIP Investment":
        st.title("Systematic Investment Plan (SIP)")
        current_user_id = st.session_state.get("user_id")
        if current_user_id:
            symbol = st.text_input("Enter Stock Symbol for SIP (e.g., RELIANCE, TCS)", value="RELIANCE").upper()
            sip_amount = st.number_input("Monthly Investment Amount (₹)", min_value=100, step=100, value=1000)
            duration = st.slider("Investment Duration (Months)", min_value=6, max_value=60, value=12)

            if st.button("Start SIP"):
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("INSERT INTO sip (user_id, stock_symbol, sip_amount, duration) VALUES (%s, %s, %s, %s)", 
                               (current_user_id, symbol, sip_amount, duration))
                conn.commit()
                conn.close()
                st.success(f"SIP started for {symbol} with ₹{sip_amount} per month for {duration} months.")
        else:
            st.error("User not authenticated. Please log in.")
      
    elif page == "AI Chatbot":  
        chatbot.chatbot_ui()  

    elif page == "Crypto Prices":
        crypto.crypto_ui()
