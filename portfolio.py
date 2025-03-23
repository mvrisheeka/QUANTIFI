import streamlit as st
import pandas as pd
import yfinance as yf
import db_config
import plotly.express as px
import plotly.graph_objects as go

# ✅ Fetch portfolio data from the database
def get_portfolio_data(user_id):
    conn = db_config.get_db_connection()  # Connect to the database
    cursor = conn.cursor()
    
    # Execute SQL query to fetch user's portfolio data
    cursor.execute("SELECT stock_symbol, quantity, avg_price FROM portfolio WHERE user_id = %s", (user_id,))
    data = cursor.fetchall()  # This returns a list of tuples with stock symbol, quantity, and average price
    
    cursor.close()
    conn.close()
    
    # ✅ Fix: Convert to DataFrame only if data is not empty
    if data:
        return pd.DataFrame(data, columns=["Stock", "Quantity", "Avg. Price"])  # Convert to DataFrame
    else:
        return pd.DataFrame(columns=["Stock", "Quantity", "Avg. Price"])  # Return empty DataFrame if no data

# ✅ Fetch live stock prices from Yahoo Finance
def fetch_stock_prices(stocks):
    prices = {}
    for stock in stocks:
        try:
            # Fetch the latest price for each stock from Yahoo Finance (Indian market symbol .BO)
            data = yf.Ticker(stock + ".BO").history(period="1d")
            if not data.empty:
                prices[stock] = data["Close"].iloc[-1]  # Get the most recent closing price
        except Exception as e:
            print(f"Error fetching stock data for {stock}: {e}")
    return prices

# ✅ Portfolio Analysis Function
def portfolio_analysis():
    # Display header with a centered, white-colored text
    st.markdown("<h1 style='text-align: center; color: white;'>📊 Portfolio Analysis</h1>", unsafe_allow_html=True)

    # 🔐 Ensure the user is logged in
    user_id = st.session_state.get("user_id")  # Check if user_id is stored in session state
    if not user_id:
        st.error("🔐 Please log in to view your portfolio.")  # Show error if user is not logged in
        return

    # 📌 Fetch the portfolio data for the logged-in user
    portfolio = get_portfolio_data(user_id)
    if portfolio.empty:
        st.warning("📉 Your portfolio is empty! Start investing to see insights.")  # Show a warning if portfolio is empty
        return

    # 📌 Fetch the latest stock prices for all stocks in the portfolio
    stock_prices = fetch_stock_prices(portfolio["Stock"].tolist())
    portfolio["Latest Price"] = portfolio["Stock"].apply(lambda stock: stock_prices.get(stock, None))  # Add latest price to portfolio DataFrame

    # ✅ Compute the total investment value
    portfolio["Investment Value"] = portfolio["Latest Price"] * portfolio["Quantity"]
    total_value = portfolio["Investment Value"].sum()

    if total_value == 0:
        st.error("Total investment value is zero, cannot compute allocation.")  # Show error if total value is zero
        return

    # ✅ Compute portfolio allocation percentage for each stock
    portfolio["Allocation (%)"] = (portfolio["Investment Value"] / total_value) * 100

    # ✅ Compute profit or loss for each stock
    portfolio["Profit/Loss"] = (portfolio["Latest Price"] - portfolio["Avg. Price"]) * portfolio["Quantity"]

    # 🎨 Color code profit/loss for styling
    def highlight_loss(val):
        return f"color: {'green' if val > 0 else 'red'}; font-weight: bold"  # If positive profit, green; otherwise red

    # ✅ Display the portfolio summary table
    st.markdown("### 📜 Your Portfolio Summary")
    styled_df = portfolio.style.applymap(highlight_loss, subset=["Profit/Loss"]).format(
        {"Latest Price": "₹{:.2f}", "Avg. Price": "₹{:.2f}", "Investment Value": "₹{:.2f}", "Profit/Loss": "₹{:.2f}", "Allocation (%)": "{:.2f}%"})
    st.dataframe(styled_df)  # Display the styled DataFrame

    # ✅ Create a Pie Chart to show portfolio allocation
    fig_pie = px.pie(
        portfolio, values="Investment Value", names="Stock",
        title="Portfolio Allocation", hole=0.4,
        color_discrete_sequence=px.colors.sequential.Blues
    )
    st.plotly_chart(fig_pie, use_container_width=True)  # Display pie chart

    # ✅ Create a Bar Chart for Profit/Loss visualization
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
    st.plotly_chart(fig_bar, use_container_width=True)  # Display bar chart

    # ✅ Create a Line Chart to show cumulative returns for each stock
    st.markdown("### 📈 Cumulative Returns Over Time")
    fig_line = go.Figure()
    for stock in portfolio["Stock"]:
        stock_data = yf.Ticker(stock + ".BO").history(period="6mo")["Close"]
        stock_data = (stock_data / stock_data.iloc[0]) * 100  # Normalize prices to 100 for comparison
        fig_line.add_trace(go.Scatter(x=stock_data.index, y=stock_data, mode="lines", name=stock))

    fig_line.update_layout(
        title="Cumulative Returns Over 6 Months",
        xaxis_title="Date",
        yaxis_title="Normalized Price",
        template="plotly_dark"
    )
    st.plotly_chart(fig_line, use_container_width=True)  # Display line chart

    # ✅ Calculate and display Expected Returns and Risk (Volatility)
    st.markdown("### 📈 Expected Returns & Risk")
    stock_returns = {stock: yf.Ticker(stock + ".BO").history(period="6mo")["Close"].pct_change().mean() for stock in portfolio["Stock"]}
    avg_return = sum(stock_returns.values()) / len(stock_returns)  # Calculate average return
    avg_risk = sum(yf.Ticker(stock + ".BO").history(period="6mo")["Close"].pct_change().std() for stock in portfolio["Stock"]) / len(stock_returns)  # Calculate average risk

    st.write(f"📈 *Expected Returns:* {avg_return * 100:.2f}%")  # Display expected return
    st.write(f"⚠ *Portfolio Risk (Volatility):* {avg_risk * 100:.2f}%")  # Display portfolio risk
#portfolio code end
