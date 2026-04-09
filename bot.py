import discord
from discord.ext import commands
import json
import os
import random
import asyncio
import datetime
import urllib.request
import urllib.error

# ─── CONFIG ────────────────────────────────────────────────────────────────────
DISCORD_TOKEN   = os.environ.get("DISCORD_TOKEN")
CHANNEL_ID      = int(os.environ.get("CHANNEL_ID", "0"))
JSONBIN_API_KEY = os.environ.get("JSONBIN_API_KEY")
JSONBIN_BIN_ID  = os.environ.get("JSONBIN_BIN_ID")
QUESTIONS_PER_SESSION = 5
ALIVE_MINUTES   = 180  # Stay alive 3 hours for button responses
# ────────────────────────────────────────────────────────────────────────────────

# ─── QUESTION BANK ─────────────────────────────────────────────────────────────
QUESTION_BANK = [
    {"type":"mcq","subject":"Physics","question":"একটি বস্তু 20 m/s বেগে উপরে নিক্ষেপ করা হলো। সর্বোচ্চ উচ্চতা কত? (g=10 m/s²)","options":{"A":"10 m","B":"20 m","C":"30 m","D":"40 m"},"answer":"B","explanation":"h = v²/2g = 400/20 = 20 m"},
    {"type":"mcq","subject":"Physics","question":"আলোর বেগ শূন্য মাধ্যমে কত?","options":{"A":"3×10⁶ m/s","B":"3×10⁷ m/s","C":"3×10⁸ m/s","D":"3×10⁹ m/s"},"answer":"C","explanation":"শূন্য মাধ্যমে আলোর বেগ c = 3×10⁸ m/s"},
    {"type":"mcq","subject":"Physics","question":"তড়িৎ বিভব একটি —","options":{"A":"ভেক্টর রাশি","B":"স্কেলার রাশি","C":"টেনসর রাশি","D":"মাত্রাহীন রাশি"},"answer":"B","explanation":"তড়িৎ বিভব একটি স্কেলার রাশি।"},
    {"type":"mcq","subject":"Physics","question":"কোন রঙের আলোর তরঙ্গদৈর্ঘ্য সবচেয়ে বেশি?","options":{"A":"বেগুনি","B":"নীল","C":"সবুজ","D":"লাল"},"answer":"D","explanation":"লাল আলোর তরঙ্গদৈর্ঘ্য সবচেয়ে বেশি (620–750 nm)।"},
    {"type":"mcq","subject":"Physics","question":"ওহমের সূত্র অনুযায়ী V = ?","options":{"A":"I/R","B":"IR","C":"I²R","D":"I/R²"},"answer":"B","explanation":"V = IR"},
    {"type":"mcq","subject":"Physics","question":"নিচের কোনটি তাড়িতচুম্বক তরঙ্গ নয়?","options":{"A":"X-ray","B":"Gamma ray","C":"Sound wave","D":"Microwave"},"answer":"C","explanation":"শব্দ তরঙ্গ যান্ত্রিক তরঙ্গ।"},
    {"type":"mcq","subject":"Physics","question":"কোনো বস্তুর ভরবেগ দ্বিগুণ হলে গতিশক্তি কতগুণ হবে?","options":{"A":"2 গুণ","B":"3 গুণ","C":"4 গুণ","D":"√2 গুণ"},"answer":"C","explanation":"KE = p²/2m, তাই p দ্বিগুণ হলে KE = 4 গুণ"},
    {"type":"mcq","subject":"Physics","question":"তরঙ্গদৈর্ঘ্য 6000 Å আলোর কম্পাঙ্ক কত?","options":{"A":"4×10¹⁴ Hz","B":"5×10¹⁴ Hz","C":"6×10¹⁴ Hz","D":"7×10¹⁴ Hz"},"answer":"B","explanation":"f = c/λ = 5×10¹⁴ Hz"},
    {"type":"mcq","subject":"Physics","question":"নিউটনের গতির দ্বিতীয় সূত্র — বল = ?","options":{"A":"ভরবেগ × সময়","B":"ভরবেগের পরিবর্তনের হার","C":"ভর × দূরত্ব","D":"ত্বরণ / ভর"},"answer":"B","explanation":"F = dp/dt"},
    {"type":"mcq","subject":"Physics","question":"সরল দোলকের দোলনকাল T=2s হলে দৈর্ঘ্য? (g=9.8)","options":{"A":"0.99 m","B":"1.99 m","C":"2.99 m","D":"3.99 m"},"answer":"A","explanation":"L = g(T/2π)² ≈ 0.99 m"},
    {"type":"mcq","subject":"Chemistry","question":"pH = 7 দ্রবণটি কী ধরনের?","options":{"A":"অম্লীয়","B":"ক্ষারীয়","C":"নিরপেক্ষ","D":"লবণাক্ত"},"answer":"C","explanation":"pH=7 নিরপেক্ষ।"},
    {"type":"mcq","subject":"Chemistry","question":"অ্যাভোগাড্রো সংখ্যার মান কত?","options":{"A":"6.022×10²¹","B":"6.022×10²³","C":"6.022×10²⁵","D":"6.022×10²⁷"},"answer":"B","explanation":"Nₐ = 6.022×10²³ mol⁻¹"},
    {"type":"mcq","subject":"Chemistry","question":"কোনটি নিষ্ক্রিয় গ্যাস?","options":{"A":"নাইট্রোজেন","B":"হাইড্রোজেন","C":"আর্গন","D":"অক্সিজেন"},"answer":"C","explanation":"আর্গন গ্রুপ 18।"},
    {"type":"mcq","subject":"Chemistry","question":"কোন ধাতু ঘরের তাপমাত্রায় তরল?","options":{"A":"সোডিয়াম","B":"পারদ","C":"পটাসিয়াম","D":"অ্যালুমিনিয়াম"},"answer":"B","explanation":"পারদ একমাত্র তরল ধাতু।"},
    {"type":"mcq","subject":"Chemistry","question":"Na (Z=11) এর শেষ কক্ষপথে কতটি ইলেকট্রন?","options":{"A":"1","B":"2","C":"3","D":"8"},"answer":"A","explanation":"Na: 2,8,1"},
    {"type":"mcq","subject":"Chemistry","question":"কার্বনের পারমাণবিক সংখ্যা কত?","options":{"A":"4","B":"6","C":"8","D":"12"},"answer":"B","explanation":"C: Z = 6"},
    {"type":"mcq","subject":"Chemistry","question":"কোনটি তীব্র অম্ল?","options":{"A":"অ্যাসিটিক এসিড","B":"কার্বনিক এসিড","C":"হাইড্রোক্লোরিক এসিড","D":"বোরিক এসিড"},"answer":"C","explanation":"HCl তীব্র অম্ল।"},
    {"type":"mcq","subject":"Chemistry","question":"তড়িৎ বিশ্লেষণে ক্যাথোডে কী ঘটে?","options":{"A":"জারণ","B":"বিজারণ","C":"নিরপেক্ষীকরণ","D":"অধঃক্ষেপণ"},"answer":"B","explanation":"ক্যাথোডে বিজারণ।"},
    {"type":"mcq","subject":"Chemistry","question":"পানির অণুতে হাইড্রোজেন পরমাণু কতটি?","options":{"A":"1","B":"2","C":"3","D":"4"},"answer":"B","explanation":"H₂O — দুটি H।"},
    {"type":"mcq","subject":"Chemistry","question":"মোলার ভর কাকে বলে?","options":{"A":"1 লিটার পদার্থের ভর","B":"1 মোল পদার্থের গ্রামে ভর","C":"1 অণুর ভর","D":"পরমাণুর ভর"},"answer":"B","explanation":"1 মোল পদার্থের গ্রামে ভর।"},
    {"type":"mcq","subject":"Math","question":"sin²θ + cos²θ = ?","options":{"A":"0","B":"1","C":"2","D":"-1"},"answer":"B","explanation":"মৌলিক ত্রিকোণমিতিক অভেদ।"},
    {"type":"mcq","subject":"Math","question":"log₁₀ 1000 = ?","options":{"A":"2","B":"3","C":"4","D":"10"},"answer":"B","explanation":"log₁₀ 10³ = 3"},
    {"type":"mcq","subject":"Math","question":"বৃত্তের ব্যাসার্ধ 7 cm হলে ক্ষেত্রফল?","options":{"A":"44 cm²","B":"154 cm²","C":"144 cm²","D":"22 cm²"},"answer":"B","explanation":"A = πr² = 154 cm²"},
    {"type":"mcq","subject":"Math","question":"∫x dx = ?","options":{"A":"x + c","B":"x² + c","C":"x²/2 + c","D":"2x + c"},"answer":"C","explanation":"∫xⁿ dx = xⁿ⁺¹/(n+1) + c"},
    {"type":"mcq","subject":"Math","question":"d/dx (sin x) = ?","options":{"A":"-sin x","B":"cos x","C":"-cos x","D":"tan x"},"answer":"B","explanation":"sin x এর অবকলন cos x।"},
    {"type":"mcq","subject":"Math","question":"A={1,2,3}, B={2,3,4} হলে A∩B = ?","options":{"A":"{1,2,3,4}","B":"{2,3}","C":"{1,4}","D":"{1,2,3}"},"answer":"B","explanation":"সাধারণ উপাদান = {2,3}"},
    {"type":"mcq","subject":"Math","question":"1+2+3+...+100 = ?","options":{"A":"4950","B":"5000","C":"5050","D":"5100"},"answer":"C","explanation":"n(n+1)/2 = 5050"},
    {"type":"mcq","subject":"Math","question":"সমকোণী ত্রিভুজের লম্ব 3, ভূমি 4 হলে অতিভুজ?","options":{"A":"5","B":"6","C":"7","D":"8"},"answer":"A","explanation":"c² = 9+16 = 25, c = 5"},
    {"type":"mcq","subject":"Math","question":"i² = ? (i = √-1)","options":{"A":"1","B":"-1","C":"i","D":"-i"},"answer":"B","explanation":"i² = -1"},
    {"type":"mcq","subject":"Math","question":"2x + 3 = 11 হলে x = ?","options":{"A":"3","B":"4","C":"5","D":"6"},"answer":"B","explanation":"x = 4"},
    {"type":"mcq","subject":"Biology","question":"মানব দেহের সবচেয়ে বড় অঙ্গ?","options":{"A":"যকৃত","B":"ফুসফুস","C":"ত্বক","D":"হৃদপিণ্ড"},"answer":"C","explanation":"ত্বক সবচেয়ে বড় অঙ্গ।"},
    {"type":"mcq","subject":"Biology","question":"সালোকসংশ্লেষণে কোন গ্যাস নির্গত হয়?","options":{"A":"CO₂","B":"N₂","C":"O₂","D":"H₂"},"answer":"C","explanation":"উদ্ভিদ O₂ নির্গত করে।"},
    {"type":"mcq","subject":"Biology","question":"মানব দেহে ক্রোমোজোম সংখ্যা?","options":{"A":"23","B":"44","C":"46","D":"48"},"answer":"C","explanation":"46টি (23 জোড়া)।"},
    {"type":"mcq","subject":"Biology","question":"কোষের শক্তিঘর কাকে বলে?","options":{"A":"নিউক্লিয়াস","B":"মাইটোকন্ড্রিয়া","C":"রাইবোজোম","D":"গলগি বডি"},"answer":"B","explanation":"মাইটোকন্ড্রিয়া ATP উৎপন্ন করে।"},
    {"type":"mcq","subject":"Biology","question":"রক্তের কোন উপাদান অক্সিজেন পরিবহন করে?","options":{"A":"শ্বেত রক্তকণিকা","B":"অণুচক্রিকা","C":"লোহিত রক্তকণিকা","D":"রক্তরস"},"answer":"C","explanation":"লোহিত রক্তকণিকার হিমোগ্লোবিন O₂ পরিবহন করে।"},
    {"type":"mcq","subject":"Biology","question":"উদ্ভিদকোষে কোন অঙ্গাণু প্রাণিকোষে নেই?","options":{"A":"মাইটোকন্ড্রিয়া","B":"ক্লোরোপ্লাস্ট","C":"রাইবোজোম","D":"নিউক্লিয়াস"},"answer":"B","explanation":"ক্লোরোপ্লাস্ট শুধু উদ্ভিদকোষে।"},
    {"type":"mcq","subject":"Biology","question":"মানব হৃদপিণ্ডে কতটি প্রকোষ্ঠ?","options":{"A":"2","B":"3","C":"4","D":"5"},"answer":"C","explanation":"2 অলিন্দ + 2 নিলয় = 4।"},
    {"type":"mcq","subject":"Biology","question":"ইনসুলিন কোথা থেকে নিঃসৃত?","options":{"A":"যকৃত","B":"অগ্ন্যাশয়","C":"থাইরয়েড","D":"বৃক্ক"},"answer":"B","explanation":"অগ্ন্যাশয়ের বিটা কোষ।"},
    {"type":"mcq","subject":"Biology","question":"প্রোটিন সংশ্লেষণ কোথায় হয়?","options":{"A":"নিউক্লিয়াস","B":"মাইটোকন্ড্রিয়া","C":"রাইবোজোম","D":"লাইসোজোম"},"answer":"C","explanation":"রাইবোজোম = প্রোটিন কারখানা।"},
    {"type":"mcq","subject":"Biology","question":"DNA-এর পূর্ণরূপ কী?","options":{"A":"Deoxyribonucleic Acid","B":"Diribonucleic Acid","C":"Deoxyribose Nucleic Acid","D":"Double Nucleic Acid"},"answer":"A","explanation":"DNA = Deoxyribonucleic Acid"},
    {"type":"flashcard","subject":"Physics","question":"নিউটনের প্রথম গতিসূত্র কী?","answer":"কোনো বস্তু স্থির থাকলে স্থিরই থাকবে, গতিশীল থাকলে সমবেগে চলতে থাকবে — যতক্ষণ বাহ্যিক বল না লাগে।","explanation":"জড়তার সূত্র।"},
    {"type":"flashcard","subject":"Chemistry","question":"পর্যায় সারণিতে কতটি মৌল আছে?","answer":"118টি মৌল।","explanation":"2016 সালে সর্বশেষ 4টি মৌলের নামকরণ।"},
    {"type":"flashcard","subject":"Math","question":"দ্বিঘাত সমীকরণের সমাধান সূত্র?","answer":"x = (−b ± √(b²−4ac)) / 2a","explanation":"b²−4ac = বিভেদক।"},
    {"type":"flashcard","subject":"Biology","question":"মানব শরীরে কতটি হাড়?","answer":"206টি।","explanation":"প্রাপ্তবয়স্ক মানুষের।"},
    {"type":"flashcard","subject":"Physics","question":"তাপগতিবিদ্যার প্রথম সূত্র?","answer":"ΔU = Q − W (শক্তির সংরক্ষণ সূত্র)","explanation":"শক্তি তৈরি বা ধ্বংস হয় না।"},
    {"type":"flashcard","subject":"Chemistry","question":"হ্যালোজেন গ্রুপের মৌলগুলো?","answer":"F, Cl, Br, I, At (গ্রুপ 17)","explanation":"অত্যন্ত সক্রিয় অধাতু।"},
    {"type":"flashcard","subject":"Biology","question":"মাইটোসিসের ধাপগুলো?","answer":"প্রোফেজ → মেটাফেজ → অ্যানাফেজ → টেলোফেজ","explanation":"1টি কোষ থেকে 2টি অপত্য কোষ।"},
    {"type":"flashcard","subject":"Math","question":"e (ইউলারের সংখ্যা) এর মান?","answer":"e ≈ 2.71828","explanation":"অমূলদ সংখ্যা।"},
    {"type":"flashcard","subject":"Physics","question":"তড়িৎ আধানের SI একক?","answer":"কুলম্ব (C)","explanation":"1C = 1A × 1s"},
    {"type":"flashcard","subject":"Chemistry","question":"অ্যাসিডের বৈশিষ্ট্য?","answer":"লিটমাস লাল করে, স্বাদে টক, H⁺ আয়ন দেয়।","explanation":"উদাহরণ: HCl, H₂SO₄"},
]
# ────────────────────────────────────────────────────────────────────────────────


# ─── JSONBIN SCOREBOARD ─────────────────────────────────────────────────────────

def load_scores() -> dict:
    if not JSONBIN_API_KEY or not JSONBIN_BIN_ID:
        print("WARNING: JSONBin credentials missing!")
        return {}
    try:
        req = urllib.request.Request(
            f"https://api.jsonbin.io/v3/b/{JSONBIN_BIN_ID}/latest",
            headers={
                "X-Master-Key": JSONBIN_API_KEY,
                "X-Bin-Meta": "false"
            }
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            # Strip "init" placeholder
            if isinstance(data, dict) and "init" in data and len(data) == 1:
                return {}
            return data
    except urllib.error.HTTPError as e:
        print(f"JSONBin load HTTP error {e.code}: {e.read().decode()}")
        return {}
    except Exception as e:
        print(f"Failed to load scores: {e}")
        return {}


def save_scores(scores: dict):
    if not JSONBIN_API_KEY or not JSONBIN_BIN_ID:
        return
    try:
        payload = json.dumps(scores, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(
            f"https://api.jsonbin.io/v3/b/{JSONBIN_BIN_ID}",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "X-Master-Key": JSONBIN_API_KEY
            },
            method="PUT"
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            print(f"Scores saved! Status: {resp.status}")
    except urllib.error.HTTPError as e:
        print(f"JSONBin save HTTP error {e.code}: {e.read().decode()}")
    except Exception as e:
        print(f"Failed to save scores: {e}")


def update_score(user_id: str, username: str, correct: bool, points_to_add: int = 10):
    scores = load_scores()
    if user_id not in scores:
        scores[user_id] = {"username": username, "points": 0, "correct": 0, "total": 0}
    scores[user_id]["username"] = username
    scores[user_id]["total"] += 1
    if correct:
        scores[user_id]["points"] += points_to_add
        scores[user_id]["correct"] += 1
    save_scores(scores)
    return scores[user_id]["points"]


def get_role_badge(points: int) -> str:
    if points >= 500:
        return "👑 Legend"
    elif points >= 200:
        return "⚡ Champion"
    elif points >= 50:
        return "📚 Scholar"
    return "🌱 Newcomer"


def build_scoreboard_embed(scores: dict) -> discord.Embed:
    embed = discord.Embed(
        title="🏆 Scoreboard",
        color=0xFFD700,
        timestamp=datetime.datetime.utcnow()
    )

    if not scores:
        embed.description = "No scores yet! Answer today's questions to get on the board."
        return embed

    sorted_scores = sorted(scores.values(), key=lambda x: x["points"], reverse=True)
    medals = ["🥇", "🥈", "🥉"]

    lines = []
    for i, s in enumerate(sorted_scores[:10]):
        rank = medals[i] if i < 3 else f"`{i+1}.`"
        acc = round(100 * s["correct"] / s["total"]) if s["total"] > 0 else 0
        badge = get_role_badge(s["points"])
        lines.append(
            f"{rank} **{s['username']}** {badge}\n"
            f"　`{s['points']} pts` · {acc}% accuracy · {s['total']} answered"
        )

    embed.description = "\n\n".join(lines)
    embed.set_footer(text="👑 Legend=500pts | ⚡ Champion=200pts | 📚 Scholar=50pts")
    return embed


# ─── QUESTION HELPERS ───────────────────────────────────────────────────────────

def pick_questions(count: int) -> list:
    # Try loading from questions.json first
    if os.path.exists("questions.json"):
        try:
            with open("questions.json", "r", encoding="utf-8") as f:
                external = json.load(f)
            if external:
                # Add type and subject defaults if missing
                for q in external:
                    if "type" not in q:
                        q["type"] = "mcq"
                    if "subject" not in q:
                        q["subject"] = "General"
                print(f"Loaded {len(external)} questions from questions.json")
                pool = external
                return random.sample(pool, min(count, len(pool)))
        except Exception as e:
            print(f"Failed to load questions.json: {e}, using built-in bank")
    return random.sample(QUESTION_BANK, min(count, len(QUESTION_BANK)))


# ─── DISCORD VIEWS ──────────────────────────────────────────────────────────────

class MCQView(discord.ui.View):
    def __init__(self, question: dict):
        super().__init__(timeout=ALIVE_MINUTES * 60)
        self.question = question
        self.answered_users = set()
        for label in ["A", "B", "C", "D"]:
            btn = discord.ui.Button(
                label=f"{label}: {question['options'][label]}",
                custom_id=label,
                style=discord.ButtonStyle.secondary
            )
            btn.callback = self.make_callback(label)
            self.add_item(btn)

    def make_callback(self, label: str):
        async def callback(interaction: discord.Interaction):
            try:
                user_id = str(interaction.user.id)
                username = interaction.user.display_name

                if user_id in self.answered_users:
                    await interaction.response.send_message(
                        "⚠️ তুমি এই প্রশ্নের উত্তর আগেই দিয়েছ!",
                        ephemeral=True
                    )
                    return

                self.answered_users.add(user_id)
                correct = self.question["answer"]
                is_correct = label == correct
                explanation = self.question.get("explanation", "")

                # Update score
                new_points = update_score(user_id, username, is_correct)
                badge = get_role_badge(new_points)

                if is_correct:
                    msg = (
                        f"✅ **সঠিক!** তুমি **{label}** বেছেছ।\n"
                        f"_{explanation}_\n\n"
                        f"**+10 pts!** তোমার মোট: `{new_points} pts` {badge}"
                    )
                else:
                    msg = (
                        f"❌ **ভুল।** তুমি **{label}** বেছেছ।\n"
                        f"সঠিক উত্তর: **{correct}** — {self.question['options'][correct]}\n"
                        f"_{explanation}_\n\n"
                        f"তোমার মোট: `{new_points} pts` {badge}"
                    )
                await interaction.response.send_message(msg, ephemeral=True)
            except discord.errors.NotFound:
                pass
            except Exception as e:
                print(f"Button error: {e}")
        return callback


class FlashcardView(discord.ui.View):
    def __init__(self, question: dict):
        super().__init__(timeout=ALIVE_MINUTES * 60)
        self.question = question
        self.answered_users = set()

    @discord.ui.button(label="👁 উত্তর দেখো", style=discord.ButtonStyle.primary)
    async def reveal(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            user_id = str(interaction.user.id)
            username = interaction.user.display_name

            already = user_id in self.answered_users
            self.answered_users.add(user_id)

            if not already:
                new_points = update_score(user_id, username, True, points_to_add=5)
            else:
                scores = load_scores()
                new_points = scores.get(user_id, {}).get("points", 0)
            badge = get_role_badge(new_points or 0)

            msg = (
                f"💡 **উত্তর:** {self.question['answer']}\n"
                f"_{self.question.get('explanation', '')}_"
            )
            if not already:
                badge = get_role_badge(new_points)
                msg += f"\n\n**+5 pts!** তোমার মোট: `{new_points} pts` {badge}"

            await interaction.response.send_message(msg, ephemeral=True)
        except discord.errors.NotFound:
            pass
        except Exception as e:
            print(f"Flashcard error: {e}")


# ─── QUIZ SESSION ────────────────────────────────────────────────────────────────

async def run_quiz_session(channel: discord.TextChannel):
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=6)  # BD time
    date_str = now.strftime("%d %B %Y")

    await channel.send(
        f"📚 **Daily Quiz — {date_str}**\n"
        f"🎯 আজকের {QUESTIONS_PER_SESSION}টি প্রশ্ন! সঠিক উত্তরে **+10 pts**, ফ্ল্যাশকার্ডে **+5 pts**\n"
        f"🔒 শুধু তুমিই দেখবে তোমার উত্তর সঠিক কিনা।\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    await asyncio.sleep(1)

    questions = pick_questions(QUESTIONS_PER_SESSION)

    for i, q in enumerate(questions, 1):
        subject_emoji = {"Physics":"⚡","Chemistry":"🧪","Math":"📐","Biology":"🧬"}.get(q["subject"], "📖")

        if q["type"] == "mcq":
            embed = discord.Embed(
                title=f"প্রশ্ন {i}/{len(questions)} — {subject_emoji} {q['subject']}",
                description=f"**{q['question']}**",
                color={"Physics":0x7c6aff,"Chemistry":0xff6a9b,"Math":0x6affb8,"Biology":0xfbbf24}.get(q["subject"], 0x7c6aff)
            )
            for label, text in q["options"].items():
                embed.add_field(name=label, value=text, inline=True)
            embed.set_footer(text="একটি বাটনে চাপো — শুধু তুমিই ফলাফল দেখবে!")
            await channel.send(embed=embed, view=MCQView(q))
        else:
            embed = discord.Embed(
                title=f"প্রশ্ন {i}/{len(questions)} — {subject_emoji} {q['subject']} (Flashcard)",
                description=f"**{q['question']}**",
                color=0xEB459E
            )
            embed.set_footer(text="উত্তর ভাবো, তারপর বাটন চাপো!")
            await channel.send(embed=embed, view=FlashcardView(q))

        await asyncio.sleep(1.5)

    await channel.send(
        f"✅ **আজকের প্রশ্ন শেষ!** উত্তর দিতে পারবে আগামী **{ALIVE_MINUTES//60} ঘণ্টা**।\n"
        "📊 স্কোরবোর্ড দেখতে নিচে অপেক্ষা করো..."
    )

    # Wait configured time then post scoreboard
    await asyncio.sleep(ALIVE_MINUTES * 60)
    await post_scoreboard(channel)


async def post_scoreboard(channel: discord.TextChannel):
    scores = load_scores()
    embed = build_scoreboard_embed(scores)
    await channel.send("📊 **আজকের সেশনের স্কোরবোর্ড:**", embed=embed)


# ─── BOT SETUP ───────────────────────────────────────────────────────────────────

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"✓ Logged in as {bot.user}")
    await bot.tree.sync()

    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print(f"✗ Channel {CHANNEL_ID} not found")
        await bot.close()
        return

    print(f"✓ Posting quiz to #{channel.name}")
    await run_quiz_session(channel)
    print("✓ Session complete. Shutting down.")
    await bot.close()


if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
