import sys
import os
import dotenv
import pandas as pd
# 获取项目根目录的绝对路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# 将项目根目录添加到 Python 模块搜索路径
sys.path.append(project_root)
# 然后再导入你的模块
from fmpxx import FMPClient
from fmpxx.exceptions import FMPAPIError, InvalidAPIKeyError, SymbolNotFoundError, RateLimitExceededError, FMPConnectionError
# Set pandas display options for better output in console
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)





dotenv.load_dotenv()

API_Key = os.getenv("FMP_KEY")
ticker = 'AAPL'

if not API_Key:
    print("Error: FMP_KEY environment variable not set. Please set it in your .env file or environment.")
    sys.exit(1)

# Test stocks functionality specifically
client = FMPClient(api_key=API_Key)

print("\n=== Testing Stocks Module ===")

try:
    # Test historical price full
    print(f"\n1. Testing historical_price_full for {ticker}...")
    historical_prices = client.stocks.historical_price_full(ticker, start="2023-01-01", end="2023-01-10")
    print(f"   ✓ Historical prices retrieved: {len(historical_prices)} rows")
    print(f"   ✓ Columns: {list(historical_prices.columns)}")
    print(f"   ✓ Sample data:\n{historical_prices.head(3)}")

    # Test daily prices
    print(f"\n2. Testing daily_prices for {ticker}...")
    daily_prices = client.stocks.daily_prices(ticker, period=1)
    print(f"   ✓ Daily prices retrieved: {len(daily_prices)} rows")
    print(f"   ✓ Sample data:\n{daily_prices.head(2)}")

    # Test stock list
    print("\n3. Testing stock_list...")
    stock_list = client.stocks.stock_list()
    print(f"   ✓ Stock list retrieved: {len(stock_list)} stocks")

    # Test quote
    print(f"\n4. Testing quote for {ticker}...")
    quote = client.stocks.quote(ticker)
    print(f"   ✓ Quote retrieved: {len(quote)} rows")
    print(f"   ✓ Quote data:\n{quote}")

    # Test search
    print("\n5. Testing search...")
    search_results = client.stocks.search(query='Apple', limit=3)
    print(f"   ✓ Search results: {len(search_results)} matches")

    # Test JSON format using convert_to_json
    print(f"\n6. Testing JSON format output for {ticker}...")
    df_data = client.stocks.historical_price_full(ticker)
    json_quote = client.convert_to_json(df_data)
    print(json_quote)

    print("\n=== All Stocks Tests Passed! ===")

except InvalidAPIKeyError:
    print("Test Failed: Invalid API Key. Please check your FMP_KEY.")
except SymbolNotFoundError as e:
    print(f"Test Failed: Symbol not found. {e}")
except RateLimitExceededError:
    print("Test Failed: Rate limit exceeded. Please wait and try again.")
except FMPConnectionError as e:
    print(f"Test Failed: Connection error. {e}")
except FMPAPIError as e:
    print(f"Test Failed: An FMP API error occurred. {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    import traceback
    traceback.print_exc()