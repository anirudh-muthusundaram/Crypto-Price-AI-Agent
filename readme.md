# Pydantic AI Crypto Price Agent

An intelligent cryptocurrency price monitoring agent that uses Pydantic-AI with local Llama 3.2 to fetch and analyze real-time crypto market data. The agent actively monitors the top 50 cryptocurrencies, detects market shifts, and updates your Supabase database automatically.

## Features

- 🤖 **AI-Powered Data Fetching**: Uses Pydantic-AI with local Llama 3.2 model
- 📊 **Real-time Market Monitoring**: Tracks top 50 cryptocurrencies by market cap
- 🔍 **Active Market Listening**: Detects when coins enter/exit the top 50
- 🗄️ **Database Integration**: Automatically updates Supabase with latest data
- ⚡ **Fast & Reliable**: Fetches data every 5 seconds with error handling
- 🔄 **Data Validation**: Uses Pydantic models for reliable data parsing

## Prerequisites

- Python 3.8 or higher
- Ollama (for running local Llama 3.2 model)
- Supabase account and project
- CoinGecko API key
- Internet connection

## Installation Guide

### 1. Install Ollama

Ollama allows you to run large language models locally on your machine.

#### Windows
1. Visit [ollama.com](https://ollama.com) and download the Windows installer
2. Run the installer and follow the setup wizard
3. Open Command Prompt or PowerShell to verify installation:
```cmd
ollama --version
```

#### macOS
```bash
# Using Homebrew (recommended)
brew install ollama

# Or download from ollama.com and run the installer
```

#### Linux
```bash
# Install via curl
curl -fsSL https://ollama.com/install.sh | sh

# Or using package managers:
# Ubuntu/Debian
sudo apt update && sudo apt install ollama

# Fedora
sudo dnf install ollama

# Arch Linux
sudo pacman -S ollama
```

### 2. Download and Run Llama 3.2 Model

After installing Ollama, download the Llama 3.2 model:

```bash
ollama pull llama3.2
```

**Start the Ollama service:**

#### Windows
```cmd
# Ollama typically starts automatically on Windows
# If not, run:
ollama serve
```

#### macOS
```bash
# Start Ollama service
ollama serve
```

#### Linux
```bash
# Start Ollama service
ollama serve

# Or if using systemd:
sudo systemctl start ollama
sudo systemctl enable ollama  # To start on boot
```

**Verify Llama 3.2 is working:**
```bash
ollama run llama3.2
# You should see a prompt where you can chat with the model
# Type /bye to exit
```

### 3. Set Up Python Environment

#### Windows
```cmd
# Create virtual environment
python -m venv crypto_agent_env
crypto_agent_env\Scripts\activate

# Install dependencies
pip install pydantic-ai requests python-dotenv supabase pydantic
```

#### macOS/Linux
```bash
# Create virtual environment
python3 -m venv crypto_agent_env
source crypto_agent_env/bin/activate

# Install dependencies
pip install pydantic-ai requests python-dotenv supabase pydantic
```

### 4. Set Up Environment Variables

Create a `.env` file in your project directory:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_service_role_key_here

# CoinGecko API Key (get free key from coingecko.com)
CRYPTO_API_KEY=your_coingecko_api_key_here
```

**Get your API keys:**

1. **Supabase credentials**:
   - Go to your Supabase project → Settings → API
   - Copy the Project URL and service_role key

2. **CoinGecko API key**:
   - Visit [coingecko.com](https://www.coingecko.com/en/api)
   - Sign up for a free account
   - Get your API key from the dashboard

### 5. Set Up Supabase Database

Create the cryptocurrencies table in your Supabase project:

```sql
CREATE TABLE cryptocurrencies (
    id TEXT PRIMARY KEY,
    symbol TEXT NOT NULL,
    name TEXT NOT NULL,
    current_price NUMERIC NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for better performance
CREATE INDEX idx_cryptocurrencies_symbol ON cryptocurrencies(symbol);
CREATE INDEX idx_cryptocurrencies_last_updated ON cryptocurrencies(last_updated);
```

## Running the Agent

### 1. Start Ollama and Llama 3.2

**In Terminal/Command Prompt 1:**
```bash
ollama run llama3.2
```

Keep this running in the background. You can minimize this terminal.

### 2. Run the Price Agent

**In Terminal/Command Prompt 2:**

#### Windows
```cmd
# Navigate to your project directory
cd path\to\your\project

# Activate virtual environment
crypto_agent_env\Scripts\activate

# Run the agent
python priceAgent.py
```

#### macOS/Linux
```bash
# Navigate to your project directory
cd path/to/your/project

# Activate virtual environment
source crypto_agent_env/bin/activate

# Run the agent
python3 priceAgent.py
```

## Expected Output

When running successfully, you should see output like this:

```
Supabase client initialized.
Pydantic-AI agent initialized with Llama 3.2.

--- Starting new data cycle at 2024-01-15 10:30:45 UTC ---
Sending prompt to agent: 'Get the latest market data for the top 50 cryptocurrencies by market cap.'
🤖 AI Agent triggered tool: fetch_top_50_coins_data
✅ Successfully fetched and validated data for 50 coins.
Uploading 50 records to Supabase...
✅ Successfully upserted data to Supabase.
--- Cycle finished. Waiting for 5 seconds... ---

--- Starting new data cycle at 2024-01-15 10:30:50 UTC ---
📢 Market Shift Detected! New coins in top 50: dogecoin
📢 Market Shift Detected! Coins that dropped out of top 50: some-other-coin
```

## Configuration Options

You can modify these settings in `priceAgent.py`:

```python
# Change update frequency (in seconds)
update_interval_seconds = 5  # Default: 5 seconds

# Change number of coins to fetch (max 250 for free CoinGecko API)
"per_page": 50,  # In the fetch_top_50_coins_data function
```

## Troubleshooting

### Common Error: "Connection refused" or "Ollama not responding"

**Cause**: Ollama service is not running or not accessible.

**Solutions**:
1. **Check if Ollama is running**:
```bash
curl http://localhost:11434/api/tags
```

2. **Start Ollama service**:
```bash
ollama serve
```

3. **Verify Llama 3.2 is installed**:
```bash
ollama list
# Should show llama3.2 in the list
```

### Common Error: "Model not found" or "llama3.2 not available"

**Solutions**:
1. **Pull the model again**:
```bash
ollama pull llama3.2
```

2. **Check available models**:
```bash
ollama list
```

3. **Try alternative model names**:
```python
# In priceAgent.py, try:
ollama_model = OpenAIModel(model_name='llama3.2:latest', provider=ollama_provider)
```

### Common Error: "CRYPTO_API_KEY not found"

**Solutions**:
1. **Check your .env file** exists and has the correct format
2. **Verify API key** is valid at coingecko.com
3. **Check file location** - .env should be in the same directory as priceAgent.py

### Common Error: "Supabase connection failed"

**Solutions**:
1. **Verify Supabase credentials** in your .env file
2. **Check database table exists** with correct schema
3. **Ensure service_role key** is used (not anon key)

### Performance Issues

**If the agent is slow**:
1. **Check internet connection** for API calls
2. **Increase update interval**:
```python
update_interval_seconds = 30  # Change from 5 to 30 seconds
```

3. **Reduce number of coins**:
```python
"per_page": 25,  # Change from 50 to 25
```

### Ollama Service Management

#### Windows
```cmd
# Check if Ollama is running
tasklist | find "ollama"

# Kill Ollama if needed
taskkill /f /im ollama.exe

# Restart
ollama serve
```

#### macOS
```bash
# Check if Ollama is running
ps aux | grep ollama

# Kill Ollama if needed
pkill ollama

# Restart
ollama serve
```

#### Linux
```bash
# If using systemd
sudo systemctl status ollama
sudo systemctl restart ollama

# Manual process management
ps aux | grep ollama
pkill ollama
ollama serve
```

## File Structure

```
your-project/
├── priceAgent.py          # Main agent script
├── .env                   # Environment variables (create this)
├── README.md             # This guide
└── crypto_agent_env/     # Virtual environment directory
```

## Advanced Configuration

### Using Different Models

You can experiment with other Ollama models:

```bash
# Install other models
ollama pull llama3.1
ollama pull codellama
ollama pull mistral

# Update priceAgent.py
ollama_model = OpenAIModel(model_name='llama3.1', provider=ollama_provider)
```

### Custom Update Intervals

Modify the update frequency based on your needs:

```python
# For development (slower updates)
update_interval_seconds = 60  # 1 minute

# For production monitoring (faster updates)
update_interval_seconds = 1   # 1 second (be careful with API limits)
```

## API Rate Limits

- **CoinGecko Free API**: 30 calls/minute
- **With API key**: 500 calls/minute
- **Current agent frequency**: 12 calls/minute (every 5 seconds)

## Security Notes

- Never commit your `.env` file to version control
- Use environment variables for all sensitive data
- Consider using CoinGecko Pro API for production use
- Monitor your API usage to avoid hitting rate limits

## Stopping the Agent

To stop the agent:
1. **Press `Ctrl + C`** in the terminal running priceAgent.py
2. **Stop Ollama** if no longer needed:
```bash
# Kill the ollama process
pkill ollama
```

# Supabase Crypto MCP Server

A Model Context Protocol (MCP) server that provides cryptocurrency database operations using Supabase as the backend. This server allows Claude Desktop to interact with a cryptocurrency database through various CRUD operations.

## Features

- **Get all cryptocurrencies**: Retrieve all cryptocurrency records from the database
- **Get cryptocurrency by symbol**: Fetch a specific cryptocurrency by its symbol (e.g., BTC, ETH)
- **Add cryptocurrency**: Insert new cryptocurrency records
- **Update cryptocurrency price**: Update the price of existing cryptocurrencies
- **Delete cryptocurrency**: Remove cryptocurrencies from the database

## Prerequisites

- Python 3.8 or higher
- Claude Desktop application
- Supabase account and project
- macOS, Windows, or Linux

## Required Dependencies

- `fastmcp`
- `supabase`
- `python-dotenv`

## Setup Instructions

### 1. Supabase Database Setup

1. **Create a Supabase account** at [supabase.com](https://supabase.com)

2. **Create a new project** in your Supabase dashboard

3. **Create the cryptocurrencies table** using the SQL editor:

```sql
CREATE TABLE cryptocurrencies (
    id TEXT PRIMARY KEY,
    symbol TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    price_in_usd NUMERIC NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add some sample data (optional)
INSERT INTO cryptocurrencies (id, symbol, name, price_in_usd) VALUES
('bitcoin', 'BTC', 'Bitcoin', 65000.00),
('ethereum', 'ETH', 'Ethereum', 3500.00);
```

4. **Get your Supabase credentials**:
   - Go to Project Settings → API
   - Copy your **Project URL** (SUPABASE_URL)
   - Copy your **service_role** key (SUPABASE_KEY) - NOT the anon key

### 2. Install UV Package Manager

UV is required for running the MCP server with FastMCP.

**On macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**On Windows:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Add UV to your PATH:**
```bash
# For bash/zsh
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# For fish
echo 'set -gx PATH $HOME/.local/bin $PATH' >> ~/.config/fish/config.fish
```

**Verify installation:**
```bash
which uv
# Should return: /Users/[username]/.local/bin/uv (on macOS)
```

### 3. Project Setup

1. **Clone or download the project files**

2. **Create a virtual environment and install dependencies:**
```bash
cd your-project-directory
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install fastmcp supabase python-dotenv
```

3. **Create a `.env` file** in your project root:
```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_service_role_key
```

4. **Test the connection locally:**
```bash
python main.py
```

### 4. Claude Desktop Configuration

#### Method 1: Using FastMCP (Recommended)

```bash
fastmcp install claude-desktop main.py
```

#### Method 2: Manual Configuration

If the automatic installation doesn't work, manually edit your Claude Desktop configuration:

**Find your config file:**
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

**Edit the configuration:**
```json
{
  "mcpServers": {
    "Supabase Crypto DB MCP Server": {
      "command": "/full/path/to/uv",
      "args": [
        "run",
        "--with",
        "fastmcp",
        "fastmcp",
        "run",
        "/full/path/to/your/main.py"
      ],
      "env": {
        "SUPABASE_URL": "your_actual_supabase_url",
        "SUPABASE_KEY": "your_actual_supabase_key"
      }
    }
  }
}
```

**Alternative Python-only configuration:**
```json
{
  "mcpServers": {
    "Supabase Crypto DB MCP Server": {
      "command": "python",
      "args": ["/full/path/to/your/main.py"],
      "env": {
        "SUPABASE_URL": "your_actual_supabase_url",
        "SUPABASE_KEY": "your_actual_supabase_key"
      }
    }
  }
}
```

### 5. Final Steps

1. **Restart Claude Desktop completely** (Cmd+Q on macOS, then reopen)
2. **Open a new conversation** in Claude Desktop
3. **Verify the connection** by asking Claude to list all cryptocurrencies

## Usage Examples

Once connected, you can ask Claude to:

- "Show me all cryptocurrencies in the database"
- "Get information about Bitcoin"
- "Add Cardano (ADA) to the database with a price of $0.45"
- "Update the price of Ethereum to $3600"
- "Delete Dogecoin from the database"

## Troubleshooting

### Common Error: "spawn uv ENOENT"

**Cause**: Claude Desktop cannot find the `uv` command.

**Solutions**:

1. **Check if UV is installed and in PATH:**
```bash
which uv
# Should return the path to uv
```

2. **Use full path to UV in configuration:**
```json
{
  "mcpServers": {
    "Supabase Crypto DB MCP Server": {
      "command": "/Users/[username]/.local/bin/uv",
      "args": [...],
      "env": {...}
    }
  }
}
```

3. **Use Python directly instead of UV:**
```json
{
  "mcpServers": {
    "Supabase Crypto DB MCP Server": {
      "command": "python",
      "args": ["/full/path/to/main.py"],
      "env": {...}
    }
  }
}
```

### Common Error: "is not valid JSON"

**Cause**: The MCP server is outputting error messages instead of proper JSON.

**Solutions**:

1. **Test locally first:**
```bash
python main.py
```

2. **Check Supabase credentials** in your configuration

3. **Verify database table exists** and has correct structure

4. **Add debug output** to your code:
```python
try:
    supabase: SupabaseClient = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("Successfully connected to Supabase.")
    
    # Test connection
    test_response = supabase.table('cryptocurrencies').select("count", count="exact").execute()
    print(f"Connection test successful. Table has {test_response.count} rows.")
    
except Exception as e:
    print(f"Error connecting to Supabase: {e}")
    print(f"SUPABASE_URL: {SUPABASE_URL}")
    print(f"SUPABASE_KEY: {'*' * 10 if SUPABASE_KEY else 'None'}")
```

### Common Error: "Malformed JSON in config"

**Cause**: Syntax errors in the Claude Desktop configuration file.

**Solution**: Validate your JSON using an online JSON validator and ensure:
- No trailing commas
- Proper quotes around all strings
- Correct bracket/brace matching

### Environment Variable Issues

**Symptoms**: Connection errors or "None" values for environment variables

**Solutions**:

1. **Check environment variables are set:**
```bash
echo $SUPABASE_URL
echo $SUPABASE_KEY
```

2. **Verify .env file format** (no quotes needed):
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key
```

3. **Ensure correct key type**: Use the `service_role` key, not the `anon` key

### Still Having Issues?

1. **Completely restart Claude Desktop** (don't just refresh)
2. **Check Claude Desktop logs** for detailed error messages
3. **Verify all file paths** are absolute and correct
4. **Test the MCP server independently** before connecting to Claude
5. **Check Supabase project status** and API limits

## File Structure

```
your-project/
├── main.py                 # Main MCP server code
├── .env                   # Environment variables (create this)
├── README.md             # This file
└── requirements.txt      # Python dependencies (optional)
```

## Security Notes

- Never commit your `.env` file to version control
- Use the service role key only in secure environments
- Consider using row-level security (RLS) in Supabase for production use
- Regularly rotate your API keys

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve this MCP server.

## MIT License

Copyright (c) 2024 [Your Real Name or GitHub Username]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.