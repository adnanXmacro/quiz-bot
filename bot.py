import discord
from discord.ext import commands
import json
import os
import random
import asyncio
import datetime
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=4)

# âââ CONFIG ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
DISCORD_TOKEN         = os.environ.get("DISCORD_TOKEN")
CHANNEL_ID            = int(os.environ.get("CHANNEL_ID", "1493121034226761758"))
GIST_TOKEN            = os.environ.get("GIST_TOKEN")
GIST_ID               = os.environ.get("GIST_ID")
QUESTIONS_PER_SESSION = 0
ALIVE_MINUTES         = 1
PERSONAL_TIMER_MIN    = 1
# ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

# âââ QUESTION BANK ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
# â¼â¼â¼ PASTE YOUR QUESTIONS HERE â replace the placeholder below â¼â¼â¼
QUESTION_BANK = [
    {"type":"mcq","subject":"Biology","question":"à¦¨à¦¿à¦à§à¦° à¦à§à¦¨à¦à¦¿à¦¤à§ à¦¹à¦¾à¦à¦¡à§à¦°à¦¾à¦° à¦¬à¦¹à¦¿à¦à¦à§à¦·à§à¦¯à¦¼ à¦ªà¦°à¦¿à¦ªà¦¾à¦ à¦¸à¦à¦à¦à¦¿à¦¤ à¦¹à¦¯à¦¼?","options":{"A":"à¦à§à¦¯à¦¾à¦¸à§à¦à§à¦°à§à¦¡à¦¾à¦°à§à¦®à¦¿à¦¸","B":"à¦¹à¦¾à¦à¦ªà§à¦¸à§à¦à§à¦®","C":"à¦¸à¦¿à¦²à§à¦¨à§à¦à§à¦°à¦¨","D":"à¦à¦°à§à¦·à¦¿à¦à¦¾"},"answer":"C","explanation":"à¦¹à¦¾à¦à¦¡à§à¦°à¦¾à¦° à¦¸à¦¿à¦²à§à¦¨à§à¦à§à¦°à¦¨à§ à¦¬à¦¹à¦¿à¦à¦à§à¦·à§à¦¯à¦¼ à¦ªà¦°à¦¿à¦ªà¦¾à¦ à¦à¦à§à¥¤"},
    {"type":"mcq","subject":"Biology","question":"à¦à§à¦· à¦¬à¦¿à¦­à¦¾à¦à¦¨à§à¦° à¦¸à¦®à¦¯à¦¼ à¦à§à¦·à¦ªà§à¦²à§à¦ à¦¤à§à¦°à¦¿à¦¤à§ à¦¸à¦¾à¦¹à¦¾à¦¯à§à¦¯ à¦à¦°à§ à¦à§à¦¨ à¦à¦à§à¦à¦¾à¦£à§?","options":{"A":"à¦²à¦¾à¦à¦¸à§à¦¸à§à¦®","B":"à¦à¦²à¦à¦¿ à¦¬à¦¸à§à¦¤à§","C":"à¦®à¦¾à¦à¦à§à¦à¦¨à§à¦¡à§à¦°à¦¿à¦¯à¦¼à¦¾","D":"à¦°à¦¾à¦à¦¬à§à¦¸à§à¦®"},"answer":"B","explanation":"à¦à¦²à¦à¦¿ à¦¬à¦¸à§à¦¤à§ à¦à§à¦· à¦¬à¦¿à¦­à¦¾à¦à¦¨à§à¦° à¦¸à¦®à¦¯à¦¼ à¦à§à¦·à¦ªà§à¦²à§à¦ à¦à¦ à¦¨à§ à¦¸à¦¾à¦¹à¦¾à¦¯à§à¦¯ à¦à¦°à§à¥¤"},
    {"type":"mcq","subject":"Biology","question":"à¦°à§à¦¸à§à¦à§à¦°à¦¿à¦à¦¶à¦¨ à¦à¦¨à¦à¦¾à¦à¦®à§à¦° à¦à¦¾à¦ à¦à§?","options":{"A":"DNA à¦à¦£à§ à¦¬à§à¦¦à§à¦§à¦¿à¦à¦°à¦£","B":"DNA à¦à¦£à§à¦¡à¦à§ à¦à§à¦¡à¦¼à¦¾ à¦²à¦¾à¦à¦¾à¦¨à§","C":"à¦¨à¦¿à¦°à§à¦¦à¦¿à¦·à§à¦ à¦à§à¦¬à§ à¦°à¦¿à¦à¦®à§à¦¬à¦¿à¦¨à§à¦¨à§à¦ DNA à¦ªà§à¦°à¦¬à§à¦¶ à¦à¦°à¦¾à¦¨à§","D":"à¦à¦¾à¦à§à¦à§à¦·à¦¿à¦¤ DNA à¦à§ à¦¨à¦¿à¦°à§à¦¦à¦¿à¦·à§à¦ à¦¸à§à¦¥à¦¾à¦¨à§ à¦à§à¦¦à¦¨ à¦à¦°à¦¾"},"answer":"D","explanation":"à¦°à§à¦¸à§à¦à§à¦°à¦¿à¦à¦¶à¦¨ à¦à¦¨à¦à¦¾à¦à¦® à¦¨à¦¿à¦°à§à¦¦à¦¿à¦·à§à¦ à¦¸à§à¦¥à¦¾à¦¨à§ DNA à¦à§à¦¦à¦¨ à¦à¦°à§à¥¤"},
    {"type":"mcq","subject":"Chemistry","question":"18Â°C à¦¤à¦¾à¦ªà¦®à¦¾à¦¤à§à¦°à¦¾à¦¯à¦¼ 0.8 atm à¦à¦¾à¦ªà§ à¦à¦à¦à¦¿ à¦à§à¦¯à¦¾à¦¸à§à¦° à¦à¦¨à¦¤à§à¦¬ 2.25 gLâ»Â¹ à¦¹à¦²à§ à¦à¦£à¦¬à¦¿à¦ à¦­à¦° à¦à¦¤?","options":{"A":"36.63 g molâ»Â¹","B":"36.24 g molâ»Â¹","C":"24.36 g molâ»Â¹","D":"67.11 g molâ»Â¹"},"answer":"A","explanation":"PV=nRT à¦¬à§à¦¯à¦¬à¦¹à¦¾à¦° à¦à¦°à§ M = dRT/P â 36.63 g/mol"},
    {"type":"mcq","subject":"Chemistry","question":"à¦à§à¦¨ à¦¦à§à¦°à¦¬à¦£à§à¦° OHâ» à¦à¦¯à¦¼à¦¨à§à¦° à¦à¦¨à¦®à¦¾à¦¤à§à¦°à¦¾ 3.5Ã10â»â´ M à¦¹à¦²à§ pH à¦à¦¤?","options":{"A":"12.50","B":"13.55","C":"10.54","D":"3.55"},"answer":"C","explanation":"pOH = -log(3.5Ã10â»â´) â 3.46; pH = 14-3.46 = 10.54"},
    {"type":"mcq","subject":"Physics","question":"à¦«à§à¦à¦¾à¦¸ à¦¦à§à¦°à¦¤à§à¦¬ 1000 cm à¦¹à¦²à§ à¦à¦¤à§à¦¤à¦² à¦²à§à¦¨à§à¦¸à§à¦° à¦à§à¦·à¦®à¦¤à¦¾ à¦à¦¤?","options":{"A":"+10 D","B":"+100 D","C":"+0.1 D","D":"-0.1 D"},"answer":"C","explanation":"P = 1/f(m) = 1/10 = +0.1 D"},
    {"type":"mcq","subject":"Physics","question":"à¦¦à§à¦à¦¿ à¦­à§à¦à§à¦à¦° 8 à¦ 6 à¦à¦à¦, 30Â° à¦à§à¦£à§ à¦à§à¦°à¦¿à¦¯à¦¼à¦¾à¦¶à§à¦² à¦¹à¦²à§ à¦­à§à¦à§à¦à¦° à¦à§à¦£à¦«à¦² à¦à¦¤?","options":{"A":"16","B":"20","C":"48","D":"24"},"answer":"D","explanation":"AÃB = |A||B|sinÎ¸ = 8Ã6Ãsin30Â° = 24"},
    {"type":"mcq","subject":"English","question":"Synonym of 'anarchy'â","options":{"A":"serenity","B":"placidity","C":"lawlessness","D":"discipline"},"answer":"C","explanation":"Anarchy = a state of disorder/lawlessness."},
    {"type":"mcq","subject":"GK","question":"à¦¬à¦¾à¦à¦²à¦¾à¦¦à§à¦¶à§à¦° à§§à§¦à§¦ à¦à¦¾à¦à¦¾à¦° à¦¨à§à¦à§ à¦à§à¦¨ à¦®à¦¸à¦à¦¿à¦¦à§à¦° à¦à¦¬à¦¿ à¦à¦à§?","options":{"A":"à¦®à¦¡à§à¦² à¦®à¦¸à¦à¦¿à¦¦","B":"à¦·à¦¾à¦ à¦à¦®à§à¦¬à§à¦ à¦®à¦¸à¦à¦¿à¦¦","C":"à¦à¦¤à¦¿à¦¯à¦¼à¦¾ à¦®à¦¸à¦à¦¿à¦¦","D":"à¦¤à¦¾à¦°à¦¾ à¦®à¦¸à¦à¦¿à¦¦"},"answer":"B","explanation":"à§§à§¦à§¦ à¦à¦¾à¦à¦¾à¦° à¦¨à§à¦à§ à¦·à¦¾à¦ à¦à¦®à§à¦¬à§à¦ à¦®à¦¸à¦à¦¿à¦¦à¥¤"},
    {"type":"mcq","subject":"GK","question":"WHO à¦à¦¾à¦²à¦¾à¦à§à¦¬à¦°à¦®à§à¦à§à¦¤ à¦¦à§à¦¶ à¦¹à¦¿à¦¸à§à¦¬à§ à¦¬à¦¾à¦à¦²à¦¾à¦¦à§à¦¶à¦à§ à¦¸à§à¦¬à§à¦à§à¦¤à¦¿ à¦¦à§à¦¯à¦¼ à¦à¦¬à§?","options":{"A":"à§©à§¦ à¦¸à§à¦ªà§à¦à§à¦®à§à¦¬à¦° à§¨à§¦à§¨à§©","B":"à§©à§§ à¦à¦à§à¦à§à¦¬à¦° à§¨à§¦à§¨à§©","C":"à§¦à§§ à¦¨à¦­à§à¦®à§à¦¬à¦° à§¨à§¦à§¨à§©","D":"à§©à§¦ à¦¨à¦­à§à¦®à§à¦¬à¦° à§¨à§¦à§¨à§©"},"answer":"B","explanation":"à§©à§§ à¦à¦à§à¦à§à¦¬à¦° à§¨à§¦à§¨à§© à¦¸à¦¾à¦²à§ WHO à¦à¦ à¦¸à§à¦¬à§à¦à§à¦¤à¦¿ à¦¦à§à¦¯à¦¼à¥¤"},
    {"type":"mcq","subject":"Math","question":"à¦à§à¦¨ à¦¤à¦¾à¦ªà¦®à¦¾à¦¤à§à¦°à¦¾à¦¯à¦¼ à¦¸à§à¦²à¦¸à¦¿à¦¯à¦¼à¦¾à¦¸ à¦ à¦«à¦¾à¦°à§à¦¨à¦¹à¦¾à¦à¦ à¦à¦à¦ à¦®à¦¾à¦¨ à¦¦à§à¦à¦¾à¦¯à¦¼?","options":{"A":"-40Â°","B":"32Â°","C":"40Â°","D":"-32Â°"},"answer":"A","explanation":"C=F à¦¹à¦²à§, C = 9C/5+32 â C = -40Â°"},
    {"type":"mcq","subject":"Biology","question":"à¦¹à¦¿à¦®à§à¦à§à¦²à§à¦¬à¦¿à¦¨à§à¦° à¦à§à¦¨ à¦à¦à¦¶à§ COâ à¦¯à§à¦à§à¦¤ à¦¹à¦¯à¦¼?","options":{"A":"âOH","B":"âCOOH","C":"âHCOâ","D":"âNHâ"},"answer":"D","explanation":"COâ, à¦¹à¦¿à¦®à§à¦à§à¦²à§à¦¬à¦¿à¦¨à§à¦° âNHâ à¦à§à¦°à§à¦ªà§à¦° à¦¸à¦¾à¦¥à§ à¦¯à§à¦à§à¦¤ à¦¹à¦¯à¦¼à¥¤"},
]
# â²â²â² END OF QUESTION BANK â²â²â²
# ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ


# âââ GIST DATA STORAGE ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
# Saves to Gist on every answer using a lock to prevent 409 conflicts.

SESSION_DATA = {"scores": {}, "asked": [], "streaks": {}, "session_count": 0}
_save_lock   = None  # asyncio.Lock â initialized in on_ready

def _load_data_sync() -> dict:
    try:
        req = urllib.request.Request(
            f"https://api.github.com/gists/{GIST_ID}",
            headers={"Authorization": f"token {GIST_TOKEN}", "Accept": "application/vnd.github.v3+json"}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            raw  = json.loads(data["files"]["scores.json"]["content"])
            if "scores" not in raw:
                return {"scores": raw, "asked": [], "streaks": {}, "session_count": 0}
            raw.setdefault("session_count", 0)
            return raw
    except Exception as e:
        print(f"Gist load error: {e}")
        return {"scores": {}, "asked": [], "streaks": {}, "session_count": 0}

def _save_data_sync(data: dict) -> bool:
    try:
        payload = json.dumps({
            "files": {"scores.json": {"content": json.dumps(data, ensure_ascii=False, indent=2)}}
        }).encode("utf-8")
        req = urllib.request.Request(
            f"https://api.github.com/gists/{GIST_ID}",
            data=payload,
            headers={"Authorization": f"token {GIST_TOKEN}", "Accept": "application/vnd.github.v3+json", "Content-Type": "application/json"},
            method="PATCH"
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            print(f"Gist saved. Players: {len(data.get('scores', {}))}")
            return True
    except Exception as e:
        print(f"Gist save error: {e}")
        return False

async def load_session_data():
    global SESSION_DATA
    if not GIST_TOKEN or not GIST_ID:
        return
    data = await asyncio.get_event_loop().run_in_executor(executor, _load_data_sync)
    SESSION_DATA = data
    print(f"Loaded. Players: {len(data.get('scores', {}))}, Asked: {len(data.get('asked', []))}")

async def save_to_gist():
    """Save to Gist â queued via lock so only one write at a time, no 409."""
    if not GIST_TOKEN or not GIST_ID or _save_lock is None:
        return
    async with _save_lock:
        await asyncio.get_event_loop().run_in_executor(executor, _save_data_sync, SESSION_DATA)

async def save_session_data():
    await save_to_gist()

def update_score_sync(user_id: str, username: str, correct: bool,
                      subject: str = "General", points_to_add: int = 10) -> int:
    scores  = SESSION_DATA.setdefault("scores", {})
    streaks = SESSION_DATA.setdefault("streaks", {})
    today   = (datetime.datetime.utcnow() + datetime.timedelta(hours=6)).strftime("%Y-%m-%d")

    if user_id not in scores:
        scores[user_id] = {"username": username, "points": 0, "correct": 0,
                           "total": 0, "subjects": {}}
    s = scores[user_id]
    s["username"] = username
    s["total"]    += 1
    s.setdefault("subjects", {})
    s["subjects"].setdefault(subject, {"correct": 0, "total": 0})
    s["subjects"][subject]["total"] += 1

    if correct:
        s["points"]  += points_to_add
        s["correct"] += 1
        s["subjects"][subject]["correct"] += 1

    if user_id not in streaks:
        streaks[user_id] = {"streak": 0, "last_date": ""}
    st = streaks[user_id]
    if st["last_date"] != today:
        yesterday = (datetime.datetime.utcnow() + datetime.timedelta(hours=6)
                     - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        st["streak"] = st["streak"] + 1 if st["last_date"] == yesterday else 1
        st["last_date"] = today

    return s["points"]

def get_streak_badge(streak: int) -> str:
    if streak >= 14: return "ð¥ð¥ð¥"
    elif streak >= 7: return "ð¥ð¥"
    elif streak >= 3: return "ð¥"
    return ""

async def update_score(user_id: str, username: str, correct: bool,
                       subject: str = "General", points_to_add: int = 10) -> int:
    """Update memory AND save to Gist immediately (queued)."""
    pts = update_score_sync(user_id, username, correct, subject, points_to_add)
    await save_to_gist()
    return pts

async def load_scores() -> dict:
    return SESSION_DATA.get("scores", {})


# âââ UI HELPERS âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

SUBJECT_META = {
    "Physics":   {"emoji": "â¡", "color": 0x5865F2, "label": "Physics"},
    "Chemistry": {"emoji": "âï¸",  "color": 0xED4245, "label": "Chemistry"},
    "Math":      {"emoji": "ð", "color": 0x57F287, "label": "Mathematics"},
    "Biology":   {"emoji": "ð¬", "color": 0xFEE75C, "label": "Biology"},
    "English":   {"emoji": "ð", "color": 0x00B4FF, "label": "English"},
    "GK":        {"emoji": "ð", "color": 0xFF8C00, "label": "General Knowledge"},
}

def get_subject(subject: str) -> dict:
    return SUBJECT_META.get(subject, {"emoji": "ð", "color": 0x5865F2, "label": subject})

def get_rank(points: int) -> tuple:
    """Returns (badge_emoji, title, color_hex)"""
    if points >= 1000: return ("ð", "ELITE",      0xA8D8EA)
    elif points >= 500: return ("ð", "LEGEND",     0xFFD700)
    elif points >= 200: return ("ð¥", "CHAMPION",   0xFF6B35)
    elif points >= 100: return ("â¡", "SCHOLAR",    0x5865F2)
    elif points >= 50:  return ("ð", "APPRENTICE", 0x57F287)
    return                     ("ð±", "ROOKIE",     0x99AAB5)

SESSIONS_PER_CYCLE = 10  # Scoreboard resets every 10 sessions

def build_scoreboard_embed(scores: dict, streaks: dict = None, session_count: int = 0) -> discord.Embed:
    now_bd   = datetime.datetime.utcnow() + datetime.timedelta(hours=6)
    streaks  = streaks or {}
    sessions_left = SESSIONS_PER_CYCLE - (session_count % SESSIONS_PER_CYCLE)
    cycle_num     = (session_count // SESSIONS_PER_CYCLE) + 1

    if not scores:
        embed = discord.Embed(
            title="ð  Leaderboard",
            description=(
                f"No participants yet.\n\n"
                f"**Cycle #{cycle_num}**  Â·  Session `{session_count % SESSIONS_PER_CYCLE}/{SESSIONS_PER_CYCLE}`\n"
                f"Resets in `{sessions_left}` sessions."
            ),
            color=0x2B2D31,
            timestamp=datetime.datetime.utcnow()
        )
        return embed

    sorted_scores = sorted(scores.values(), key=lambda x: x["points"], reverse=True)
    max_pts = max(s["points"] for s in sorted_scores) or 1
    id_map  = {v["username"]: k for k, v in scores.items()}

    embed = discord.Embed(
        title=f"ð  Leaderboard  Â·  {now_bd.strftime('%d %B %Y')}",
        color=0xFFD700,
        timestamp=datetime.datetime.utcnow()
    )

    # Cycle progress bar
    filled_cycle = round(((session_count % SESSIONS_PER_CYCLE) / SESSIONS_PER_CYCLE) * 10)
    cycle_bar    = "â" * filled_cycle + "â" * (10 - filled_cycle)
    embed.description = (
        f"**Cycle #{cycle_num}**  `{cycle_bar}`  "
        f"Session **{session_count % SESSIONS_PER_CYCLE}/{SESSIONS_PER_CYCLE}**"
        f"  Â·  Resets in `{sessions_left}` sessions"
    )

    # Podium top 3 with ties â same score = same rank, next rank = rank+1 (not skipped)
    rank      = 0
    prev_pts  = None
    podium_lines = []
    rest_lines   = []
    podium_icons = ["ð¥", "ð¥", "ð¥"]

    for i, s in enumerate(sorted_scores[:10]):
        if s["points"] != prev_pts:
            rank     = rank + 1  # only increment rank when score changes
        prev_pts = s["points"]

        acc    = round(100 * s["correct"] / s["total"]) if s["total"] > 0 else 0
        badge, title, _ = get_rank(s["points"])
        uid    = id_map.get(s["username"], "")
        streak = streaks.get(uid, {}).get("streak", 0)
        sb     = get_streak_badge(streak)
        st     = f" {sb}`{streak}d`" if streak >= 3 else ""

        if rank <= 3:
            icon = podium_icons[rank - 1]
            podium_lines.append(
                f"{icon} **{s['username']}**  {badge} {title}{st}\n"
                f"ã`{s['points']} pts`  Â·  **{acc}%** accuracy  Â·  {s['correct']}/{s['total']} â"
            )
        else:
            filled = round((s["points"] / max_pts) * 10)
            bar    = "â°" * filled + "â±" * (10 - filled)
            rest_lines.append(
                f"`#{rank:02d}` **{s['username'][:14]}**  {bar}  `{s['points']} pts`  Â·  {acc}%{st}"
            )

    if podium_lines:
        embed.add_field(name="ð Podium", value="\n\n".join(podium_lines), inline=False)
    if rest_lines:
        embed.add_field(name="ð Rankings", value="\n".join(rest_lines), inline=False)

    # Session stats
    total_p = len(sorted_scores)
    total_a = sum(s["total"] for s in sorted_scores)
    avg_acc = round(sum(
        100 * s["correct"] / s["total"] for s in sorted_scores if s["total"] > 0
    ) / max(total_p, 1))

    embed.add_field(
        name="ð This Session",
        value=f"`{total_p}` players  Â·  `{total_a}` answers  Â·  `{avg_acc}%` avg accuracy",
        inline=False
    )
    embed.set_footer(text="ð¥3d Â· ð¥ð¥7d Â· ð¥ð¥ð¥14d  |  ð1000 Â· ð500 Â· ð¥200 Â· â¡100 Â· ð50 Â· ð±0")
    return embed


# âââ QUESTION PICKER ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

async def pick_questions_smart(count: int) -> list:
    """Pick questions avoiding recently asked ones, using in-memory SESSION_DATA."""
    asked = set(SESSION_DATA.get("asked", []))

    if os.path.exists("questions.json"):
        try:
            with open("questions.json", "r", encoding="utf-8") as f:
                raw_pool = json.load(f)
            for q in raw_pool:
                q.setdefault("type", "mcq")
                q.setdefault("subject", "General")
            # Deduplicate by question text
            seen = set()
            pool = []
            for q in raw_pool:
                if q["question"] not in seen:
                    seen.add(q["question"])
                    pool.append(q)
            dupes = len(raw_pool) - len(pool)
            if dupes > 0:
                print(f"Removed {dupes} duplicate questions. Unique: {len(pool)}")
            else:
                print(f"Loaded {len(pool)} questions from questions.json")
        except Exception as e:
            print(f"Failed to load questions.json: {e}, using built-in bank")
            pool = QUESTION_BANK.copy()
    else:
        pool = QUESTION_BANK.copy()

    fresh = [q for q in pool if q["question"] not in asked]
    print(f"Fresh: {len(fresh)} / {len(pool)}")

    if len(fresh) < count:
        print("Full cycle complete â resetting asked history!")
        asked = set()
        fresh = pool.copy()
        SESSION_DATA["asked"] = []

    random.shuffle(fresh)
    selected = fresh[:min(count, len(fresh))]
    SESSION_DATA["asked"] = list(asked | {q["question"] for q in selected})
    return selected


# âââ DISCORD VIEWS ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

class MCQView(discord.ui.View):
    def __init__(self, question: dict):
        super().__init__(timeout=ALIVE_MINUTES * 60)
        self.question = question
        # Normalize option keys to uppercase
        self.question["options"] = {k.upper(): v for k, v in question.get("options", {}).items()}
        self.question["answer"]  = question.get("answer", "A").upper()
        self.answered_users  = set()
        self.user_start_times = {}
        for i, label in enumerate(["A", "B", "C", "D"]):
            btn = discord.ui.Button(
                label=f"{label}.  {question['options'][label]}",
                custom_id=label,
                style=discord.ButtonStyle.secondary,
                row=i // 2
            )
            btn.callback = self.make_callback(label)
            self.add_item(btn)

    def make_callback(self, label: str):
        async def callback(interaction: discord.Interaction):
            try:
                user_id = str(interaction.user.id)
                username = interaction.user.display_name
                now = datetime.datetime.utcnow()

                # Personal timer check
                if user_id in self.user_start_times:
                    elapsed = (now - self.user_start_times[user_id]).total_seconds()
                    if elapsed > PERSONAL_TIMER_MIN * 60:
                        expiry = self.user_start_times[user_id] + datetime.timedelta(minutes=PERSONAL_TIMER_MIN)
                        e = discord.Embed(
                            title="â°  Time's Up",
                            description=f"Your {PERSONAL_TIMER_MIN}-minute window expired at **{expiry.strftime('%H:%M')} UTC**.",
                            color=0x2B2D31
                        )
                        await interaction.response.send_message(embed=e, ephemeral=True)
                        return

                if user_id in self.answered_users:
                    e = discord.Embed(
                        title="â ï¸  Already Answered",
                        description="You have already responded to this question.",
                        color=0xFFA500
                    )
                    await interaction.response.send_message(embed=e, ephemeral=True)
                    return

                # Start timer on first tap
                if user_id not in self.user_start_times:
                    self.user_start_times[user_id] = now

                self.answered_users.add(user_id)
                correct = self.question["answer"]
                is_correct = label == correct
                explanation = self.question.get("explanation", "")
                subject = self.question.get("subject", "General")
                new_points = await update_score(user_id, username, is_correct, subject)
                badge, rank_title, rank_color = get_rank(new_points)
                expiry_str = (now + datetime.timedelta(minutes=PERSONAL_TIMER_MIN)).strftime("%H:%M UTC")

                # Get streak from in-memory data
                streak = SESSION_DATA.get("streaks", {}).get(user_id, {}).get("streak", 0)
                streak_badge = get_streak_badge(streak)
                streak_text = f"  {streak_badge} {streak}-day streak" if streak >= 3 else ""

                if is_correct:
                    e = discord.Embed(color=0x57F287)
                    e.add_field(
                        name="â  Correct",
                        value=f"**{label}.  {self.question['options'][label]}**",
                        inline=False
                    )
                    if explanation:
                        e.add_field(name="ð¡ Explanation", value=explanation, inline=False)
                    e.add_field(
                        name="Score",
                        value=f"`+10 pts` â **{new_points} pts total**  Â·  {badge} {rank_title}{streak_text}",
                        inline=False
                    )
                else:
                    e = discord.Embed(color=0xED4245)
                    e.add_field(
                        name="â  Incorrect",
                        value=f"~~{label}.  {self.question['options'][label]}~~",
                        inline=False
                    )
                    e.add_field(
                        name="â  Correct Answer",
                        value=f"**{correct}.  {self.question['options'][correct]}**",
                        inline=False
                    )
                    if explanation:
                        e.add_field(name="ð¡ Explanation", value=explanation, inline=False)
                    e.add_field(
                        name="Score",
                        value=f"**{new_points} pts total**  Â·  {badge} {rank_title}{streak_text}",
                        inline=False
                    )
                e.set_footer(text=f"Your window closes at {expiry_str}  Â·  {PERSONAL_TIMER_MIN} min per session")
                await interaction.response.send_message(embed=e, ephemeral=True)
            except discord.errors.NotFound:
                pass
            except Exception as ex:
                print(f"Button error: {ex}")
        return callback


class FlashcardView(discord.ui.View):
    def __init__(self, question: dict):
        super().__init__(timeout=ALIVE_MINUTES * 60)
        self.question = question
        self.answered_users = set()
        self.user_start_times = {}

    @discord.ui.button(label="Reveal Answer", style=discord.ButtonStyle.secondary)
    async def reveal(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            user_id = str(interaction.user.id)
            username = interaction.user.display_name
            now = datetime.datetime.utcnow()

            if user_id in self.user_start_times:
                elapsed = (now - self.user_start_times[user_id]).total_seconds()
                if elapsed > PERSONAL_TIMER_MIN * 60:
                    expiry = self.user_start_times[user_id] + datetime.timedelta(minutes=PERSONAL_TIMER_MIN)
                    e = discord.Embed(
                        title="â°  Time's Up",
                        description=f"Your window expired at **{expiry.strftime('%H:%M')} UTC**.",
                        color=0x2B2D31
                    )
                    await interaction.response.send_message(embed=e, ephemeral=True)
                    return

            already = user_id in self.answered_users
            self.answered_users.add(user_id)
            if user_id not in self.user_start_times:
                self.user_start_times[user_id] = now

            if not already:
                subject = self.question.get("subject", "General")
                new_points = await update_score(user_id, username, True, subject, points_to_add=5)
            else:
                new_points = SESSION_DATA.get("scores", {}).get(user_id, {}).get("points", 0)

            badge, rank_title, _ = get_rank(new_points or 0)
            expiry_str = (self.user_start_times[user_id] + datetime.timedelta(minutes=PERSONAL_TIMER_MIN)).strftime("%H:%M UTC")

            e = discord.Embed(color=0x5865F2)
            e.add_field(name="ð¡  Answer", value=f"**{self.question['answer']}**", inline=False)
            if self.question.get("explanation"):
                e.add_field(name="ð Explanation", value=self.question["explanation"], inline=False)
            pts_text = f"`+5 pts` â **{new_points} pts total**  Â·  {badge} {rank_title}" if not already else f"**{new_points} pts total**  Â·  {badge} {rank_title}"
            e.add_field(name="Score", value=pts_text, inline=False)
            e.set_footer(text=f"Your window closes at {expiry_str}")
            await interaction.response.send_message(embed=e, ephemeral=True)
        except discord.errors.NotFound:
            pass
        except Exception as ex:
            print(f"Flashcard error: {ex}")


# âââ QUIZ SESSION ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

async def run_quiz_session(channel: discord.TextChannel):
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=6)
    date_str = now.strftime("%d %B %Y")
    end_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=ALIVE_MINUTES)

    announce = discord.Embed(
        title=f"ð  Daily Quiz  Â·  {date_str}",
        color=0x5865F2
    )
    announce.add_field(name="Questions",  value=f"`{QUESTIONS_PER_SESSION}`", inline=True)
    announce.add_field(name="MCQ",        value="`+10 pts`", inline=True)
    announce.add_field(name="Flashcard",  value="`+5 pts`",  inline=True)
    announce.add_field(name="Your Timer", value=f"`{PERSONAL_TIMER_MIN} min` from first tap", inline=True)
    announce.add_field(name="Session Ends", value=f"<t:{int(end_time.timestamp())}:R>", inline=True)
    announce.add_field(name="Visibility", value="Only you see your answers", inline=True)
    announce.set_footer(text="ð Elite Â· ð Legend Â· ð¥ Champion Â· â¡ Scholar Â· ð Apprentice Â· ð± Rookie")
    await channel.send(embed=announce)
    await asyncio.sleep(1.5)

    questions = await pick_questions_smart(QUESTIONS_PER_SESSION)
    print(f"Posting {len(questions)} questions")

    for i, q in enumerate(questions, 1):
        meta    = get_subject(q.get("subject", "General"))
        subject = q.get("subject", "General")

        if q["type"] == "mcq":
            opts = q.get("options", {})
            # Normalize keys â handle both uppercase and lowercase
            opts = {k.upper(): v for k, v in opts.items()}
            embed = discord.Embed(title=q["question"], color=meta["color"])
            embed.set_author(name=f"{meta['emoji']}  {meta['label']}  Â·  Question {i} of {len(questions)}")
            embed.add_field(
                name="",
                value=(
                    f"**A.**  {opts.get('A', 'â')}\n"
                    f"**B.**  {opts.get('B', 'â')}\n"
                    f"**C.**  {opts.get('C', 'â')}\n"
                    f"**D.**  {opts.get('D', 'â')}"
                ),
                inline=False
            )
            embed.set_footer(text=f"â± {PERSONAL_TIMER_MIN} min from first tap  Â·  Only you see your result")
            # Also normalize options in the question object for button callbacks
            q["options"] = opts
            await channel.send(embed=embed, view=MCQView(q))
        else:
            embed = discord.Embed(title=q["question"], color=meta["color"])
            embed.set_author(name=f"{meta['emoji']}  {meta['label']}  Â·  Flashcard {i} of {len(questions)}")
            embed.set_footer(text="ð­ Think of your answer, then tap Reveal  Â·  Only you see the result")
            await channel.send(embed=embed, view=FlashcardView(q))

        await asyncio.sleep(1.5)

    closing = discord.Embed(
        title="â³  Session Running",
        description=(
            f"All {len(questions)} questions posted.\n\n"
            f"Tap any button to start your **{PERSONAL_TIMER_MIN}-minute** personal timer.\n"
            f"Leaderboard posts <t:{int(end_time.timestamp())}:R>."
        ),
        color=0xFF8C00
    )
    await channel.send(embed=closing)
    await asyncio.sleep(ALIVE_MINUTES * 60)
    await post_scoreboard(channel)


async def post_scoreboard(channel: discord.TextChannel):
    scores        = SESSION_DATA.get("scores", {})
    streaks       = SESSION_DATA.get("streaks", {})
    session_count = SESSION_DATA.get("session_count", 0) + 1
    SESSION_DATA["session_count"] = session_count

    embed = build_scoreboard_embed(scores, streaks, session_count)
    await channel.send(embed=embed)

    # Check if cycle complete â reset scores every 10 sessions
    if session_count % SESSIONS_PER_CYCLE == 0:
        cycle_num = session_count // SESSIONS_PER_CYCLE
        SESSION_DATA["scores"] = {}
        reset_embed = discord.Embed(
            title=f"ð  Cycle #{cycle_num} Complete!",
            description=(
                f"The **{SESSIONS_PER_CYCLE}-session scoreboard** has been reset.\n\n"
                f"All scores back to zero â a fresh start for everyone!\n"
                f"Streaks are preserved. Good luck in Cycle #{cycle_num + 1}! ð"
            ),
            color=0x5865F2,
            timestamp=datetime.datetime.utcnow()
        )
        await channel.send(embed=reset_embed)
        print(f"Cycle {cycle_num} complete â scores reset!")

    # Save to Gist ONCE
    await save_session_data()
    print("Session data saved to Gist.")
    # Send individual report cards
    await send_report_cards(channel.guild, scores, streaks)


async def send_report_cards(guild: discord.Guild, scores: dict, streaks: dict):
    """DM each participant their personal report card."""
    if not scores:
        return

    # Build sorted list for rank
    sorted_scores = sorted(scores.values(), key=lambda x: x["points"], reverse=True)
    rank_map = {}
    rank = 0
    prev_pts = None
    for i, s in enumerate(sorted_scores):
        if s["points"] != prev_pts:
            rank = i + 1
        prev_pts = s["points"]
        rank_map[s["username"]] = rank

    for user_id, s in scores.items():
        try:
            member = guild.get_member(int(user_id))
            if not member:
                continue

            acc = round(100*s["correct"]/s["total"]) if s["total"] > 0 else 0
            badge, rank_title, _ = get_rank(s["points"])
            streak = streaks.get(user_id, {}).get("streak", 0)
            streak_badge = get_streak_badge(streak)
            user_rank = rank_map.get(s["username"], "â")

            embed = discord.Embed(
                title=f"ð  Your Report Card",
                color=0x5865F2,
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_author(name=member.display_name, icon_url=member.display_avatar.url)

            # Overall
            embed.add_field(
                name="Overall",
                value=(
                    f"Rank: **#{user_rank}**  Â·  {badge} {rank_title}\n"
                    f"Points: **{s['points']} pts**\n"
                    f"Accuracy: **{acc}%** ({s['correct']}/{s['total']} correct)\n"
                    + (f"Streak: {streak_badge} **{streak} days**" if streak >= 1 else "Streak: just started!")
                ),
                inline=False
            )

            # Subject breakdown
            subjects = s.get("subjects", {})
            if subjects:
                sub_lines = []
                best_sub = max(subjects.items(), key=lambda x: x[1]["correct"]/max(x[1]["total"],1))
                worst_sub = min(subjects.items(), key=lambda x: x[1]["correct"]/max(x[1]["total"],1))

                for subj, stat in subjects.items():
                    sub_acc = round(100*stat["correct"]/stat["total"]) if stat["total"] > 0 else 0
                    bar_f = round(sub_acc/10)
                    bar = "â°"*bar_f + "â±"*(10-bar_f)
                    meta = SUBJECT_META.get(subj, {"emoji":"ð"})
                    sub_lines.append(f"{meta['emoji']} **{subj}**  {bar}  {sub_acc}% ({stat['correct']}/{stat['total']})")

                embed.add_field(name="ð Subject Breakdown", value="\n".join(sub_lines), inline=False)
                embed.add_field(
                    name="ðª Strength & Weakness",
                    value=f"Best: **{best_sub[0]}**  Â·  Needs work: **{worst_sub[0]}**",
                    inline=False
                )

            # Motivational line
            if acc >= 80:
                msg = "Excellent work! You're on fire ð¥"
            elif acc >= 60:
                msg = "Good job! Keep pushing ðª"
            elif acc >= 40:
                msg = "Not bad â review your weak subjects ð"
            else:
                msg = "Don't give up! Consistency beats talent ð±"
            embed.set_footer(text=msg)

            await member.send(embed=embed)
            await asyncio.sleep(0.5)  # avoid rate limit
        except discord.Forbidden:
            print(f"Can't DM {user_id} â DMs closed")
        except Exception as ex:
            print(f"Report card error for {user_id}: {ex}")


# âââ BOT ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    global _save_lock
    _save_lock = asyncio.Lock()
    print(f"Logged in as {bot.user}")
    await bot.tree.sync()
    print(f"CHANNEL_ID: {CHANNEL_ID} | GIST_ID: {GIST_ID} | TOKEN_LEN: {len(GIST_TOKEN) if GIST_TOKEN else 0}")
    # Load data ONCE into memory
    await load_session_data()
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print(f"Channel {CHANNEL_ID} not found")
        await bot.close()
        return
    print(f"Starting quiz in #{channel.name}")
    await run_quiz_session(channel)
    print("Done. Shutting down.")
    await bot.close()


@bot.tree.command(name="savescores", description="[Admin] Force save current scores to Gist mid-session")
async def savescores_cmd(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    ok = await save_session_data()
    if ok:
        await interaction.followup.send("â Scores saved to Gist! You can now edit the Gist safely.", ephemeral=True)
    else:
        await interaction.followup.send("â Save failed. Check logs.", ephemeral=True)


@bot.tree.command(name="editscore", description="[Admin] Manually set a player's points")
async def editscore_cmd(interaction: discord.Interaction, username: str, points: int):
    scores = SESSION_DATA.setdefault("scores", {})
    # Find by username
    for uid, s in scores.items():
        if s["username"].lower() == username.lower():
            old = s["points"]
            s["points"] = points
            await interaction.response.send_message(
                f"â **{s['username']}**: `{old} pts` â `{points} pts`",
                ephemeral=True
            )
            return
    await interaction.response.send_message(
        f"â Player `{username}` not found in current session.",
        ephemeral=True
    )


if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
