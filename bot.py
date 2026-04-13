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

# ─── CONFIG ────────────────────────────────────────────────────────────────────
DISCORD_TOKEN         = os.environ.get("DISCORD_TOKEN")
CHANNEL_ID            = int(os.environ.get("CHANNEL_ID", "0"))
GIST_TOKEN            = os.environ.get("GIST_TOKEN")
GIST_ID               = os.environ.get("GIST_ID")
QUESTIONS_PER_SESSION = 10
ALIVE_MINUTES         = 60
PERSONAL_TIMER_MIN    = 10
# ────────────────────────────────────────────────────────────────────────────────

# ─── QUESTION BANK ──────────────────────────────────────────────────────────────
# ▼▼▼ PASTE YOUR QUESTIONS HERE — replace the placeholder below ▼▼▼
QUESTION_BANK = [
    {"type":"mcq","subject":"Biology","question":"নিচের কোনটিতে হাইড্রার বহিঃকোষীয় পরিপাক সংঘটিত হয়?","options":{"A":"গ্যাস্ট্রোডার্মিস","B":"হাইপোস্টোম","C":"সিলেন্টেরন","D":"কর্ষিকা"},"answer":"C","explanation":"হাইড্রার সিলেন্টেরনে বহিঃকোষীয় পরিপাক ঘটে।"},
    {"type":"mcq","subject":"Biology","question":"কোষ বিভাজনের সময় কোষপ্লেট তৈরিতে সাহায্য করে কোন অঙ্গাণু?","options":{"A":"লাইসোসোম","B":"গলগি বস্তু","C":"মাইটোকন্ড্রিয়া","D":"রাইবোসোম"},"answer":"B","explanation":"গলগি বস্তু কোষ বিভাজনের সময় কোষপ্লেট গঠনে সাহায্য করে।"},
    {"type":"mcq","subject":"Biology","question":"রেস্ট্রিকশন এনজাইমের কাজ কী?","options":{"A":"DNA অণু বৃদ্ধিকরণ","B":"DNA খণ্ডকে জোড়া লাগানো","C":"নির্দিষ্ট জীবে রিকম্বিনেন্ট DNA প্রবেশ করানো","D":"কাঙ্ক্ষিত DNA কে নির্দিষ্ট স্থানে ছেদন করা"},"answer":"D","explanation":"রেস্ট্রিকশন এনজাইম নির্দিষ্ট স্থানে DNA ছেদন করে।"},
    {"type":"mcq","subject":"Chemistry","question":"18°C তাপমাত্রায় 0.8 atm চাপে একটি গ্যাসের ঘনত্ব 2.25 gL⁻¹ হলে আণবিক ভর কত?","options":{"A":"36.63 g mol⁻¹","B":"36.24 g mol⁻¹","C":"24.36 g mol⁻¹","D":"67.11 g mol⁻¹"},"answer":"A","explanation":"PV=nRT ব্যবহার করে M = dRT/P ≈ 36.63 g/mol"},
    {"type":"mcq","subject":"Chemistry","question":"কোন দ্রবণের OH⁻ আয়নের ঘনমাত্রা 3.5×10⁻⁴ M হলে pH কত?","options":{"A":"12.50","B":"13.55","C":"10.54","D":"3.55"},"answer":"C","explanation":"pOH = -log(3.5×10⁻⁴) ≈ 3.46; pH = 14-3.46 = 10.54"},
    {"type":"mcq","subject":"Physics","question":"ফোকাস দূরত্ব 1000 cm হলে উত্তল লেন্সের ক্ষমতা কত?","options":{"A":"+10 D","B":"+100 D","C":"+0.1 D","D":"-0.1 D"},"answer":"C","explanation":"P = 1/f(m) = 1/10 = +0.1 D"},
    {"type":"mcq","subject":"Physics","question":"দুটি ভেক্টর 8 ও 6 একক, 30° কোণে ক্রিয়াশীল হলে ভেক্টর গুণফল কত?","options":{"A":"16","B":"20","C":"48","D":"24"},"answer":"D","explanation":"A×B = |A||B|sinθ = 8×6×sin30° = 24"},
    {"type":"mcq","subject":"English","question":"Synonym of 'anarchy'—","options":{"A":"serenity","B":"placidity","C":"lawlessness","D":"discipline"},"answer":"C","explanation":"Anarchy = a state of disorder/lawlessness."},
    {"type":"mcq","subject":"GK","question":"বাংলাদেশের ১০০ টাকার নোটে কোন মসজিদের ছবি আছে?","options":{"A":"মডেল মসজিদ","B":"ষাট গম্বুজ মসজিদ","C":"আতিয়া মসজিদ","D":"তারা মসজিদ"},"answer":"B","explanation":"১০০ টাকার নোটে ষাট গম্বুজ মসজিদ।"},
    {"type":"mcq","subject":"GK","question":"WHO কালাজ্বরমুক্ত দেশ হিসেবে বাংলাদেশকে স্বীকৃতি দেয় কবে?","options":{"A":"৩০ সেপ্টেম্বর ২০২৩","B":"৩১ অক্টোবর ২০২৩","C":"০১ নভেম্বর ২০২৩","D":"৩০ নভেম্বর ২০২৩"},"answer":"B","explanation":"৩১ অক্টোবর ২০২৩ সালে WHO এই স্বীকৃতি দেয়।"},
    {"type":"mcq","subject":"Math","question":"কোন তাপমাত্রায় সেলসিয়াস ও ফারেনহাইট একই মান দেখায়?","options":{"A":"-40°","B":"32°","C":"40°","D":"-32°"},"answer":"A","explanation":"C=F হলে, C = 9C/5+32 → C = -40°"},
    {"type":"mcq","subject":"Biology","question":"হিমোগ্লোবিনের কোন অংশে CO₂ যুক্ত হয়?","options":{"A":"−OH","B":"−COOH","C":"−HCO₃","D":"−NH₂"},"answer":"D","explanation":"CO₂, হিমোগ্লোবিনের −NH₂ গ্রুপের সাথে যুক্ত হয়।"},
]
# ▲▲▲ END OF QUESTION BANK ▲▲▲
# ────────────────────────────────────────────────────────────────────────────────


# ─── GIST SCORE STORAGE ─────────────────────────────────────────────────────────

def _load_scores_sync() -> dict:
    try:
        req = urllib.request.Request(
            f"https://api.github.com/gists/{GIST_ID}",
            headers={"Authorization": f"token {GIST_TOKEN}", "Accept": "application/vnd.github.v3+json"}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            return json.loads(data["files"]["scores.json"]["content"])
    except Exception as e:
        print(f"Gist load error: {e}")
        return {}

def _save_scores_sync(scores: dict) -> bool:
    try:
        payload = json.dumps({
            "files": {"scores.json": {"content": json.dumps(scores, ensure_ascii=False, indent=2)}}
        }).encode("utf-8")
        req = urllib.request.Request(
            f"https://api.github.com/gists/{GIST_ID}",
            data=payload,
            headers={"Authorization": f"token {GIST_TOKEN}", "Accept": "application/vnd.github.v3+json", "Content-Type": "application/json"},
            method="PATCH"
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            print(f"Scores saved. Players: {len(scores)}")
            return True
    except Exception as e:
        print(f"Gist save error: {e}")
        return False

async def load_scores() -> dict:
    if not GIST_TOKEN or not GIST_ID:
        return {}
    return await asyncio.get_event_loop().run_in_executor(executor, _load_scores_sync)

async def save_scores(scores: dict) -> bool:
    if not GIST_TOKEN or not GIST_ID:
        return False
    return await asyncio.get_event_loop().run_in_executor(executor, _save_scores_sync, scores)

async def update_score(user_id: str, username: str, correct: bool, points_to_add: int = 10) -> int:
    scores = await load_scores()
    if user_id not in scores:
        scores[user_id] = {"username": username, "points": 0, "correct": 0, "total": 0}
    scores[user_id]["username"] = username
    scores[user_id]["total"] += 1
    if correct:
        scores[user_id]["points"] += points_to_add
        scores[user_id]["correct"] += 1
    await save_scores(scores)
    return scores[user_id]["points"]


# ─── UI HELPERS ─────────────────────────────────────────────────────────────────

SUBJECT_META = {
    "Physics":   {"emoji": "⚡", "color": 0x5865F2, "label": "Physics"},
    "Chemistry": {"emoji": "⚗️",  "color": 0xED4245, "label": "Chemistry"},
    "Math":      {"emoji": "📐", "color": 0x57F287, "label": "Mathematics"},
    "Biology":   {"emoji": "🔬", "color": 0xFEE75C, "label": "Biology"},
    "English":   {"emoji": "📖", "color": 0x00B4FF, "label": "English"},
    "GK":        {"emoji": "🌐", "color": 0xFF8C00, "label": "General Knowledge"},
}

def get_subject(subject: str) -> dict:
    return SUBJECT_META.get(subject, {"emoji": "📋", "color": 0x5865F2, "label": subject})

def get_rank(points: int) -> tuple:
    """Returns (badge_emoji, title, color_hex)"""
    if points >= 1000: return ("💎", "ELITE",      0xA8D8EA)
    elif points >= 500: return ("👑", "LEGEND",     0xFFD700)
    elif points >= 200: return ("🔥", "CHAMPION",   0xFF6B35)
    elif points >= 100: return ("⚡", "SCHOLAR",    0x5865F2)
    elif points >= 50:  return ("📚", "APPRENTICE", 0x57F287)
    return                     ("🌱", "ROOKIE",     0x99AAB5)

def build_scoreboard_embed(scores: dict) -> discord.Embed:
    now_bd = datetime.datetime.utcnow() + datetime.timedelta(hours=6)

    if not scores:
        embed = discord.Embed(
            title="🏆  Leaderboard",
            description="No participants today. Come back tomorrow!",
            color=0x2B2D31,
            timestamp=datetime.datetime.utcnow()
        )
        return embed

    sorted_scores = sorted(scores.values(), key=lambda x: x["points"], reverse=True)
    max_pts = max(s["points"] for s in sorted_scores) or 1

    embed = discord.Embed(
        title=f"🏆  Leaderboard  ·  {now_bd.strftime('%d %B %Y')}",
        color=0xFFD700,
        timestamp=datetime.datetime.utcnow()
    )

    # Top 3 as special fields
    podium_icons = ["🥇", "🥈", "🥉"]
    podium_lines = []
    for i, s in enumerate(sorted_scores[:3]):
        acc = round(100*s["correct"]/s["total"]) if s["total"] > 0 else 0
        badge, title, _ = get_rank(s["points"])
        podium_lines.append(
            f"{podium_icons[i]} **{s['username']}** {badge}\n"
            f"　`{s['points']} pts`  ·  {acc}% accuracy  ·  {title}"
        )
    embed.description = "\n\n".join(podium_lines)

    # Ranks 4-10
    if len(sorted_scores) > 3:
        rest_lines = []
        for i, s in enumerate(sorted_scores[3:10], 4):
            acc = round(100*s["correct"]/s["total"]) if s["total"] > 0 else 0
            filled = round((s["points"]/max_pts)*10)
            bar = "▰"*filled + "▱"*(10-filled)
            rest_lines.append(f"`{i:02d}`  {s['username'][:16]}  {bar}  `{s['points']}`")
        embed.add_field(name="Others", value="\n".join(rest_lines), inline=False)

    # Stats
    total_p = len(sorted_scores)
    total_a = sum(s["total"] for s in sorted_scores)
    avg_acc = round(sum(100*s["correct"]/s["total"] for s in sorted_scores if s["total"]>0)/max(total_p,1))
    embed.add_field(
        name="📊 Session",
        value=f"`{total_p}` players  ·  `{total_a}` answers  ·  `{avg_acc}%` avg",
        inline=False
    )
    embed.set_footer(text="💎 Elite 1000+  ·  👑 Legend 500+  ·  🔥 Champion 200+  ·  ⚡ Scholar 100+  ·  📚 Apprentice 50+")
    return embed


# ─── QUESTION PICKER ────────────────────────────────────────────────────────────

def pick_questions(count: int) -> list:
    if os.path.exists("questions.json"):
        try:
            with open("questions.json", "r", encoding="utf-8") as f:
                external = json.load(f)
            if external:
                for q in external:
                    q.setdefault("type", "mcq")
                    q.setdefault("subject", "General")
                print(f"Loaded {len(external)} questions from questions.json")
                pool = external.copy()
                random.shuffle(pool)
                return pool[:count]
        except Exception as e:
            print(f"Failed to load questions.json: {e}, using built-in bank")
    pool = QUESTION_BANK.copy()
    random.shuffle(pool)
    # Fix: ensure we never return more than available
    return pool[:min(count, len(pool))]


# ─── DISCORD VIEWS ──────────────────────────────────────────────────────────────

class MCQView(discord.ui.View):
    def __init__(self, question: dict):
        super().__init__(timeout=ALIVE_MINUTES * 60)
        self.question = question
        self.answered_users = set()
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
                            title="⏰  Time's Up",
                            description=f"Your {PERSONAL_TIMER_MIN}-minute window expired at **{expiry.strftime('%H:%M')} UTC**.",
                            color=0x2B2D31
                        )
                        await interaction.response.send_message(embed=e, ephemeral=True)
                        return

                if user_id in self.answered_users:
                    e = discord.Embed(
                        title="⚠️  Already Answered",
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
                new_points = await update_score(user_id, username, is_correct)
                badge, rank_title, rank_color = get_rank(new_points)
                expiry_str = (now + datetime.timedelta(minutes=PERSONAL_TIMER_MIN)).strftime("%H:%M UTC")

                if is_correct:
                    e = discord.Embed(color=0x57F287)
                    e.add_field(
                        name="✅  Correct",
                        value=f"**{label}.  {self.question['options'][label]}**",
                        inline=False
                    )
                    if explanation:
                        e.add_field(name="💡 Explanation", value=explanation, inline=False)
                    e.add_field(
                        name="Score",
                        value=f"`+10 pts` → **{new_points} pts total**  ·  {badge} {rank_title}",
                        inline=False
                    )
                else:
                    e = discord.Embed(color=0xED4245)
                    e.add_field(
                        name="❌  Incorrect",
                        value=f"~~{label}.  {self.question['options'][label]}~~",
                        inline=False
                    )
                    e.add_field(
                        name="✅  Correct Answer",
                        value=f"**{correct}.  {self.question['options'][correct]}**",
                        inline=False
                    )
                    if explanation:
                        e.add_field(name="💡 Explanation", value=explanation, inline=False)
                    e.add_field(
                        name="Score",
                        value=f"**{new_points} pts total**  ·  {badge} {rank_title}",
                        inline=False
                    )
                e.set_footer(text=f"Your window closes at {expiry_str}  ·  {PERSONAL_TIMER_MIN} min per session")
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
                        title="⏰  Time's Up",
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
                new_points = await update_score(user_id, username, True, points_to_add=5)
            else:
                sc = await load_scores()
                new_points = sc.get(user_id, {}).get("points", 0)

            badge, rank_title, _ = get_rank(new_points or 0)
            expiry_str = (self.user_start_times[user_id] + datetime.timedelta(minutes=PERSONAL_TIMER_MIN)).strftime("%H:%M UTC")

            e = discord.Embed(color=0x5865F2)
            e.add_field(name="💡  Answer", value=f"**{self.question['answer']}**", inline=False)
            if self.question.get("explanation"):
                e.add_field(name="📖 Explanation", value=self.question["explanation"], inline=False)
            pts_text = f"`+5 pts` → **{new_points} pts total**  ·  {badge} {rank_title}" if not already else f"**{new_points} pts total**  ·  {badge} {rank_title}"
            e.add_field(name="Score", value=pts_text, inline=False)
            e.set_footer(text=f"Your window closes at {expiry_str}")
            await interaction.response.send_message(embed=e, ephemeral=True)
        except discord.errors.NotFound:
            pass
        except Exception as ex:
            print(f"Flashcard error: {ex}")


# ─── QUIZ SESSION ────────────────────────────────────────────────────────────────

async def run_quiz_session(channel: discord.TextChannel):
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=6)
    date_str = now.strftime("%d %B %Y")
    end_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=ALIVE_MINUTES)

    announce = discord.Embed(
        title=f"📋  Daily Quiz  ·  {date_str}",
        color=0x5865F2
    )
    announce.add_field(name="Questions",  value=f"`{QUESTIONS_PER_SESSION}`", inline=True)
    announce.add_field(name="MCQ",        value="`+10 pts`", inline=True)
    announce.add_field(name="Flashcard",  value="`+5 pts`",  inline=True)
    announce.add_field(name="Your Timer", value=f"`{PERSONAL_TIMER_MIN} min` from first tap", inline=True)
    announce.add_field(name="Session Ends", value=f"<t:{int(end_time.timestamp())}:R>", inline=True)
    announce.add_field(name="Visibility", value="Only you see your answers", inline=True)
    announce.set_footer(text="💎 Elite · 👑 Legend · 🔥 Champion · ⚡ Scholar · 📚 Apprentice · 🌱 Rookie")
    await channel.send(embed=announce)
    await asyncio.sleep(1.5)

    questions = pick_questions(QUESTIONS_PER_SESSION)
    print(f"Posting {len(questions)} questions")

    for i, q in enumerate(questions, 1):
        meta = get_subject(q.get("subject", "General"))

        if q["type"] == "mcq":
            embed = discord.Embed(title=q["question"], color=meta["color"])
            embed.set_author(name=f"{meta['emoji']}  {meta['label']}  ·  Q{i} / {len(questions)}")
            embed.add_field(name="A", value=q["options"]["A"], inline=True)
            embed.add_field(name="B", value=q["options"]["B"], inline=True)
            embed.add_field(name="C", value=q["options"]["C"], inline=True)
            embed.add_field(name="D", value=q["options"]["D"], inline=True)
            embed.set_footer(text=f"Timer starts on your first tap  ·  {PERSONAL_TIMER_MIN} min window  ·  Only you see your result")
            await channel.send(embed=embed, view=MCQView(q))
        else:
            embed = discord.Embed(title=q["question"], color=meta["color"])
            embed.set_author(name=f"{meta['emoji']}  {meta['label']}  ·  Flashcard  {i} / {len(questions)}")
            embed.set_footer(text="Think, then tap Reveal  ·  Only you see the answer")
            await channel.send(embed=embed, view=FlashcardView(q))

        await asyncio.sleep(1.5)

    closing = discord.Embed(
        title="⏳  Session Running",
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
    scores = await load_scores()
    embed = build_scoreboard_embed(scores)
    await channel.send(embed=embed)


# ─── BOT ────────────────────────────────────────────────────────────────────────

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await bot.tree.sync()
    print(f"CHANNEL_ID: {CHANNEL_ID} | GIST_ID: {GIST_ID} | TOKEN_LEN: {len(GIST_TOKEN) if GIST_TOKEN else 0}")
    test = await load_scores()
    print(f"Gist load: {test}")
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print(f"Channel {CHANNEL_ID} not found")
        await bot.close()
        return
    print(f"Starting quiz in #{channel.name}")
    await run_quiz_session(channel)
    print("Done. Shutting down.")
    await bot.close()


if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
