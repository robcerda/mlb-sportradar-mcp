"""
MLB SportRadar MCP Server

This module implements a Model Context Protocol (MCP) server for connecting
Claude with the SportRadar MLB API. It provides tools for retrieving MLB
game data, standings, player statistics, and more.

Main Features:
    - Daily MLB schedules
    - Game summaries and boxscores
    - Team standings
    - Player profiles and statistics
    - League leaders
    - Error handling with user-friendly messages
    - Configurable parameters with environment variable support

Usage:
    This server is designed to be run as a standalone script and exposes several MCP tools
    for use with Claude Desktop or other MCP-compatible clients. The server loads configuration
    from environment variables (optionally via a .env file) and communicates with the SportRadar API.

    To run the server:
        $ python src/mlb_sportradar_mcp/server.py

    MCP tools provided:
        - get_daily_schedule
        - get_game_summary
        - get_game_boxscore
        - get_game_play_by_play
        - get_game_pitch_metrics
        - get_standings
        - get_player_profile
        - get_player_seasonal_stats
        - get_team_profile
        - get_team_roster
        - get_seasonal_statistics
        - get_league_leaders
        - get_seasonal_splits
        - get_injuries
        - get_transactions
        - get_draft_summary
        - get_team_hierarchy

    See the README for more details on configuration and usage.
"""

import os
import sys
import logging
import asyncio
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, date
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
import httpx

# Configure logging to stderr
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)
logger = logging.getLogger("mlb_sportradar_mcp")

# Load environment variables
load_dotenv()

# Get API key from environment
SPORTRADAR_API_KEY = os.getenv("SPORTRADAR_API_KEY")
if not SPORTRADAR_API_KEY:
    raise ValueError("SPORTRADAR_API_KEY environment variable is required")

# Initialize FastMCP server
mcp = FastMCP("mlb-sportradar-mcp")

# SportRadar MLB API base URL
BASE_URL = "https://api.sportradar.com/mlb/trial/v8"

async def get_http_client():
    """Get or create HTTP client with proper headers."""
    return httpx.AsyncClient(
        base_url=BASE_URL,
        params={"api_key": SPORTRADAR_API_KEY},
        timeout=30.0
    )

@mcp.tool()
async def get_daily_schedule(date_str: Optional[str] = None) -> Dict:
    """Get MLB schedule for a specific date (YYYY-MM-DD format) or today if not specified."""
    if date_str is None:
        date_str = date.today().strftime("%Y-%m-%d")
    
    async with await get_http_client() as client:
        try:
            # Format: /en/games/{year}/{month}/{day}/schedule.json
            date_parts = date_str.split("-")
            year, month, day = date_parts[0], date_parts[1], date_parts[2]
            
            response = await client.get(f"/en/games/{year}/{month}/{day}/schedule.json")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting daily schedule for {date_str}: {str(e)}")
            raise

@mcp.tool()
async def get_game_summary(game_id: str) -> Dict:
    """Get summary information for a specific MLB game."""
    async with await get_http_client() as client:
        try:
            response = await client.get(f"/en/games/{game_id}/summary.json")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting game summary for {game_id}: {str(e)}")
            raise

@mcp.tool()
async def get_game_boxscore(game_id: str) -> Dict:
    """Get detailed boxscore for a specific MLB game."""
    async with await get_http_client() as client:
        try:
            response = await client.get(f"/en/games/{game_id}/boxscore.json")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting game boxscore for {game_id}: {str(e)}")
            raise

@mcp.tool()
async def get_standings(
    year: Optional[int] = None,
    league: Optional[str] = None
) -> Dict:
    """Get MLB standings for a specific year and league (AL/NL) or current season if not specified."""
    if year is None:
        year = datetime.now().year
    
    async with await get_http_client() as client:
        try:
            url = f"/en/seasons/{year}/standings.json"
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            
            # Filter by league if specified
            if league and league.upper() in ['AL', 'NL']:
                # Filter standings by league
                if 'standings' in data and 'leagues' in data['standings']:
                    for league_data in data['standings']['leagues']:
                        if league_data.get('alias', '').upper() == league.upper():
                            return {'league': league_data}
            
            return data
        except Exception as e:
            logger.error(f"Error getting standings for {year}: {str(e)}")
            raise

@mcp.tool()
async def get_player_profile(player_id: str) -> Dict:
    """Get detailed profile information for a specific MLB player."""
    async with await get_http_client() as client:
        try:
            response = await client.get(f"/en/players/{player_id}/profile.json")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting player profile for {player_id}: {str(e)}")
            raise

@mcp.tool()
async def get_team_profile(team_id: str) -> Dict:
    """Get detailed profile information for a specific MLB team."""
    async with await get_http_client() as client:
        try:
            response = await client.get(f"/en/teams/{team_id}/profile.json")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting team profile for {team_id}: {str(e)}")
            raise

@mcp.tool()
async def get_league_leaders(
    year: Optional[int] = None,
    category: Optional[str] = "hitting"
) -> Dict:
    """Get MLB league leaders for a specific year and category (hitting/pitching)."""
    if year is None:
        year = datetime.now().year
    
    async with await get_http_client() as client:
        try:
            response = await client.get(f"/en/seasons/{year}/leaders.json")
            response.raise_for_status()
            data = response.json()
            
            # Filter by category if specified
            if category and category.lower() in ['hitting', 'pitching']:
                if 'leaders' in data:
                    filtered_leaders = {}
                    for key, value in data['leaders'].items():
                        if category.lower() in key.lower():
                            filtered_leaders[key] = value
                    if filtered_leaders:
                        return {'leaders': filtered_leaders, 'category': category}
            
            return data
        except Exception as e:
            logger.error(f"Error getting league leaders for {year}: {str(e)}")
            raise

@mcp.tool()
async def get_team_roster(team_id: str) -> Dict:
    """Get current roster for a specific MLB team."""
    async with await get_http_client() as client:
        try:
            response = await client.get(f"/en/teams/{team_id}/roster.json")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting team roster for {team_id}: {str(e)}")
            raise

@mcp.tool()
async def get_injuries() -> Dict:
    """Get current MLB injury report."""
    async with await get_http_client() as client:
        try:
            response = await client.get("/en/injuries.json")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting injury report: {str(e)}")
            raise

@mcp.tool()
async def get_game_play_by_play(game_id: str) -> Dict:
    """Get detailed play-by-play data for a specific MLB game."""
    async with await get_http_client() as client:
        try:
            response = await client.get(f"/en/games/{game_id}/pbp.json")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting play-by-play for game {game_id}: {str(e)}")
            raise

@mcp.tool()
async def get_game_pitch_metrics(game_id: str) -> Dict:
    """Get pitch-level metrics and Statcast data for a specific MLB game."""
    async with await get_http_client() as client:
        try:
            response = await client.get(f"/en/games/{game_id}/pitch_metrics.json")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting pitch metrics for game {game_id}: {str(e)}")
            raise

@mcp.tool()
async def get_seasonal_statistics(
    team_id: str,
    year: Optional[int] = None,
    season_type: Optional[str] = "REG"
) -> Dict:
    """Get seasonal statistics for a specific team."""
    if year is None:
        year = datetime.now().year
    
    async with await get_http_client() as client:
        try:
            response = await client.get(f"/en/seasons/{year}/{season_type}/teams/{team_id}/statistics.json")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting seasonal statistics for team {team_id}: {str(e)}")
            raise

@mcp.tool()
async def get_player_seasonal_stats(
    player_id: str,
    year: Optional[int] = None
) -> Dict:
    """Get seasonal statistics for a specific player."""
    if year is None:
        year = datetime.now().year
    
    async with await get_http_client() as client:
        try:
            response = await client.get(f"/en/players/{player_id}/seasons/{year}/statistics.json")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting seasonal stats for player {player_id}: {str(e)}")
            raise

@mcp.tool()
async def get_transactions(date_str: Optional[str] = None) -> Dict:
    """Get MLB transactions for a specific date or recent transactions."""
    async with await get_http_client() as client:
        try:
            if date_str:
                # Format: /en/league/{year}/{month}/{day}/transactions.json
                date_parts = date_str.split("-")
                year, month, day = date_parts[0], date_parts[1], date_parts[2]
                response = await client.get(f"/en/league/{year}/{month}/{day}/transactions.json")
            else:
                response = await client.get("/en/league/transactions.json")
            
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting transactions: {str(e)}")
            raise

@mcp.tool()
async def get_draft_summary(year: int) -> Dict:
    """Get MLB draft summary for a specific year."""
    async with await get_http_client() as client:
        try:
            response = await client.get(f"/en/league/drafts/{year}/summary.json")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting draft summary for {year}: {str(e)}")
            raise

@mcp.tool()
async def get_team_hierarchy() -> Dict:
    """Get complete MLB team hierarchy with divisions and leagues."""
    async with await get_http_client() as client:
        try:
            response = await client.get("/en/league/hierarchy.json")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting team hierarchy: {str(e)}")
            raise

@mcp.tool()
async def get_seasonal_splits(
    player_id: str,
    year: Optional[int] = None,
    split_type: Optional[str] = "home_away"
) -> Dict:
    """Get seasonal splits for a player (home/away, vs lefty/righty, etc.)."""
    if year is None:
        year = datetime.now().year
    
    async with await get_http_client() as client:
        try:
            response = await client.get(f"/en/players/{player_id}/seasons/{year}/splits.json")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting seasonal splits for player {player_id}: {str(e)}")
            raise

def main():
    """Main entry point for the MCP server."""
    logger.info("Starting MLB SportRadar MCP Server...")
    try:
        # API key check before starting the server
        if not SPORTRADAR_API_KEY:
            logger.error("SPORTRADAR_API_KEY environment variable is not set")
            print("SPORTRADAR_API_KEY environment variable is not set", file=sys.stderr)
            sys.exit(1)
            
        logger.info("API key found. Starting server...")
        mcp.run()
    except Exception as e:
        print(f"Failed to run server: {str(e)}", file=sys.stderr)
        raise

if __name__ == "__main__":
    main()