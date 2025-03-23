import yfinance as yf  # Import yfinance for fetching stock data
from db_config import get_db_connection  # Import database connection function
import time  # Import time module for retries
from decimal import Decimal  # Import Decimal for precise calculations

# ✅ Get live stock price with retries
def get_stock_price(symbol, retries=3):
    """
    Fetches the latest stock price from Yahoo Finance with retry mechanism.

    Args:
        symbol (str): Stock ticker symbol.
        retries (int): Number of retries in case of failure.

    Returns:
        float: Latest stock closing price or None if retrieval fails.
    """
    full_symbol = symbol.upper() + ".BO"  # Append ".BO" for BSE stocks
    for attempt in range(retries):
        try:
            stock = yf.Ticker(full_symbol)
            data = stock.history(period="1d")  # Fetch daily historical data
            if not data.empty:
                return float(data["Close"].iloc[-1])  # Return last closing price
        except Exception as e:
            print(f"Error fetching stock price ({attempt+1}/{retries}): {e}")
            time.sleep(1)  # Wait before retrying
    return None  # Return None if all attempts fail

# ✅ Get stock quantity from portfolio
def get_stock_quantity(user_id, symbol):
    """
    Fetches the quantity of a specific stock owned by a user.

    Args:
        user_id (int): User ID.
        symbol (str): Stock ticker symbol.

    Returns:
        int: Quantity of stock owned (0 if none).
    """
    try:
        conn = get_db_connection()  # Get database connection
        cursor = conn.cursor()
        full_symbol = symbol.upper() + ".BO"  # Convert symbol to BSE format
        
        # Query to get the total quantity of the stock owned by the user
        cursor.execute("SELECT COALESCE(SUM(quantity), 0) FROM portfolio WHERE user_id=%s AND stock_symbol=%s", 
                       (user_id, full_symbol))
        quantity = cursor.fetchone()[0]  # Fetch result
        conn.close()  # Close connection
        return int(quantity)  # Ensure integer return type
    except Exception as e:
        print(f"Error fetching stock quantity: {e}")
        return 0  # Return 0 in case of error

# ✅ Buy stock (Handles average price calculation & database updates)
def buy_stock(user_id, symbol, quantity):
    """
    Executes a stock purchase, updating portfolio and computing average price.

    Args:
        user_id (int): User ID.
        symbol (str): Stock ticker symbol.
        quantity (int): Number of shares to buy.

    Returns:
        str: Confirmation message or error message.
    """
    try:
        conn = get_db_connection()  # Get database connection
        cursor = conn.cursor()
        full_symbol = symbol.upper() + ".BO"  # Convert symbol to BSE format

        stock_price = get_stock_price(symbol)  # Fetch current stock price
        if stock_price is None:
            return "Error: Could not fetch stock price."

        # Check if the user already owns this stock
        cursor.execute("SELECT quantity, avg_price FROM portfolio WHERE user_id = %s AND stock_symbol = %s", 
                       (user_id, full_symbol))
        result = cursor.fetchone()

        if result:
            existing_quantity, avg_price = result
            existing_quantity = int(existing_quantity or 0)
            avg_price = float(avg_price or 0)

            # Calculate new average price
            total_quantity = existing_quantity + quantity
            new_avg_price = ((existing_quantity * avg_price) + (quantity * stock_price)) / total_quantity
            
            # Update existing stock entry
            cursor.execute("UPDATE portfolio SET quantity = %s, avg_price = %s WHERE user_id = %s AND stock_symbol = %s",
                           (total_quantity, new_avg_price, user_id, full_symbol))
        else:
            # Insert new stock entry if user does not own it
            cursor.execute("INSERT INTO portfolio (user_id, stock_symbol, quantity, avg_price) VALUES (%s, %s, %s, %s)",
                           (user_id, full_symbol, quantity, stock_price))

        conn.commit()  # Commit transaction
        cursor.close()
        conn.close()
        return f"✅ Bought {quantity} shares of {symbol} at ₹{stock_price:.2f}."
    except Exception as e:
        conn.rollback()  # Rollback transaction in case of an error
        cursor.close()
        conn.close()
        return f"Error: {e}"

# ✅ Sell stock (Handles stock validation, portfolio updates & trading history logging)
def sell_stock(user_id, symbol, quantity):
    """
    Executes a stock sale, updating the portfolio and logging the transaction.

    Args:
        user_id (int): User ID.
        symbol (str): Stock ticker symbol.
        quantity (int): Number of shares to sell.

    Returns:
        str: Confirmation message or error message.
    """
    try:
        conn = get_db_connection()  # Get database connection
        cursor = conn.cursor()
        full_symbol = symbol.upper() + ".BO"  # Convert symbol to BSE format

        # Check user's stock quantity
        cursor.execute("SELECT quantity, avg_price FROM portfolio WHERE user_id = %s AND stock_symbol = %s", 
                       (user_id, full_symbol))
        result = cursor.fetchone()

        if not result:
            return "❌ Not enough shares to sell!"
        
        existing_quantity, avg_price = result
        existing_quantity = int(existing_quantity or 0)
        avg_price = float(avg_price or 0)

        if existing_quantity < quantity:
            return "❌ Not enough shares to sell!"

        stock_price = get_stock_price(symbol)  # Fetch current stock price
        if stock_price is None:
            return "Error: Could not fetch stock price."

        total_cost = quantity * stock_price  # Calculate total transaction cost

        # Update or remove stock from portfolio
        new_quantity = existing_quantity - quantity
        if new_quantity > 0:
            cursor.execute("UPDATE portfolio SET quantity = %s WHERE user_id=%s AND stock_symbol = %s",
                           (new_quantity, user_id, full_symbol))
        else:
            cursor.execute("DELETE FROM portfolio WHERE user_id=%s AND stock_symbol = %s", (user_id, full_symbol))

        # ✅ Ensure `total_cost` is included in the insert statement
        cursor.execute("""
            INSERT INTO trading_history (user_id, stock_symbol, action, quantity, price, total_cost) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, full_symbol, "SELL", quantity, stock_price, total_cost))

        conn.commit()  # Commit transaction
        cursor.close()
        conn.close()
        return f"✅ Sold {quantity} shares of {symbol} at ₹{stock_price:.2f}."
    except Exception as e:
        conn.rollback()  # Rollback transaction on failure
        cursor.close()
        conn.close()
        return f"Error: {e}"
