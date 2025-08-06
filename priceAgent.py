import os
import time
import requests
import json
from datetime import datetime, timezone
from pydantic import BaseModel, Field, ValidationError
from typing import List, Set
from dotenv import load_dotenv
from supabase import create_client, Client

# Use Pydantic-AI for agent capabilities
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

# --- 1. Load Environment Variables & Initialize Clients ---
load_dotenv()

# Supabase Credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# CoinGecko API Key
COINGECKO_API_KEY = os.getenv("CRYPTO_API_KEY")

# --- 2. Define the Rich Data Schema (from V3) ---
class CryptoInfo(BaseModel):
    """Represents the rich data for a single cryptocurrency."""
    id: str = Field(..., description="The unique ID of the cryptocurrency, e.g., 'bitcoin'.")
    symbol: str = Field(..., description="The ticker symbol, e.g., 'btc'.")
    name: str = Field(..., description="The display name, e.g., 'Bitcoin'.")
    price_in_usd: float = Field(..., alias="current_price", description="The current price in USD.")
    last_updated: datetime = Field(..., description="The timestamp of the last price update.")

# --- 3. Define Tools for the AI Agent ---

def fetch_top_50_coins_data() -> List[CryptoInfo]:
    """
    Fetches rich data for the top 50 cryptocurrencies from CoinGecko.
    This function acts as a 'tool' for our AI agent. It's reliable and fast.
    """
    print("🤖 AI Agent triggered tool: fetch_top_50_coins_data")
    if not COINGECKO_API_KEY:
        raise ValueError("COINGECKO_API_KEY environment variable not found.")

    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 50,
        "page": 1,
        "sparkline": "false",
        "x_cg_demo_api_key": COINGECKO_API_KEY
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    
    # Directly validate the API data into our Pydantic models.
    # This is far more reliable than asking an LLM to parse and format JSON.
    coins_data = [CryptoInfo.model_validate(item) for item in response.json()]
    print(f"✅ Successfully fetched and validated data for {len(coins_data)} coins.")
    return coins_data

def upsert_crypto_data(supabase_client: Client, data: List[CryptoInfo]):
    """
    Upserts (updates or inserts) cryptocurrency data into the Supabase table.
    """
    if not data:
        print("No data to upload.")
        return

    print(f"Uploading {len(data)} records to Supabase...")
    data_to_upsert = [
        coin.model_dump(by_alias=True, exclude={'last_updated'}) | {'last_updated': coin.last_updated.isoformat()}
        for coin in data
    ]
    
    # The 'id' column is used as the conflict target for the upsert operation.
    response = supabase_client.from_("cryptocurrencies").upsert(data_to_upsert, on_conflict='id').execute()
    print("✅ Successfully upserted data to Supabase.")


# --- 4. The Main Application Loop with AI Agent ---
def main():
    """
    Main function to run the AI-driven data fetching and database update cycle.
    """
    if not all([SUPABASE_URL, SUPABASE_KEY]):
        print("❌ Supabase URL or Key not found. Exiting.")
        return

    # --- Initialize Clients ---
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("Supabase client initialized.")

    # Initialize the Pydantic-AI Agent (using local Ollama Llama 3.2 from V2)
    ollama_provider = OpenAIProvider(base_url='http://localhost:11434/v1', api_key='ollama')
    ollama_model = OpenAIModel(model_name='llama3.2', provider=ollama_provider)
    # Give the agent the 'fetch_top_50_coins_data' function as a tool it can use
    agent = Agent(
    model=ollama_model, 
    output_type=List[CryptoInfo], 
    tools=[fetch_top_50_coins_data] # <--- Changed to 'tools'
)
    print("Pydantic-AI agent initialized with Llama 3.2.")

    # --- State for "Active Listening" ---
    previous_top_50_ids: Set[str] = set()
    update_interval_seconds = 5  # 5 seconds

    while True:
        print(f"\n--- Starting new data cycle at {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z')} ---")
        try:
            # Step 1: Instruct the AI Agent to perform the task.
            # The agent will determine that it needs to call the `fetch_top_50_coins_data` tool.
            prompt = "Get the latest market data for the top 50 cryptocurrencies by market cap."
            print(f"Sending prompt to agent: '{prompt}'")
            
            # The .run() method will execute the tool and return its validated output directly.
            latest_coin_data: List[CryptoInfo] = agent.run_sync(prompt)

            # Step 2: "Active Listening" - Check for changes in the top 50 list.
            current_top_50_ids = {coin.id for coin in latest_coin_data}
            
            if previous_top_50_ids and current_top_50_ids != previous_top_50_ids:
                new_coins = current_top_50_ids - previous_top_50_ids
                dropped_coins = previous_top_50_ids - current_top_50_ids
                if new_coins:
                    print(f"📢 Market Shift Detected! New coins in top 50: {', '.join(new_coins)}")
                if dropped_coins:
                    print(f"📢 Market Shift Detected! Coins that dropped out of top 50: {', '.join(dropped_coins)}")
            
            # Update the state for the next cycle
            previous_top_50_ids = current_top_50_ids

            # Step 3: Upsert this data into your Supabase database.
            upsert_crypto_data(supabase, latest_coin_data)

        except requests.RequestException as e:
            print(f"❌ API Error: Failed to fetch data from CoinGecko. {e}")
        except ValidationError as e:
            print(f"❌ Data Validation Error: The API data did not match our schema. {e}")
        except Exception as e:
            print(f"❌ An unexpected error occurred: {e}")

        print(f"--- Cycle finished. Waiting for {update_interval_seconds} seconds... ---")
        time.sleep(update_interval_seconds)

if __name__ == "__main__":
    main()