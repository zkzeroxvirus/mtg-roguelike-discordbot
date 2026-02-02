# MTG Roguelike Discord Bot

A Discord bot that automatically posts and updates player leaderboards from a Google Sheets spreadsheet. Designed for tracking MTG (Magic: The Gathering) Roguelike game progress with weighted scoring based on achievements, crypt buffs, tickets, and essence.

## Features

- 🏆 **Automated Leaderboard**: Automatically fetches player data from Google Sheets and posts ranked leaderboards
- 📊 **Weighted Scoring System**: Smart scoring that values achievements, crypt buffs, tickets, and essence
- 🔄 **Auto-Update**: Regularly refreshes leaderboard data at configurable intervals
- 💾 **Persistent Messages**: Edits existing messages instead of spamming new ones
- ⚡ **Rate Limit Compliant**: Built-in delays to respect Discord API rate limits
- 🎨 **Clean Display**: 
  - Top 10: Score + unlock counts (simplified, no individual names)
  - Ranks 11+: Score only for cleaner display
- 🐳 **Docker Support**: Easy deployment with Docker and Docker Compose

## Scoring System

The bot uses a weighted scoring formula to rank players:

- **Achievements**: 50,000 points each (hardest to obtain)
- **Crypt Buffs**: 5,000 points each (from defeating crypt bosses)
- **Tickets**: 500 points each (expensive investments)
- **Essence**: 1 point per essence

**Formula**: `Score = (Achievements × 50,000) + (Buffs × 5,000) + (Tickets × 500) + Essence`

## Prerequisites

- Python 3.11+ (for local setup)
- Docker and Docker Compose (for Docker setup)
- A Discord Bot Token
- A Google Sheets API service account
- Access to a Google Sheet with player data

## Quick Start (Unraid Docker - Recommended)

### Option 1: Using Unraid Template (Easiest)

1. **Download Required Files**
   - Download `service_account.json` from your Google Cloud Console (see below)
   - Create directory: `/mnt/user/appdata/mtg-discord-bot/`
   - Save `service_account.json` to that directory

2. **Add Template to Unraid**
   - Download the template file from: `https://raw.githubusercontent.com/zkzeroxvirus/mtg-roguelike-discordbot/main/unraid-template.xml`
   - Save it to `/boot/config/plugins/dockerMan/templates-user/` on your Unraid server
   - Open Unraid web interface and go to **Docker** tab
   - Click **Add Container** and select "MTG Roguelike Discord Bot" from the template dropdown
   - Fill in the required environment variables (see step 5 below)
   - Click **Apply**

3. **Set Up Google Sheets API** (if not done already)
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one
   - Enable the Google Sheets API
   - Create a service account and download the JSON credentials as `service_account.json`
   - Place the file in `/mnt/user/appdata/mtg-discord-bot/service_account.json`
   - Share your Google Sheet with the service account email (found in the JSON file)

4. **Create Discord Bot** (if not done already)
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Create a new application
   - Go to the "Bot" section and create a bot
   - Copy the bot token
   - Enable "Message Content Intent" in the bot settings
   - Invite the bot to your server with appropriate permissions (Send Messages, Embed Links, Read Message History, Manage Messages)

5. **Get Required IDs**

**Sheet ID:**
- From the URL: `https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID_HERE/edit`

**Channel ID:**
- Enable Developer Mode in Discord (User Settings > Advanced)
- Right-click on the channel and select "Copy ID"

6. **Start and Verify**
   - The container should start automatically
   - Check logs for any errors
   - Verify the bot appears online in Discord
   - Check that the leaderboard updates in the specified channel

### Option 2: Manual Installation via Unraid Web UI

1. **Download Required Files** (if not done already)
   - Download `service_account.json` from your Google Cloud Console (see Option 1, step 3)
   - Save it to a location on your Unraid server (e.g., `/mnt/user/appdata/mtg-discord-bot/`)

2. **Set Up Prerequisites** (if not done already)
   - Follow steps 3-5 from Option 1 above to set up Google Sheets API and Discord Bot

3. **Configure the Container**
   - Open Unraid web interface
   - Go to **Docker** tab
   - Click **Add Container**
   - Configure the following settings:

4. **Container Configuration Details**

**Container Settings:**
```
Name: mtg-roguelike-discord-bot
Repository: zkzeroxvirus/mtg-roguelike-discordbot:latest
(Or use: ghcr.io/zkzeroxvirus/mtg-roguelike-discordbot:latest)

Docker Hub URL: https://github.com/zkzeroxvirus/mtg-roguelike-discordbot
Icon URL: (Leave blank or use a Discord/Python icon URL of your choice)

Network Type: Bridge
Console shell command: Shell

Privileged: No
```

**Port Mappings:**
```
None required - this bot doesn't expose any ports
```

**Volume Mappings:**
```
Container Path: /app/data
Host Path: /mnt/user/appdata/mtg-discord-bot/data
Access Mode: Read/Write
Description: Persistent storage for message IDs

Container Path: /app/service_account.json
Host Path: /mnt/user/appdata/mtg-discord-bot/service_account.json
Access Mode: Read Only
Description: Google Sheets service account credentials
```

**Environment Variables:**
```
Key: DISCORD_TOKEN
Value: your_discord_bot_token_here
Description: Your Discord bot token

Key: SHEET_ID
Value: your_google_sheet_id_here
Description: Google Sheets spreadsheet ID

Key: LEADERBOARD_CHANNEL_ID
Value: your_channel_id_here
Description: Discord channel ID for leaderboard

Key: UPDATE_INTERVAL_SECONDS
Value: 300
Default: 300
Description: Update frequency in seconds (5 minutes)

Key: GOOGLE_APPLICATION_CREDENTIALS
Value: /app/service_account.json
Default: /app/service_account.json
Description: Path to service account JSON (leave as default)

Key: TZ
Value: UTC
Default: UTC
Description: Timezone (optional, e.g., America/New_York, Europe/London)
```

5. **Get Required IDs** (if not already obtained)

**Sheet ID:**
- From the URL: `https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID_HERE/edit`

**Channel ID:**
- Enable Developer Mode in Discord (User Settings > Advanced)
- Right-click on the channel and select "Copy ID"

6. **Start the Container**
   - Click **Apply** to create and start the container
   - View logs by clicking the container icon and selecting **Logs**

7. **Verify Installation**
   - Check the container logs for any errors
   - Verify the bot appears online in your Discord server
   - Check that the leaderboard updates in the specified channel

### Updating the Container in Unraid

To update to the latest version:
1. Go to **Docker** tab
2. Click **Check for Updates**
3. If an update is available, click **Update** next to the container
4. Or manually: Stop container > Force Update > Start container

---

## Alternative: Docker Compose Setup

### 1. Clone the Repository

```bash
git clone https://github.com/zkzeroxvirus/mtg-roguelike-discordbot.git
cd mtg-roguelike-discordbot
```

### 2. Set Up Google Sheets API (if not done already)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Sheets API
4. Create a service account and download the JSON credentials
5. Save the credentials as `service_account.json` in the project directory
6. Share your Google Sheet with the service account email (found in the JSON file)

### 3. Create Discord Bot (if not done already)

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to the "Bot" section and create a bot
4. Copy the bot token
5. Enable "Message Content Intent" in the bot settings
6. Invite the bot to your server with appropriate permissions (Send Messages, Embed Links, Read Message History, Manage Messages)

### 4. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and fill in your configuration:

```env
DISCORD_TOKEN=your_discord_bot_token_here
SHEET_ID=your_google_sheet_id_here
LEADERBOARD_CHANNEL_ID=your_channel_id_here
UPDATE_INTERVAL_SECONDS=300
```

**How to get the Sheet ID:**
- From the URL: `https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID_HERE/edit`

**How to get the Channel ID:**
- Enable Developer Mode in Discord (User Settings > Advanced)
- Right-click on the channel and select "Copy ID"

### 5. Run with Docker Compose

```bash
docker-compose up -d
```

To view logs:
```bash
docker-compose logs -f
```

To stop the bot:
```bash
docker-compose down
```

To rebuild after changes:
```bash
docker-compose up -d --build
```

## Local Setup (Alternative)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

```bash
export DISCORD_TOKEN="your_discord_bot_token"
export SHEET_ID="your_google_sheet_id"
export LEADERBOARD_CHANNEL_ID="your_channel_id"
export UPDATE_INTERVAL_SECONDS="300"
export GOOGLE_APPLICATION_CREDENTIALS="service_account.json"
```

### 3. Run the Bot

```bash
python bot.py
```

## Google Sheet Format

The bot expects your Google Sheet to have the following columns:

| Column | Name | Description |
|--------|------|-------------|
| B (2) | Player | Player name |
| C (3) | Essence | Current essence amount |
| F (6) | Achievements | Key:value pairs separated by `\|` (e.g., `ach1:1\|ach2:1`) |
| G (7) | Crypt Buffs | Key:value pairs separated by `\|` (e.g., `buff1:1\|buff2:1`) |
| H (8) | Tickets | Key:value pairs separated by `\|` (e.g., `ticket1:1\|ticket2:5`) |

Example row:
```
Player: JohnDoe
Essence: 12500
Achievements: legendary_deck:1|perfect_run:1
Crypt Buffs: boss_defeated:1|speed_buff:1
Tickets: rare_ticket:3|epic_ticket:1
```

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DISCORD_TOKEN` | Yes | - | Your Discord bot token |
| `SHEET_ID` | Yes | - | Google Sheets spreadsheet ID |
| `LEADERBOARD_CHANNEL_ID` | Yes | 0 | Discord channel ID for leaderboard |
| `UPDATE_INTERVAL_SECONDS` | No | 300 | Update frequency in seconds (5 minutes) |
| `GOOGLE_APPLICATION_CREDENTIALS` | No | service_account.json | Path to service account JSON |

### Customizing Weights

To adjust the scoring weights, edit the constants in `bot.py`:

```python
ACHIEVEMENT_WEIGHT = 50000  # Points per achievement
CRYPT_BUFF_WEIGHT = 5000    # Points per crypt buff
TICKET_WEIGHT = 500         # Points per ticket
```

### Customizing Rate Limits

The bot includes rate limiting delays to comply with Discord API requirements. You can adjust these in `bot.py` if needed:

```python
RATE_LIMIT_DELAY = 1.0       # Delay between message operations (seconds)
MESSAGE_EDIT_DELAY = 0.5     # Delay between consecutive edits (seconds)
```

**Note**: Discord allows approximately 5 messages per 5 seconds per channel. The default delays ensure compliance with these limits.

## Leaderboard Display

The bot creates multiple embed messages with a clean, easy-to-read format:

1. **Top 10 Players**: Shows score and count of each unlock type (achievements, crypt buffs, tickets)
   - Medal emojis for positions 1-3 (🥇🥈🥉)
   - Clean format: Score + unlock counts only
2. **Ranks 11-50**: Condensed view showing only player name and score
3. **Ranks 51+**: Additional condensed views in groups of 50, score only

The leaderboard refreshes automatically at the configured interval (default: 5 minutes).

### Rate Limiting

The bot implements Discord API best practices:
- 1 second delay between message posts
- 0.5 second delay between message edits
- Automatic delays to prevent rate limiting (429 errors)
- Built-in error handling and retry logic

## Troubleshooting

### Bot doesn't start
- Check that all environment variables are set correctly
- Verify your Discord token is valid
- Ensure the service account JSON file exists and is readable

### Leaderboard doesn't update
- Check that the bot has permissions in the channel
- Verify the channel ID is correct
- Look at the logs for error messages: `docker-compose logs -f`

### Google Sheets errors
- Ensure the service account has access to the sheet
- Verify the Sheet ID is correct
- Check that the sheet has the expected column structure

### Permission errors
The bot needs these Discord permissions:
- View Channels
- Send Messages
- Embed Links
- Read Message History
- Manage Messages (to edit its own messages)

## Data Persistence

The bot stores message IDs in `/app/data/message_ids.txt` to track which messages to update. When using Docker, this directory is mounted as a volume to persist data across container restarts.

## Development

### Running Tests

```bash
python -m py_compile bot.py
```

### Code Style

The codebase follows PEP 8 guidelines with:
- Clear function documentation
- Type hints for function parameters
- Descriptive variable names
- Consistent formatting

## Docker Commands Reference

```bash
# Build the image
docker-compose build

# Start the bot
docker-compose up -d

# View logs
docker-compose logs -f bot

# Stop the bot
docker-compose down

# Restart the bot
docker-compose restart

# Rebuild and restart
docker-compose up -d --build

# Remove everything including volumes
docker-compose down -v
```

## Security Notes

⚠️ **Important Security Practices:**

- Never commit your `.env` file or `service_account.json` to version control
- Keep your Discord bot token secret
- Regularly rotate your credentials
- Use environment variables for all sensitive data
- Restrict service account permissions to only what's needed

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Support

For issues, questions, or contributions, please open an issue on GitHub.

## Acknowledgments

Built for the MTG Roguelike community to track player progress and achievements.
