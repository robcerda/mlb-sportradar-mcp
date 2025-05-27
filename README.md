# MLB SportRadar MCP Server

Model Context Protocol (MCP) server for connecting Claude with the SportRadar MLB API. It provides tools for accessing MLB game data, standings, player statistics, and more through the SportRadar API.

## Requirements

* Python 3.12 or higher
* Model Context Protocol (MCP) Python SDK
* httpx
* python-dotenv
* SportRadar API key

## Setup

### 1. Get SportRadar API Key

1. Sign up at [SportRadar Developer Portal](https://developer.sportradar.com/)
2. Get your MLB API key (trial or production)

### 2. Install uv (recommended)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 3. Clone this repository

```bash
git clone https://github.com/yourusername/mlb-sportradar-mcp.git
cd mlb-sportradar-mcp
```

### 4. Create and activate a virtual environment

```bash
# Create virtual environment
uv venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate
```

### 5. Install dependencies

```bash
# Option 1: Using uv (recommended)
uv sync

# Option 2: Using pip with requirements.txt
pip install -r requirements.txt

# Option 3: Install as editable package
uv pip install -e .
```

### 6. Set up environment variables

Create a `.env` file in the project root with your SportRadar API key:

```bash
SPORTRADAR_API_KEY=your_api_key_here
```

## Usage

### 1. Configure Claude Desktop

First, install the MCP CLI globally:

```bash
uv tool install "mcp[cli]"
```

Then add this server to your Claude Desktop configuration file (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "MLB SportRadar": {
      "command": "/Users/<USERNAME>/.local/share/uv/tools/mcp/bin/mcp",
      "args": ["run", "/full/path/to/mlb-sportradar-mcp/src/mlb_sportradar_mcp/server.py"]
    }
  }
}
```

**Important**: Replace `/full/path/to/` with the actual absolute path to your `mlb-sportradar-mcp` directory.

Restart Claude Desktop after saving the configuration.

### 2. Use the MCP server with Claude

Once configured, Claude Desktop will have access to these MLB SportRadar tools:

**Game Data:**
* **`get_daily_schedule`**: Get MLB schedule for a specific date or today
* **`get_game_summary`**: Get summary information for a specific game
* **`get_game_boxscore`**: Get detailed boxscore for a specific game
* **`get_game_play_by_play`**: Get detailed play-by-play data for a game
* **`get_game_pitch_metrics`**: Get pitch-level metrics and Statcast data

**Team & League:**
* **`get_standings`**: Get MLB standings for a specific year and league
* **`get_team_profile`**: Get detailed team information
* **`get_team_roster`**: Get current roster for a specific team
* **`get_team_hierarchy`**: Get complete MLB team hierarchy with divisions
* **`get_seasonal_statistics`**: Get seasonal statistics for a team

**Player Data:**
* **`get_player_profile`**: Get detailed player information
* **`get_player_seasonal_stats`**: Get seasonal statistics for a player
* **`get_seasonal_splits`**: Get player splits (home/away, vs lefty/righty, etc.)
* **`get_league_leaders`**: Get MLB league leaders in various categories

**League Information:**
* **`get_injuries`**: Get current MLB injury report
* **`get_transactions`**: Get MLB transactions for a specific date
* **`get_draft_summary`**: Get MLB draft summary for a specific year

**Example queries to try with Claude:**
- "Show me today's MLB schedule"
- "Get the current AL standings" 
- "What are the current batting leaders in MLB?"
- "Show me the injury report for MLB"
- "Get play-by-play data for game [game_id]"
- "Show me pitch metrics for the latest game"
- "Get player splits for [player_name]"
- "What transactions happened today in MLB?"

## Development and testing

Install development dependencies and run the test suite with:

```bash
uv sync --all-extras
pytest -v tests
```

### Running the server locally

To start the server manually (useful when developing or testing), run:

```bash
mlb-sportradar-mcp
```

Alternatively, you can run it directly with:

```bash
uv run python src/mlb_sportradar_mcp/server.py
```

### Installing MCP CLI globally

If you want to use `mcp run` commands, install the MCP CLI globally:

```bash
uv tool install "mcp[cli]"
```

Then you can run:

```bash
mcp run src/mlb_sportradar_mcp/server.py
```

## API Endpoints

This MCP server uses the SportRadar MLB API v8 endpoints:

- **Schedule**: `/en/games/{year}/{month}/{day}/schedule.json`
- **Game Summary**: `/en/games/{game_id}/summary.json`
- **Game Boxscore**: `/en/games/{game_id}/boxscore.json`
- **Standings**: `/en/seasons/{year}/standings.json`
- **Player Profile**: `/en/players/{player_id}/profile.json`
- **Team Profile**: `/en/teams/{team_id}/profile.json`
- **League Leaders**: `/en/seasons/{year}/leaders.json`
- **Team Roster**: `/en/teams/{team_id}/roster.json`
- **Injuries**: `/en/injuries.json`

## Rate Limits

Please be aware of SportRadar's API rate limits. The trial API typically has lower limits than production keys. Monitor your usage to avoid hitting rate limits.

## License

MIT