# bot_config_manager.py
# Discord bot để quản lý config và push lên GitHub
# Yêu cầu pip install: discord.py requests python-dotenv

import os
import base64
import requests
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

GH_OWNER = "PhatLee877"
GH_REPO = "config"
GH_PATH = "config"
GH_BRANCH = "main"

if not DISCORD_TOKEN or not GITHUB_TOKEN:
    raise SystemExit("Vui lòng đặt DISCORD_TOKEN và GITHUB_TOKEN trong env vars.")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents, help_command=None)

config = {
    "PRICE_LIMIT": 10_000_000,
    "WEBHOOK": "https://discord.com/api/webhooks/1410618016487444490/5Z5XqXUsfd7lFbxgXcCMMQqJDU_iGPc-h0AjLA09mqz-DRaIYpKP7aMVQhM6lm9oIgTv",
    "targetNames": [
        {"name": "Strawberry Elephant", "priority": 1},
        {"name": "Dragon Cannelloni", "priority": 2},
        {"name": "Spaghetti Tualetti", "priority": 3},
        {"name": "Garama and Madundung", "priority": 4},
        {"name": "Los Hotspotsitos", "priority": 5},
        {"name": "Los Bros", "priority": 6},
        {"name": "Ketchuru and Musturu", "priority": 7},
        {"name": "La Supreme Combinasion", "priority": 8},
        {"name": "Ketupat Kepat", "priority": 9},
        {"name": "Esok Sekolah", "priority": 10},
        {"name": "Los Nooo My Hotspotsitos", "priority": 11},
        {"name": "Nooo My Hotspot", "priority": 12},
        {"name": "Nuclearo Dinossauro", "priority": 13},
        {"name": "La Grande Combinasion", "priority": 14},
        {"name": "Los Combinasionas", "priority": 15},
        {"name": "Tacorita Bicicleta", "priority": 16},
        {"name": "Los Lucky Blocks", "priority": 17},
        {"name": "Secret Lucky Block", "priority": 18},
        {"name": "Admin Lucky Block", "priority": 19},
        {"name": "Taco Lucky Block", "priority": 20},
        {"name": "67", "priority": 21},
    ],
    "Displayname": ["Sweet", "phatle8117", "PhuBeo"],
    "Receiver": ["phatle8117", "ConCuTiHon02", "candyblossom1243", "bomaylatip", "banpetuytin1111", " banpetuytin11114", "banpetuytin11115", " banpetuytin111140"]
}

def reindex_priorities():
    config["targetNames"].sort(key=lambda x: x["priority"])
    for i, t in enumerate(config["targetNames"], start=1):
        t["priority"] = i

def add_target(name: str, priority: int = 1):
    for t in config["targetNames"]:
        if t["priority"] >= priority:
            t["priority"] += 1
    config["targetNames"].append({"name": name, "priority": priority})
    reindex_priorities()

def remove_target_by_priority(prio: int):
    removed = None
    for t in config["targetNames"]:
        if t["priority"] == prio:
            removed = t
            break
    if not removed:
        return None
    config["targetNames"].remove(removed)
    reindex_priorities()
    return removed

def edit_target(prio: int, new_name: str):
    for t in config["targetNames"]:
        if t["priority"] == prio:
            t["name"] = new_name
            return t
    return None

def lua_serialize_config(cfg: dict) -> str:
    lines = []
    lines.append("-- 🔗 Shared Config (by PhatLee)")
    lines.append("local config = {}")
    lines.append("")
    lines.append("-- ====== Giới hạn giá ======")
    lines.append(f"config.PRICE_LIMIT = {cfg['PRICE_LIMIT']:_}")
    lines.append("")
    lines.append(f'config.WEBHOOK = "{cfg["WEBHOOK"]}"')
    lines.append("")
    lines.append("-- ====== Target Names có ưu tiên ======")
    lines.append("config.targetNames = {")
    items = sorted(cfg["targetNames"], key=lambda x: x["priority"])
    for item in items:
        name = item["name"].replace('"', '\\"')
        pr = item["priority"]
        lines.append(f'    {{name = "{name}", priority = {pr}}},')
    lines.append("}")
    lines.append("")
    disp = ", ".join(f'"{d}"' for d in cfg["Displayname"])
    lines.append(f"config.Displayname = {{ {disp} }}")
    lines.append("")
    recv = ", ".join(f'"{r}"' for r in cfg["Receiver"])
    lines.append(f"config.Receiver = {{{recv}}}")
    lines.append("")
    lines.append("return config")
    return "\n".join(lines)

GITHUB_API_BASE = "https://api.github.com"

def gh_get_file_sha_and_content(owner, repo, path, branch="main"):
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/contents/{path}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    params = {"ref": branch}
    r = requests.get(url, headers=headers, params=params)
    if r.status_code == 200:
        j = r.json()
        return j.get("sha"), j.get("content"), j.get("encoding")
    return None, None, None

def gh_update_file(owner, repo, path, branch, new_content_str, sha, commit_message="Update config via bot"):
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/contents/{path}"
    b64 = base64.b64encode(new_content_str.encode("utf-8")).decode("utf-8")
    payload = {
        "message": commit_message,
        "content": b64,
        "sha": sha,
        "branch": branch
    }
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    r = requests.put(url, headers=headers, json=payload)
    return r

async def auto_push_to_github(username: str, action: str):
    """Automatically push config to GitHub after changes"""
    try:
        sha, content_b64, encoding = gh_get_file_sha_and_content(GH_OWNER, GH_REPO, GH_PATH, GH_BRANCH)
        if not sha:
            return False, "Could not fetch file from GitHub"
        
        new_lua = lua_serialize_config(config)
        msg = f"{action} by {username}"
        r = gh_update_file(GH_OWNER, GH_REPO, GH_PATH, GH_BRANCH, new_lua, sha, commit_message=msg)
        
        if r.status_code in (200, 201):
            return True, "Pushed to GitHub"
        else:
            return False, f"Failed: {r.status_code}"
    except Exception as e:
        return False, f"Error: {str(e)}"

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (id: {bot.user.id})")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands")
    except Exception as e:
        print(f"Failed to sync commands: {e}")
    print("Bot is ready. Use slash commands with /")

@bot.tree.command(name="config", description="📋 Show current configuration")
async def showconfig(interaction: discord.Interaction):
    
    lines = [f"**PRICE_LIMIT:** {config['PRICE_LIMIT']:_}", "", "**Target Names:**"]
    for t in sorted(config["targetNames"], key=lambda x: x["priority"]):
        lines.append(f"{t['priority']}. {t['name']}")
    lines.append("")
    lines.append("**Displayname:** " + ", ".join(config['Displayname']))
    lines.append("**Receiver:** " + ", ".join(config['Receiver']))
    
    full = "\n".join(lines)
    if len(full) > 1900:
        await interaction.response.send_message(
            "📋 Config is too large, sending as file...",
            file=discord.File(fp=discord.utils.io.BytesIO(full.encode("utf-8")), filename="config.txt")
        )
    else:
        await interaction.response.send_message(full)

@bot.tree.command(name="price", description="💰 View or update PRICE_LIMIT")
@app_commands.describe(value="New price limit (leave empty to view current)")
async def price(interaction: discord.Interaction, value: int = None):
    
    if value is None:
        return await interaction.response.send_message(f"💰 Current PRICE_LIMIT: **{config['PRICE_LIMIT']:_}**")
    
    config['PRICE_LIMIT'] = value
    await interaction.response.defer()
    
    success, msg = await auto_push_to_github(interaction.user.name, f"Updated PRICE_LIMIT to {value:_}")
    if success:
        await interaction.followup.send(f"✅ PRICE_LIMIT updated to **{config['PRICE_LIMIT']:_}**\n🚀 Auto-pushed to GitHub!")
    else:
        await interaction.followup.send(f"✅ PRICE_LIMIT updated to **{config['PRICE_LIMIT']:_}**\n⚠️ GitHub push failed: {msg}")

@bot.tree.command(name="targets", description="📝 List all target names with priorities")
async def listtargets(interaction: discord.Interaction):
    
    if not config['targetNames']:
        return await interaction.response.send_message("📝 No targets configured.")
    
    msg = "\n".join(f"`{t['priority']}.` {t['name']}" for t in sorted(config['targetNames'], key=lambda x: x['priority']))
    await interaction.response.send_message(f"**📝 Target Names:**\n{msg}")

@bot.tree.command(name="addtarget", description="➕ Add a new target at specified priority")
@app_commands.describe(name="Name of the target to add", priority="Priority position (default: 1, existing targets will shift up)")
async def addtarget(interaction: discord.Interaction, name: str, priority: int = 1):
    
    if priority < 1:
        return await interaction.response.send_message("❌ Priority must be 1 or higher")
    
    add_target(name, priority)
    await interaction.response.defer()
    
    success, msg = await auto_push_to_github(interaction.user.name, f"Added target '{name}' at priority {priority}")
    if success:
        await interaction.followup.send(f"✅ Added target **'{name}'** at priority {priority}\n📊 Existing targets at priority {priority}+ shifted up\n🚀 Auto-pushed to GitHub!")
    else:
        await interaction.followup.send(f"✅ Added target **'{name}'** at priority {priority}\n⚠️ GitHub push failed: {msg}")

@bot.tree.command(name="removetarget", description="❌ Remove a target by priority number")
@app_commands.describe(priority="Priority number of the target to remove")
async def removetarget(interaction: discord.Interaction, priority: int):
    
    removed = remove_target_by_priority(priority)
    if not removed:
        return await interaction.response.send_message(f"❌ No target found with priority {priority}")
    
    await interaction.response.defer()
    success, msg = await auto_push_to_github(interaction.user.name, f"Removed target '{removed['name']}'")
    if success:
        await interaction.followup.send(f"✅ Removed target **'{removed['name']}'**\n🚀 Auto-pushed to GitHub!")
    else:
        await interaction.followup.send(f"✅ Removed target **'{removed['name']}'**\n⚠️ GitHub push failed: {msg}")

@bot.tree.command(name="edittarget", description="✏️ Edit a target's name")
@app_commands.describe(priority="Priority number of the target", new_name="New name for the target")
async def edittarget(interaction: discord.Interaction, priority: int, new_name: str):
    
    edited = edit_target(priority, new_name)
    if not edited:
        return await interaction.response.send_message(f"❌ No target found with priority {priority}")
    
    await interaction.response.defer()
    success, msg = await auto_push_to_github(interaction.user.name, f"Edited target {priority} to '{new_name}'")
    if success:
        await interaction.followup.send(f"✅ Updated target {priority} to **'{new_name}'**\n🚀 Auto-pushed to GitHub!")
    else:
        await interaction.followup.send(f"✅ Updated target {priority} to **'{new_name}'**\n⚠️ GitHub push failed: {msg}")

@bot.tree.command(name="adddisplay", description="➕ Add a display name")
@app_commands.describe(name="Display name to add")
async def adddisplayname(interaction: discord.Interaction, name: str):
    
    if name in config['Displayname']:
        return await interaction.response.send_message(f"⚠️ '{name}' already exists in Displayname list.")
    
    config['Displayname'].append(name)
    await interaction.response.defer()
    
    success, msg = await auto_push_to_github(interaction.user.name, f"Added Displayname '{name}'")
    if success:
        await interaction.followup.send(f"✅ Added Displayname **'{name}'**\n🚀 Auto-pushed to GitHub!")
    else:
        await interaction.followup.send(f"✅ Added Displayname **'{name}'**\n⚠️ GitHub push failed: {msg}")

@bot.tree.command(name="removedisplay", description="❌ Remove a display name")
@app_commands.describe(name="Display name to remove")
async def removedisplayname(interaction: discord.Interaction, name: str):
    
    if name not in config['Displayname']:
        return await interaction.response.send_message(f"❌ '{name}' not found in Displayname list.")
    
    config['Displayname'].remove(name)
    await interaction.response.defer()
    
    success, msg = await auto_push_to_github(interaction.user.name, f"Removed Displayname '{name}'")
    if success:
        await interaction.followup.send(f"✅ Removed Displayname **'{name}'**\n🚀 Auto-pushed to GitHub!")
    else:
        await interaction.followup.send(f"✅ Removed Displayname **'{name}'**\n⚠️ GitHub push failed: {msg}")

@bot.tree.command(name="addreceiver", description="➕ Add a receiver name")
@app_commands.describe(name="Receiver name to add")
async def addreceiver(interaction: discord.Interaction, name: str):
    
    config['Receiver'].append(name)
    await interaction.response.defer()
    
    success, msg = await auto_push_to_github(interaction.user.name, f"Added Receiver '{name}'")
    if success:
        await interaction.followup.send(f"✅ Added Receiver **'{name}'**\n🚀 Auto-pushed to GitHub!")
    else:
        await interaction.followup.send(f"✅ Added Receiver **'{name}'**\n⚠️ GitHub push failed: {msg}")

@bot.tree.command(name="removereceiver", description="❌ Remove a receiver name")
@app_commands.describe(name="Receiver name to remove")
async def removereceiver(interaction: discord.Interaction, name: str):
    
    if name not in config['Receiver']:
        return await interaction.response.send_message(f"❌ '{name}' not found in Receiver list.")
    
    config['Receiver'].remove(name)
    await interaction.response.defer()
    
    success, msg = await auto_push_to_github(interaction.user.name, f"Removed Receiver '{name}'")
    if success:
        await interaction.followup.send(f"✅ Removed Receiver **'{name}'**\n🚀 Auto-pushed to GitHub!")
    else:
        await interaction.followup.send(f"✅ Removed Receiver **'{name}'**\n⚠️ GitHub push failed: {msg}")

@bot.tree.command(name="push", description="🚀 Push current config to GitHub")
@app_commands.describe(message="Custom commit message (optional)")
async def pushconfig(interaction: discord.Interaction, message: str = None):
    
    await interaction.response.defer()
    
    sha, content_b64, encoding = gh_get_file_sha_and_content(GH_OWNER, GH_REPO, GH_PATH, GH_BRANCH)
    if not sha:
        return await interaction.followup.send("❌ Could not fetch file from GitHub. Check repository path and permissions.")
    
    new_lua = lua_serialize_config(config)
    msg = message or f"Update config via Discord bot by {interaction.user.name}"
    r = gh_update_file(GH_OWNER, GH_REPO, GH_PATH, GH_BRANCH, new_lua, sha, commit_message=msg)
    
    if r.status_code in (200, 201):
        commit_url = r.json().get("commit", {}).get("html_url", "unknown")
        await interaction.followup.send(f"✅ **Config pushed successfully!**\n🔗 Commit: {commit_url}")
    else:
        await interaction.followup.send(f"❌ Failed to push config: {r.status_code}\n```{r.text[:500]}```")

@bot.tree.command(name="fetch", description="📥 Fetch current config from GitHub")
async def fetchconfig(interaction: discord.Interaction):
    
    await interaction.response.defer()
    
    sha, content_b64, encoding = gh_get_file_sha_and_content(GH_OWNER, GH_REPO, GH_PATH, GH_BRANCH)
    if not sha or not content_b64:
        return await interaction.followup.send("❌ Could not fetch file from GitHub.")
    
    try:
        decoded = base64.b64decode(content_b64).decode(encoding or "utf-8")
        await interaction.followup.send(
            "📥 **Fetched config from GitHub:**",
            file=discord.File(fp=discord.utils.io.BytesIO(decoded.encode("utf-8")), filename="remote_config.lua")
        )
    except Exception as e:
        await interaction.followup.send(f"❌ Error decoding content: {e}")

@bot.tree.command(name="help", description="❓ Show all available commands")
async def help_command(interaction: discord.Interaction):
    help_text = """
**🤖 Discord Config Manager Bot**

**Configuration:**
`/config` - Show current configuration
`/price [value]` - View or update PRICE_LIMIT

**Target Management:**
`/targets` - List all target names
`/addtarget <name>` - Add new target (priority 1)
`/removetarget <priority>` - Remove target by priority
`/edittarget <priority> <new_name>` - Edit target name

**Display Names:**
`/adddisplay <name>` - Add display name
`/removedisplay <name>` - Remove display name

**Receivers:**
`/addreceiver <name>` - Add receiver
`/removereceiver <name>` - Remove receiver

**GitHub Sync:**
`/push [message]` - Push config to GitHub
`/fetch` - Fetch config from GitHub

**Other:**
`/help` - Show this help message

💡 Changes are local until you use `/push` to commit to GitHub!
"""
    await interaction.response.send_message(help_text)

bot.run(DISCORD_TOKEN)
