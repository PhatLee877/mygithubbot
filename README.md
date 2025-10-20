# Discord Bot - GitHub Config Manager

A Discord bot that manages configuration and syncs it to GitHub using slash commands.

## 🚀 Quick Start

The bot is already running! Use slash commands in Discord by typing `/` to see all available commands.

## 📝 Available Commands

All commands use the `/` prefix (slash commands):

### Configuration
- `/config` - Show current configuration
- `/price [value]` - View or update PRICE_LIMIT
- `/help` - Show all available commands

### Target Management
- `/targets` - List all target names with priorities
- `/addtarget <name> [priority]` - Add target at specified priority (default: 1, shifts others up)
- `/removetarget <priority>` - Remove target by priority number
- `/edittarget <priority> <new_name>` - Edit target name

### Display Names
- `/adddisplay <name>` - Add a display name
- `/removedisplay <name>` - Remove a display name

### Receivers
- `/addreceiver <name>` - Add a receiver
- `/removereceiver <name>` - Remove a receiver

### GitHub Sync
- `/push [message]` - Push current config to GitHub
- `/fetch` - Fetch config file from GitHub

## ⚙️ Configuration

The bot uses these environment secrets:
- `DISCORD_TOKEN` - Your Discord bot token (required)
- `GITHUB_TOKEN` - Your GitHub personal access token (required)

GitHub repository settings are in `bot_config_manager.py`:
- Repository: `PhatLee877/config`
- File path: `config`
- Branch: `main`

## 💡 How It Works

1. Make changes using Discord slash commands
2. **Changes automatically push to GitHub** - no manual sync needed!
3. Every modification is instantly committed with a descriptive message
4. Use `/push` for manual sync if needed
5. Use `/fetch` to download the current GitHub version

## 🛠️ Customization

Edit `bot_config_manager.py` to modify:
- GitHub repository settings
- Config structure
- Command behavior
- Authorization logic
