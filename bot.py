import os
import asyncio
import logging
from typing import List, Dict, Any
import discord
from discord.ext import tasks
import gspread

logging.basicConfig(level=logging. INFO)
logger = logging.getLogger("leaderboard-bot")

# -------- Config from environment --------
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
SHEET_ID = os.environ.get("SHEET_ID")
GOOGLE_CREDS_PATH = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "service_account.json")

LEADERBOARD_CHANNEL_ID = int(os.environ.get("LEADERBOARD_CHANNEL_ID", "0"))
UPDATE_INTERVAL_SECONDS = int(os.environ.get("UPDATE_INTERVAL_SECONDS", "300"))

# Persistence file for message IDs
MESSAGE_IDS_FILE = "/app/data/message_ids.txt"

# Sheet columns (1-indexed)
COL_PLAYER = 2  # B
COL_ESSENCE = 3  # C
COL_ACHIEVEMENTS = 6  # F
COL_CRYPT_BUFFS = 7  # G
COL_TICKETS = 8  # H

# Weighted scoring (revised based on difficulty/cost)
ACHIEVEMENT_WEIGHT = 50000  # Hardest:  deck criteria + crypt win
CRYPT_BUFF_WEIGHT = 5000    # Hard: beat crypt boss
TICKET_WEIGHT = 500         # Expensive investment (1500-10000 Essence)

intents = discord.Intents. default()
intents.message_content = True
client = discord. Client(intents=intents)

message_ids:  List[int] = []

# -------- Persistence helpers --------
def load_message_ids():
    global message_ids
    try: 
        if os.path.exists(MESSAGE_IDS_FILE):
            with open(MESSAGE_IDS_FILE, "r") as f:
                content = f.read().strip()
                if content:
                    message_ids = [int(mid. strip()) for mid in content.split(",") if mid.strip()]
                    logger.info("Loaded %d message IDs from file:  %s", len(message_ids), message_ids)
    except Exception as e:
        logger.warning("Could not load message IDs from file: %s", e)

def save_message_ids():
    try:
        os.makedirs(os.path. dirname(MESSAGE_IDS_FILE), exist_ok=True)
        with open(MESSAGE_IDS_FILE, "w") as f:
            f.write(",". join(map(str, message_ids)))
        logger.info("Saved %d message IDs to file", len(message_ids))
    except Exception as e: 
        logger.warning("Could not save message IDs to file: %s", e)

# -------- Helpers --------
def truncate(text: str, limit: int = 950) -> str:
    return text if len(text) <= limit else text[:limit - 3] + "..."

def parse_kv_list(cell:  str) -> Dict[str, float]:
    result = {}
    if not cell:
        return result
    for part in str(cell).split("|"):
        if not part or ":" not in part:
            continue
        k, v = part.split(":", 1)
        try:
            result[k] = float(v)
        except ValueError:
            result[k] = 0
    return result

def format_name(raw_name: str) -> str:
    return raw_name.replace("_", " ").title()

def nonzero_names(d: Dict[str, float]) -> List[str]:
    return [format_name(k) for k, v in d.items() if v > 0]

def count_nonzero(d: Dict[str, float]) -> int:
    return sum(1 for v in d.values() if v > 0)

def sum_values(d: Dict[str, float]) -> float:
    return sum(d.values())

def describe_named_list(label: str, names: List[str], max_show: int = 8) -> str:
    count = len(names)
    if count == 0:
        return f"{label}:  0"
    if count <= max_show:
        return f"{label}: {count} — {', '.join(names)}"
    return f"{label}: {count} — {', '.join(names[:max_show])}, +{count - max_show} more"

def calculate_score(ach_count: int, buff_count: int, ticket_count: int, essence: float) -> float:
    """Calculate weighted score:  Achievements × 50,000 + Buffs × 5,000 + Tickets × 500 + Essence"""
    return (ach_count * ACHIEVEMENT_WEIGHT) + (buff_count * CRYPT_BUFF_WEIGHT) + (ticket_count * TICKET_WEIGHT) + essence

def build_leaderboard_rows(sheet) -> List[Dict[str, Any]]:
    data = sheet.get_all_values()
    if not data or len(data) < 2:
        return []

    rows = []
    for row in data[1:]: 
        def get(col_idx: int) -> str:
            return row[col_idx - 1] if len(row) >= col_idx else ""

        name = get(COL_PLAYER).strip()
        if not name:
            continue

        essence_raw = get(COL_ESSENCE)
        try:
            essence = float(essence_raw)
        except ValueError: 
            essence = 0

        achievements = parse_kv_list(get(COL_ACHIEVEMENTS))
        crypt_buffs = parse_kv_list(get(COL_CRYPT_BUFFS))
        tickets = parse_kv_list(get(COL_TICKETS))

        ach_count = count_nonzero(achievements)
        buff_count = count_nonzero(crypt_buffs)
        ticket_count = count_nonzero(tickets)
        total_unlocks = ach_count + buff_count + ticket_count

        score = calculate_score(ach_count, buff_count, ticket_count, essence)

        rows.append({
            "name": name,
            "essence": essence,
            "ach_dict": achievements,
            "buff_dict": crypt_buffs,
            "ticket_dict": tickets,
            "ach_count": ach_count,
            "buff_count":  buff_count,
            "ticket_count": ticket_count,
            "total_unlocks": total_unlocks,
            "tickets_total": sum_values(tickets),
            "score": score,
        })

    # Sort by weighted score (descending)
    rows.sort(key=lambda r: r["score"], reverse=True)
    return rows

def rank_display(i: int) -> str:
    if i == 1:
        return "🥇"
    elif i == 2:
        return "🥈"
    elif i == 3:
        return "🥉"
    else:
        return f"{i}."

def format_detailed_entry(idx: int, r: Dict[str, Any]) -> str:
    ach_names = nonzero_names(r["ach_dict"])
    buff_names = nonzero_names(r["buff_dict"])
    ticket_names = nonzero_names(r["ticket_dict"])
    return (
        f"**Score:  {r['score']: ,.0f}** ({r['essence']:.0f} Essence | {r['total_unlocks']} Unlocks)\n"
        f"🏆 {describe_named_list('Achievements', ach_names)}\n"
        f"🗝️ {describe_named_list('Crypt Buffs', buff_names)}\n"
        f"🎟️ {describe_named_list('Tickets', ticket_names)}"
    )

def format_condensed_entry(idx: int, r: Dict[str, Any]) -> str:
    return f"{idx}. **{r['name']}** — Score: {r['score']:,.0f} ({r['ach_count']} Ach | {r['buff_count']} Buffs | {r['ticket_count']} Tix | {r['essence']:.0f} Ess)"

def chunk_lines_by_chars(lines: List[str], max_chars: int = 950) -> List[List[str]]:
    chunks = []
    current = []
    length = 0
    for line in lines:
        add = line + "\n"
        if current and length + len(add) > max_chars:
            chunks. append(current)
            current = []
            length = 0
        current.append(line)
        length += len(add)
    if current:
        chunks.append(current)
    return chunks

def build_embeds(rows: List[Dict[str, Any]]) -> List[discord.Embed]:
    embeds = []

    if not rows:
        embed = discord.Embed(
            title="📊 Player Records",
            description="No player data available.",
            color=0xFF9800,
        )
        return [embed]

    # Post 1: Top 10 detailed, each as its own field
    top_10 = rows[:10]
    if top_10:
        embed1 = discord.Embed(
            title="📊 Player Records — Top 10",
            description=f"Ranked by weighted score:  Achievements (×{ACHIEVEMENT_WEIGHT: ,}) + Buffs (×{CRYPT_BUFF_WEIGHT:,}) + Tickets (×{TICKET_WEIGHT}) + Essence\nRefreshes every {UPDATE_INTERVAL_SECONDS // 60} min",
            color=0xFFD700,
        )
        for idx, r in enumerate(top_10, start=1):
            field_name = f"{rank_display(idx)} {r['name']}"
            field_value = truncate(format_detailed_entry(idx, r), 950)
            embed1.add_field(name=field_name, value=field_value, inline=False)
        embeds.append(embed1)

    # Post 2: Ranks 11-50 condensed, chunked
    ranks_11_50 = rows[10:50]
    if ranks_11_50:
        lines = [format_condensed_entry(i + 11, r) for i, r in enumerate(ranks_11_50)]
        for chunk_idx, chunk in enumerate(chunk_lines_by_chars(lines), start=1):
            embed = discord.Embed(
                title="📊 Player Records — Ranks 11-50" + (f" (part {chunk_idx})" if chunk_idx > 1 else ""),
                color=0xC0C0C0,
            )
            embed.add_field(name="Rankings", value="\n".join(chunk), inline=False)
            embeds.append(embed)

    # Post 3+: Ranks 51-100, 101-150, etc., chunked
    remaining = rows[50:]
    logical_group_size = 50
    for group_start in range(0, len(remaining), logical_group_size):
        group = remaining[group_start:  group_start + logical_group_size]
        start_rank = 51 + group_start
        end_rank = start_rank + len(group) - 1
        lines = [format_condensed_entry(start_rank + i, r) for i, r in enumerate(group)]
        for chunk_idx, chunk in enumerate(chunk_lines_by_chars(lines), start=1):
            embed = discord. Embed(
                title=f"📊 Player Records — Ranks {start_rank}-{end_rank}" + (f" (part {chunk_idx})" if chunk_idx > 1 else ""),
                color=0xCD7F32,
            )
            embed.add_field(name="Rankings", value="\n".join(chunk), inline=False)
            embeds.append(embed)

    return embeds

# -------- Google Sheets client --------
def get_sheet_client():
    gc = gspread.service_account(filename=GOOGLE_CREDS_PATH)
    sh = gc.open_by_key(SHEET_ID)
    return sh. sheet1

# -------- Post/update leaderboard logic --------
async def post_or_update_leaderboard():
    global message_ids
    channel = client.get_channel(LEADERBOARD_CHANNEL_ID)
    if channel is None:
        logger.error("Channel not found.  Check LEADERBOARD_CHANNEL_ID.")
        return

    try:
        sheet = get_sheet_client()
        rows = build_leaderboard_rows(sheet)
        embeds = build_embeds(rows)
    except Exception as e:
        logger.exception("Failed to build leaderboard:  %s", e)
        return

    ids_changed = False

    # Ensure enough messages
    while len(message_ids) < len(embeds):
        try:
            msg = await channel.send(embed=embeds[len(message_ids)])
            message_ids. append(msg.id)
            logger.info("Posted new leaderboard message %d.  MESSAGE_ID=%s", len(message_ids), msg.id)
            ids_changed = True
        except Exception as e:
            logger. exception("Failed to post new leaderboard message: %s", e)
            return

    # Update existing
    for i, embed in enumerate(embeds):
        if i < len(message_ids):
            try:
                msg = await channel.fetch_message(message_ids[i])
                await msg.edit(embed=embed)
                logger.info("Updated leaderboard message %d (%s)", i + 1, message_ids[i])
            except Exception as e:
                logger.warning("Could not edit message %s: %s", message_ids[i], e)

    # Delete extras
    if len(message_ids) > len(embeds):
        for mid in message_ids[len(embeds):]:
            try: 
                msg = await channel.fetch_message(mid)
                await msg.delete()
                logger. info("Deleted extra leaderboard message %s", mid)
            except Exception as e:
                logger.warning("Could not delete message %s: %s", mid, e)
        message_ids = message_ids[: len(embeds)]
        ids_changed = True

    if ids_changed:
        save_message_ids()

    logger.info("All message IDs: %s", ",".join(map(str, message_ids)))

# -------- Discord tasks --------
@tasks.loop(seconds=UPDATE_INTERVAL_SECONDS)
async def update_leaderboard():
    await post_or_update_leaderboard()

@client.event
async def on_ready():
    logger.info("Bot logged in as %s", client.user)
    if LEADERBOARD_CHANNEL_ID == 0:
        logger.error("LEADERBOARD_CHANNEL_ID not set.")
        return

    load_message_ids()
    await post_or_update_leaderboard()

    if not update_leaderboard. is_running():
        update_leaderboard.start()

if __name__ == "__main__": 
    if not DISCORD_TOKEN:
        raise SystemExit("DISCORD_TOKEN is required")
    if not SHEET_ID: 
        raise SystemExit("SHEET_ID is required")
    client.run(DISCORD_TOKEN)