import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import db_config
import chatbot
import crypto
from db_config import get_db_connection

# -------------------------
# Streamlit Page Configuration
# -------------------------
st.set_page_config(page_title="QUANTIFI", layout="wide")
st.title("Welcome to QUANTIFI")

# -------------------------
# Login/Signup Section
# -------------------------
def login_signup_page():
    """
    Display the login and signup interface using Streamlit tabs.
    """
    st.title("🔐 Welcome to QUANTIFI")
    tab1, tab2 = st.tabs(["Login", "Signup"])
    
    # -------------------------
    # Login Tab
    # -------------------------
    with tab1:
        username = st.text_input("👤 Username", key="login_username")
        password = st.text_input("🔑 Password", type="password", key="login_password")
        if st.button("🚀 Login"):
            # Verify login credentials using db_config
            user_id = db_config.verify_user(username, password)
            if user_id:
                # Save user data in session state
                st.session_state["logged_in"] = True
                st.session_state["user_id"] = user_id
                st.session_state["username"] = username
                st.success(f"Welcome back, {username}! ✅")
            else:
                st.error("Invalid login credentials ❌")
    
    # -------------------------
    # Signup Tab
    # -------------------------
    with tab2:
        new_username = st.text_input("👤 Username", key="signup_username")
        new_password = st.text_input("🔑 Password", type="password", key="signup_password")
        if st.button("📝 Signup"):
            if new_username and new_password:
                result = db_config.add_user(new_username, new_password)
                st.success(result)
            else:
                st.warning("Please fill in all details.")

# -------------------------
# Main App Section
# -------------------------
# Initialize session state for login status
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# Display login/signup page if user is not logged in
if not st.session_state["logged_in"]:
    login_signup_page()

else:
    # Sidebar with user info and navigation menu
    st.sidebar.write(f"👋 Hello, {st.session_state['username']}!")
    page = st.sidebar.radio("📌 Menu", ["Trading", "Portfolio Analysis", "SIP Investment", "AI Chatbot", "Crypto Prices"])

    # -------------------------
    # Trading Section
    # -------------------------
    if page == "Trading":
        st.title("📈 QUANTIFI - Trading Platform")
        current_user_id = st.session_state.get("user_id")

        if current_user_id:
            # Get the stock symbol from user input
            symbol = st.text_input("Enter BSE Stock Symbol (e.g., RELIANCE, TCS)", value="RELIANCE").upper()

            # Append ".BO" to symbol for BSE market data
            symbol_bse = symbol + ".BO"
            stock_info = yf.Ticker(symbol_bse)
            stock_price = stock_info.history(period="1d")
            latest_price = stock_price["Close"].iloc[-1] if not stock_price.empty else None

            # Display current stock price
            if latest_price:
                st.metric(f"📊 {symbol} Latest Price", f"₹{latest_price:.2f}")

            # Display stock candlestick chart
            st.subheader(f"📊 {symbol} Candlestick Chart")
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
                st.error("📉 No stock data available.")

            # -------------------------
            # Buy and Sell Section
            # -------------------------
            st.subheader("💰 Buy & Sell Stocks")
            col1, col2, col3 = st.columns(3)

            # Get user input for number of shares, time period, and total price
            quantity = col1.number_input("📦 Number of Shares", min_value=1, step=1, value=10)
            time_period = col2.selectbox("⏳ Time Period", ["Intraday", "Short-Term", "Long-Term"])
            total_price = quantity * latest_price if latest_price else 0
            col3.metric("💰 Total Price", f"₹{total_price:.2f}")

            # Database connection for transactions
            conn = get_db_connection()
            cursor = conn.cursor()

            # Buy action
            if col1.button("🛒 Buy"):
                cursor.execute("SELECT quantity, avg_price FROM portfolio WHERE user_id=%s AND stock_symbol=%s", 
                               (current_user_id, symbol))
                existing_stock = cursor.fetchone()

                if existing_stock:
                    old_quantity, old_avg_price = existing_stock
                    new_quantity = old_quantity + quantity
                    new_avg_price = ((old_quantity * old_avg_price) + (quantity * latest_price)) / new_quantity
                    cursor.execute("UPDATE portfolio SET quantity=%s, avg_price=%s WHERE user_id=%s AND stock_symbol=%s",
                                   (new_quantity, new_avg_price, current_user_id, symbol))
                else:
                    cursor.execute("INSERT INTO portfolio (user_id, stock_symbol, quantity, avg_price) VALUES (%s, %s, %s, %s)", 
                                   (current_user_id, symbol, int(quantity), float(latest_price)))
                conn.commit()
                st.success(f"✅ Bought {quantity} shares of {symbol} at ₹{latest_price:.2f} each.")

            # Sell action
            if col2.button("📉 Sell"):
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
                    st.warning(f"❌ Sold {quantity} shares of {symbol} at ₹{latest_price:.2f} each.")
                else:
                    st.error("⚠ You don't have enough shares to sell.")
            conn.close()

        else:
            st.error("❌ User not authenticated. Please log in.")

    # -------------------------
    # Portfolio Analysis Section
    # -------------------------
    elif page == "Portfolio Analysis":
        st.title("📊 Portfolio Analysis")
        current_user_id = st.session_state.get("user_id")

        if current_user_id:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT stock_symbol, quantity, avg_price FROM portfolio WHERE user_id=%s", (current_user_id,))
            portfolio_data = cursor.fetchall()
            conn.close()

            if portfolio_data:
                portfolio_df = pd.DataFrame(portfolio_data, columns=["Stock Symbol", "Quantity", "Avg Price"])
                st.dataframe(portfolio_df)
            else:
                st.warning("📉 Your portfolio is empty!")
        else:
            st.error("❌ User not authenticated. Please log in.")

    # -------------------------
    # AI Chatbot Section
    # -------------------------
    elif page == "AI Chatbot":
        chatbot.chatbot_ui()

    # -------------------------
    # Cryptocurrency Prices Section
    # -------------------------
    elif page == "Crypto Prices":
        crypto.crypto_ui()