# Discord Bot - GitHub Config Manager

## Overview
A Discord bot that manages configuration data and pushes updates to a GitHub repository. The bot allows authorized users to modify config through Discord commands and commit changes to GitHub.

## Project Structure
- `bot_config_manager.py` - Main Discord bot with config management commands
- `main.py` - Original starter template (can be removed)
- `requirements.txt` - Python dependencies (discord.py, requests, python-dotenv)
- `README.md` - User documentation and examples

## Available Secrets
- DISCORD_TOKEN - Discord bot authentication token (required)
- GITHUB_TOKEN - GitHub API authentication token (required)
- SESSION_SECRET - For session management

## Recent Changes
- **2025-10-20**: Initial project setup with Python environment
- **2025-10-20**: Integrated Discord bot script for GitHub config management
- **2025-10-20**: Updated bot to use slash commands (/) instead of text commands (!)
- **2025-10-20**: Removed all authorization restrictions - everyone can use all commands
- **2025-10-20**: Implemented auto-push to GitHub - all changes sync automatically
- **2025-10-20**: Added underscore formatting for numbers (10_000_000)
- **2025-10-20**: Enhanced addtarget to accept custom priority - automatically shifts existing targets

## User Preferences
- User provided their own Discord bot script
- Prefers to code themselves with environment support

## Project Architecture
- Language: Python 3.11
- Main libraries: discord.py (Discord bot), requests (GitHub API), python-dotenv
- Runtime: Discord bot (long-running process)
- Bot Commands: !showconfig, !price, !listtargets, !addtarget, !removetarget, !edittarget, !adddisplayname, !removedisplayname, !addreceiver, !removereceiver, !pushconfig, !fetchconfig
- GitHub Integration: Pushes Lua config files to PhatLee877/config repository
