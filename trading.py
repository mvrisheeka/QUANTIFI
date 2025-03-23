import yfinance as yf
from db_config import get_db_connection
import time
from decimal import Decimal

# ✅ Get live stock price with retries
def get_stock_price(symbol, retries=3):
    full_symbol = symbol.upper() + ".BO"  # Append ".BO" for BSE stocks
    for attempt in range(retries):
        try:
            stock = yf.Ticker(full_symbol)
            data = stock.history(period="1d")
            if not data.empty:
                return Decimal(str(data["Close"].iloc[-1]))  # Convert float to Decimal
        except Exception as e:
            print(f"Error fetching stock price ({attempt+1}/{retries}): {e}")
            time.sleep(1)  # Wait before retrying
    return None  # Return None if all attempts fail

# ✅ Get stock quantity from portfolio (Fixed using Solution 3)
def get_stock_quantity(user_id, symbol):
    try:
        conn = get_db_connection()
        
        # Open cursor
        cursor = conn.cursor()
        full_symbol = symbol.upper() + ".BO"

        # Execute the SELECT query
        cursor.execute("SELECT COALESCE(SUM(quantity), 0) FROM portfolio WHERE user_id=%s AND stock_symbol=%s", 
                       (user_id, full_symbol))
        
        # Fetch the result immediately
        quantity = cursor.fetchone()[0]

        # Close cursor before returning
        cursor.close()
        conn.close()

        return int(quantity)  # Ensure integer return type

    except Exception as e:
        print(f"Error fetching stock quantity: {e}")
        return 0


# ✅ Buy stock (Handles average price calculation & database updates)
def buy_stock(user_id, symbol, quantity):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(buffered=True)  # ✅ Prevents "Unread result found"
        full_symbol = symbol.upper() + ".BO"

        stock_price = get_stock_price(symbol)
        if stock_price is None:
            return "Error: Could not fetch stock price."

        stock_price_decimal = Decimal(str(stock_price))  # ✅ Convert to Decimal for accurate calculations

        # ✅ Fetch result immediately after SELECT to avoid "Unread result found"
        cursor.execute("SELECT quantity, avg_price FROM portfolio WHERE user_id = %s AND stock_symbol = %s", 
                       (user_id, full_symbol))
        result = cursor.fetchone()  # ✅ Fetch immediately

        if result:
            existing_quantity, avg_price = result
            existing_quantity = int(existing_quantity or 0)
            avg_price = Decimal(str(avg_price or 0))  # ✅ Convert to Decimal

            total_quantity = existing_quantity + quantity
            new_avg_price = ((existing_quantity * avg_price) + (quantity * stock_price_decimal)) / total_quantity

            cursor.execute("UPDATE portfolio SET quantity = %s, avg_price = %s WHERE user_id = %s AND stock_symbol = %s",
                           (total_quantity, new_avg_price, user_id, full_symbol))
        else:
            cursor.execute("INSERT INTO portfolio (user_id, stock_symbol, quantity, avg_price) VALUES (%s, %s, %s, %s)",
                           (user_id, full_symbol, quantity, stock_price_decimal))

        conn.commit()
        cursor.close()
        conn.close()
        return f"✅ Bought {quantity} shares of {symbol} at ₹{stock_price_decimal:.2f}."
    
    except Exception as e:
        conn.rollback()  # ✅ Rollback transaction in case of an error
        cursor.close()
        conn.close()
        return f"Error: {e}"

# ✅ Sell stock (Handles stock validation, portfolio updates & trading history logging)
def sell_stock(user_id, symbol, quantity):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(buffered=True)  # ✅ Buffered cursor prevents unread result issues
        full_symbol = symbol.upper() + ".BO"

        # ✅ Check user's stock quantity
        cursor.execute("SELECT quantity, avg_price FROM portfolio WHERE user_id = %s AND stock_symbol = %s", 
                       (user_id, full_symbol))
        result = cursor.fetchone()

        if not result:
            cursor.close()
            conn.close()
            return "❌ Not enough shares to sell!"

        existing_quantity, avg_price = result
        existing_quantity = int(existing_quantity or 0)
        avg_price = Decimal(str(avg_price or 0))  # ✅ Convert to Decimal for precision

        if existing_quantity < quantity:
            cursor.close()
            conn.close()
            return "❌ Not enough shares to sell!"

        # ✅ Fetch latest stock price
        stock_price = get_stock_price(symbol)
        if stock_price is None:
            cursor.close()
            conn.close()
            return "Error: Could not fetch stock price."

        stock_price_decimal = Decimal(str(stock_price))  # ✅ Convert to Decimal
        total_cost = quantity * stock_price_decimal  # ✅ Calculate total transaction cost

        # ✅ Update or remove stock from portfolio
        new_quantity = existing_quantity - quantity
        if new_quantity > 0:
            cursor.execute("UPDATE portfolio SET quantity = %s WHERE user_id=%s AND stock_symbol = %s",
                           (new_quantity, user_id, full_symbol))
        else:
            cursor.execute("DELETE FROM portfolio WHERE user_id=%s AND stock_symbol = %s", (user_id, full_symbol))

        # ✅ Log transaction in `trading_history`
        cursor.execute(""" 
            INSERT INTO trading_history (user_id, stock_symbol, action, quantity, price, total_cost) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, full_symbol, "SELL", quantity, stock_price_decimal, total_cost))

        conn.commit()  # ✅ Commit transaction

        cursor.close()
        conn.close()
        return f"✅ Sold {quantity} shares of {symbol} at ₹{stock_price_decimal:.2f}."
    
    except Exception as e:
        conn.rollback()  # ❌ Rollback transaction in case of failure
        cursor.close()
        conn.close()
        return f"Error: {e}"

        # ✅ Ensure `total_cost` is included in the insert statement
        cursor.execute(""" 
            INSERT INTO trading_history (user_id, stock_symbol, action, quantity, price, total_cost) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, full_symbol, "SELL", quantity, stock_price, total_cost))

        conn.commit()
        cursor.close()
        conn.close()
        return f"✅ Sold {quantity} shares of {symbol} at ₹{stock_price:.2f}."
    except Exception as e:
        conn.rollback()  # Rollback transaction on failure
        cursor.close()
        conn.close()
        return f"Error: {e}"
