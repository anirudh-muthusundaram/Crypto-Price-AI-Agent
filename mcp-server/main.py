import asyncio
import os
from fastmcp import FastMCP, Client
from supabase import create_client, Client as SupabaseClient
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional

# Load environment variables from a .env file
# Create a .env file in the same directory with your Supabase URL and Key
# SUPABASE_URL=your_supabase_url
# SUPABASE_KEY=your_supabase_service_role_key
load_dotenv()

# --- Supabase Configuration ---
# It's highly recommended to use environment variables for security
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# Check if the environment variables are set
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase URL and Key must be set in your environment variables or a .env file.")

# Initialize Supabase client
try:
    supabase: SupabaseClient = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("Successfully connected to Supabase.")
except Exception as e:
    print(f"Error connecting to Supabase: {e}")
    # Exit if we can't connect to the database
    exit()

# --- MCP Server Setup ---
mcp = FastMCP("Supabase Crypto DB MCP Server")

# --- MCP Tools for Database Operations ---

@mcp.tool
def get_all_cryptocurrencies() -> List[Dict[str, Any]]:
    """
    Retrieves all cryptocurrency records from the Supabase database.
    Returns a list of dictionaries, where each dictionary represents a cryptocurrency.
    """
    try:
        response = supabase.table('cryptocurrencies').select("*").execute()
        # The actual data is in response.data
        print(f"Successfully fetched {len(response.data)} records.")
        return response.data
    except Exception as e:
        print(f"Error fetching data from Supabase: {e}")
        return [{"error": str(e)}]

@mcp.tool
def get_cryptocurrency_by_symbol(symbol: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves a single cryptocurrency record by its symbol.
    :param symbol: The symbol of the cryptocurrency to fetch (e.g., 'BTC').
    """
    try:
        # Using 'eq' for an exact match on the symbol
        response = supabase.table('cryptocurrencies').select("*").eq('symbol', symbol.upper()).execute()
        if response.data:
            print(f"Successfully fetched record for symbol: {symbol}")
            return response.data[0]
        else:
            print(f"No record found for symbol: {symbol}")
            return None
    except Exception as e:
        print(f"Error fetching data for symbol {symbol}: {e}")
        return {"error": str(e)}

@mcp.tool
def add_cryptocurrency(id: str, symbol: str, name: str, price_in_usd: float) -> Dict[str, Any]:
    """
    Adds a new cryptocurrency to the database.
    The 'last_updated' field is handled automatically by the database (as CURRENT_TIMESTAMP).
    :param id: The unique identifier for the new cryptocurrency (e.g., 'bitcoin').
    :param symbol: The symbol of the new cryptocurrency (e.g., 'BTC').
    :param name: The name of the new cryptocurrency (e.g., 'Bitcoin').
    :param price_in_usd: The current price in USD.
    """
    try:
        # The insert method returns a response object with the inserted data
        response = supabase.table('cryptocurrencies').insert({
            "id": id,
            "symbol": symbol.upper(),
            "name": name,
            "price_in_usd": price_in_usd
        }).execute()
        print(f"Successfully added new cryptocurrency: {name}")
        return response.data[0]
    except Exception as e:
        print(f"Error adding cryptocurrency {name}: {e}")
        return {"error": str(e)}

@mcp.tool
def update_cryptocurrency_price(symbol: str, new_price: float) -> Optional[Dict[str, Any]]:
    """
    Updates the price of an existing cryptocurrency identified by its symbol.
    :param symbol: The symbol of the cryptocurrency to update.
    :param new_price: The new price in USD.
    """
    try:
        # The update method returns a response object with the updated data
        response = supabase.table('cryptocurrencies').update({
            "price_in_usd": new_price
        }).eq('symbol', symbol.upper()).execute()
        
        if response.data:
            print(f"Successfully updated price for {symbol}.")
            return response.data[0]
        else:
            print(f"Could not update price. Symbol '{symbol}' not found.")
            return None
    except Exception as e:
        print(f"Error updating price for {symbol}: {e}")
        return {"error": str(e)}
        
@mcp.tool
def delete_cryptocurrency(symbol: str) -> Dict[str, str]:
    """
    Deletes a cryptocurrency from the database by its symbol.
    :param symbol: The symbol of the cryptocurrency to delete.
    """
    try:
        # First, find the record to be deleted to return its info
        select_response = supabase.table('cryptocurrencies').select("*").eq('symbol', symbol.upper()).execute()
        if not select_response.data:
            return {"status": f"Error: Cryptocurrency with symbol '{symbol}' not found."}

        # Now, delete the record
        delete_response = supabase.table('cryptocurrencies').delete().eq('symbol', symbol.upper()).execute()
        
        if delete_response.data:
            print(f"Successfully deleted cryptocurrency with symbol: {symbol}")
            return {"status": f"Successfully deleted {symbol}", "deleted_record": delete_response.data[0]}
        else:
            # This case might happen if the record is deleted between the select and delete calls
            return {"status": f"Error: Could not delete cryptocurrency with symbol '{symbol}'."}

    except Exception as e:
        print(f"Error deleting cryptocurrency {symbol}: {e}")
        return {"status": "Error", "details": str(e)}


# --- Example Client Usage ---
# This part demonstrates how you would call the tools from a client application.
# You would run this part in a separate script or application (like Claude Desktop).

client = Client(mcp)

async def main():
    """Main function to demonstrate calling the MCP tools."""
    async with client:
        print("\n--- Getting all cryptocurrencies ---")
        all_coins = await client.call_tool("get_all_cryptocurrencies")
        print(all_coins)

        print("\n--- Adding a new cryptocurrency (Cardano) ---")
        new_coin = await client.call_tool("add_cryptocurrency", {
            "id": "cardano",
            "symbol": "ADA",
            "name": "Cardano",
            "price_in_usd": 0.45
        })
        print(new_coin)
        
        print("\n--- Getting a specific cryptocurrency (ADA) ---")
        ada_coin = await client.call_tool("get_cryptocurrency_by_symbol", {"symbol": "ADA"})
        print(ada_coin)

        print("\n--- Updating a cryptocurrency's price (ADA) ---")
        updated_ada = await client.call_tool("update_cryptocurrency_price", {
            "symbol": "ADA",
            "new_price": 0.48
        })
        print(updated_ada)
        
        print("\n--- Deleting a cryptocurrency (ADA) ---")
        delete_status = await client.call_tool("delete_cryptocurrency", {"symbol": "ADA"})
        print(delete_status)
        
        print("\n--- Verifying deletion ---")
        all_coins_after_delete = await client.call_tool("get_all_cryptocurrencies")
        print(all_coins_after_delete)


# if __name__ == "__main__":
    # To run this example, you need to have some data in your table first.
    # You can add some manually in the Supabase dashboard.
    # For example:
    # id: 'bitcoin', symbol: 'BTC', name: 'Bitcoin', price_in_usd: 65000.00
    # id: 'ethereum', symbol: 'ETH', name: 'Ethereum', price_in_usd: 3500.00
    
    # Running the main function to test the tools locally
    # In a real-world scenario, the MCP server would be running, and a separate
    # client would connect to it.
    # print("Running MCP tool demonstrations...")
    # asyncio.run(main())
    
    # To run the server and make it available for clients like Claude Desktop,
    # you would typically use a command provided by the FastMCP library to serve the app,
    # for example (this is hypothetical, check FastMCP docs):
    # `fastmcp serve your_script_name:mcp`

