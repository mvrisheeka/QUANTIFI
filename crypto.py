import streamlit as st
import requests
import pandas as pd

def crypto_ui():
    st.title("💰 Live Cryptocurrency Prices")
    api_key = st.secrets["COINMARKETCAP_API_KEY"]
    
    if api_key:
        url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
        headers = {"X-CMC_PRO_API_KEY": api_key}
        params = {"convert": "USD", "limit": 20}  # Fetch top 20 cryptos
        
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            crypto_data = []
            for crypto in data["data"]:
                symbol = crypto["symbol"]
                name = crypto["name"]
                price = crypto["quote"]["USD"]["price"]
                market_cap = crypto["quote"]["USD"]["market_cap"]
                percent_change_24h = crypto["quote"]["USD"]["percent_change_24h"]
                
                crypto_data.append([symbol, name, f"${price:,.2f}", f"${market_cap:,.2f}", f"{percent_change_24h:.2f}%"])
            
            df = pd.DataFrame(crypto_data, columns=["Symbol", "Name", "Price (USD)", "Market Cap", "24h Change (%)"])
            st.dataframe(df)
        else:
            st.error("⚠️ Failed to fetch cryptocurrency data. Please try again later.")
    else:
        st.error("⚠️ Missing API Key. Set COINMARKETCAP_API_KEY in secrets.toml.")