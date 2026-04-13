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

# ANSI color codes for Discord code blocks
class A:
    RESET  = "\u001b[0m"
    BOLD   = "\u001b[1m"
    GRAY   = "\u001b[30m"
    RED    = "\u001b[31m"
    GREEN  = "\u001b[32m"
    YELLOW = "\u001b[33m"
    BLUE   = "\u001b[34m"
    PINK   = "\u001b[35m"
    CYAN   = "\u001b[36m"
    WHITE  = "\u001b[37m"

# ─── QUESTION BANK ──────────────────────────────────────────────────────────────
QUESTION_BANK = [
    {"type":"mcq","subject":"Biology","question":"নিচের কোনটিতে হাইড্রার বহিঃকোষীয় পরিপাক সংঘটিত হয়?","options":{"A":"গ্যাস্ট্রোডার্মিস","B":"হাইপোস্টোম","C":"সিলেন্টেরন","D":"কর্ষিকা"},"answer":"C","explanation":"হাইড্রার সিলেন্টেরনে বহিঃকোষীয় পরিপাক ঘটে।"},
    {"type":"mcq","subject":"Biology","question":"কোষ বিভাজনের সময় কোষপ্লেট তৈরিতে সাহায্য করে কোন অঙ্গাণু?","options":{"A":"লাইসোসোম","B":"গলগি বস্তু","C":"মাইটোকন্ড্রিয়া","D":"রাইবোসোম"},"answer":"B","explanation":"গলগি বস্তু কোষ বিভাজনের সময় কোষপ্লেট গঠনে সাহায্য করে।"},
    {"type":"mcq","subject":"Biology","question":"রেস্ট্রিকশন এনজাইমের কাজ কী?","options":{"A":"DNA অণু বৃদ্ধিকরণ","B":"DNA খণ্ডকে জোড়া লাগানো","C":"নির্দিষ্ট জীবে রিকম্বিনেন্ট DNA প্রবেশ করানো","D":"কাঙ্ক্ষিত DNA কে নির্দিষ্ট স্থানে ছেদন করা"},"answer":"D","explanation":"রেস্ট্রিকশন এনজাইম নির্দিষ্ট স্থানে DNA ছেদন করে।"},
    {"type":"mcq","subject":"Biology","question":"কোন অ্যান্টিবডি প্রধান অ্যালার্জির সাথে সংশ্লিষ্ট?","options":{"A":"IgA","B":"IgM","C":"IgG","D":"IgE"},"answer":"D","explanation":"IgE অ্যান্টিবডি অ্যালার্জিক প্রতিক্রিয়ায় মুখ্য ভূমিকা রাখে।"},
    {"type":"mcq","subject":"Biology","question":"জেনেটিকভাবে নিয়ন্ত্রিত কোষের মৃত্যুকে কী বলে?","options":{"A":"অ্যাপোপটসিস","B":"নেক্রোসিস","C":"মেটাস্টেসিস","D":"অ্যাপোফাইসিস"},"answer":"A","explanation":"অ্যাপোপটসিস হলো প্রোগ্রামড সেল ডেথ।"},
    {"type":"mcq","subject":"Biology","question":"ভাইরাসের বংশবৃদ্ধিতে পোষকের কোন অঙ্গাণুতে প্রোটিন তৈরি হয়?","options":{"A":"নিউক্লিয়াস","B":"কোষ আবরণী","C":"রাইবোসোম","D":"মাইটোকন্ড্রিয়া"},"answer":"C","explanation":"ভাইরাসের প্রোটিন কোট পোষকের রাইবোসোমে তৈরি হয়।"},
    {"type":"mcq","subject":"Biology","question":"কোন ব্যাকটেরিয়া মুক্ত অক্সিজেন ছাড়া বাঁচে?","options":{"A":"Salmonella typhi","B":"Mycobacterium","C":"Clostridium","D":"Vibrio cholerae"},"answer":"C","explanation":"Clostridium বাধ্যতামূলক অবায়বীয়।"},
    {"type":"mcq","subject":"Biology","question":"কোন রক্তকণিকা 'cell-mediated immunity'-র সাথে সম্পর্কিত?","options":{"A":"ইওসিনোফিল","B":"টি-লিম্ফোসাইট","C":"নিউট্রোফিল","D":"বেসোফিল"},"answer":"B","explanation":"টি-লিম্ফোসাইট সেল-মিডিয়েটেড ইমিউনিটির মূল কোষ।"},
    {"type":"mcq","subject":"Biology","question":"হিমোগ্লোবিনের কোন অংশে CO₂ যুক্ত হয়?","options":{"A":"−OH","B":"−COOH","C":"−HCO₃","D":"−NH₂"},"answer":"D","explanation":"CO₂, হিমোগ্লোবিনের −NH₂ গ্রুপের সাথে যুক্ত হয়ে কার্বামিনোহিমোগ্লোবিন তৈরি করে।"},
    {"type":"mcq","subject":"Biology","question":"ম্যালেরিয়া রোগীর রক্তশূন্যতার প্রধান কারণ কোনটি?","options":{"A":"প্লীহা নিঃসৃত lysolecithin দ্বারা ধ্বংস","B":"এরিথ্রোসাইটিক সাইজোগনি চক্রে লোহিত কণিকা ধ্বংস","C":"Haemolysin এন্টিবডি দ্বারা ধ্বংস","D":"পুষ্টির অভাবে রক্তকণিকা তৈরি হয় না"},"answer":"B","explanation":"এরিথ্রোসাইটিক সাইজোগনি চক্রে প্লাজমোডিয়াম লোহিত কণিকা ভেঙে বের হয়।"},
    {"type":"mcq","subject":"Biology","question":"কোষ চক্রের কোন দশায় DNA সংশ্লেষণ ঘটে?","options":{"A":"M দশায়","B":"G₁ দশায়","C":"S দশায়","D":"G₂ দশায়"},"answer":"C","explanation":"S (Synthesis) দশায় DNA প্রতিলিপি তৈরি হয়।"},
    {"type":"mcq","subject":"Biology","question":"ট্রান্সজেনিক সয়াবিনের বৈশিষ্ট্য কোনটি?","options":{"A":"কীটপতঙ্গ ও ভাইরাস প্রতিরোধী","B":"আগাছানাশক সহনশীল","C":"ভিটামিন সমৃদ্ধ","D":"উচ্চ অলিয়েক অ্যাসিড সমৃদ্ধ"},"answer":"B","explanation":"ট্রান্সজেনিক সয়াবিন হার্বিসাইড সহনশীল।"},
    {"type":"mcq","subject":"Chemistry","question":"18°C তাপমাত্রায় 0.8 atm চাপে একটি গ্যাসের ঘনত্ব 2.25 gL⁻¹ হলে আণবিক ভর কত?","options":{"A":"36.63 g mol⁻¹","B":"36.24 g mol⁻¹","C":"24.36 g mol⁻¹","D":"67.11 g mol⁻¹"},"answer":"A","explanation":"PV=nRT ব্যবহার করে M = dRT/P ≈ 36.63 g/mol"},
    {"type":"mcq","subject":"Chemistry","question":"250 mL 0.1 M Na₂CO₃ দ্রবণ প্রস্তুতে কত গ্রাম Na₂CO₃ দরকার?","options":{"A":"10.6 g","B":"1.60 g","C":"2.65 g","D":"26.5 g"},"answer":"C","explanation":"মোল = 0.1×0.25 = 0.025; ভর = 0.025×106 = 2.65 g"},
    {"type":"mcq","subject":"Chemistry","question":"কোন যৌগটি জলীয় NaOH এর সাথে বিক্রিয়া করে না?","options":{"A":"C₂H₅OH","B":"C₂H₅COOH","C":"C₆H₅COOH","D":"C₆H₅OH"},"answer":"A","explanation":"ইথানল অত্যন্ত দুর্বল অ্যাসিড, NaOH এর সাথে উল্লেখযোগ্য বিক্রিয়া করে না।"},
    {"type":"mcq","subject":"Chemistry","question":"কোন দ্রবণের OH⁻ আয়নের ঘনমাত্রা 3.5×10⁻⁴ M হলে pH কত?","options":{"A":"12.50","B":"13.55","C":"10.54","D":"3.55"},"answer":"C","explanation":"pOH = -log(3.5×10⁻⁴) ≈ 3.46; pH = 14-3.46 = 10.54"},
    {"type":"mcq","subject":"Chemistry","question":"10% Na₂CO₃ দ্রবণের মোলারিটি কত?","options":{"A":"0.95","B":"9.15","C":"1.94","D":"0.94"},"answer":"D","explanation":"M = (10/106)/(100/1000) ≈ 0.94 M"},
    {"type":"mcq","subject":"Chemistry","question":"ইথাইল অ্যালকোহল ও অ্যালকোহলিক KOH বিক্রিয়ায় কোনটি উৎপন্ন হয়?","options":{"A":"ethene","B":"ethane","C":"ethyne","D":"ethanol"},"answer":"A","explanation":"অ্যালকোহলিক KOH ইলিমিনেশন বিক্রিয়ায় ইথিন উৎপন্ন করে।"},
    {"type":"mcq","subject":"Chemistry","question":"সমায়তনের 0.1M NaOH ও 0.1M H₂SO₄ মিশ্রণ কী ধরনের?","options":{"A":"উভধর্মী","B":"নিরপেক্ষ","C":"অম্লীয়","D":"ক্ষারীয়"},"answer":"C","explanation":"H₂SO₄ দ্বিক্ষারীয়, তাই সমআয়তনে NaOH কম পড়ে — অম্লীয়।"},
    {"type":"mcq","subject":"Chemistry","question":"35°C পানিতে O₂ এর দ্রাব্যতা 2.3×10⁻⁴ M হলে ppm তা কত?","options":{"A":"6.90","B":"0.74","C":"7.01","D":"7.36"},"answer":"D","explanation":"ppm = 2.3×10⁻⁴ × 32 × 1000 = 7.36 ppm"},
    {"type":"mcq","subject":"Chemistry","question":"Ca(OCl)Cl যৌগে Cl এর oxidation number কত?","options":{"A":"-1,-1","B":"+1,-2","C":"+1,-1","D":"-1,+2"},"answer":"C","explanation":"ব্লিচিং পাউডারে OCl⁻ এ Cl=+1 এবং Cl⁻=−1।"},
    {"type":"mcq","subject":"Physics","question":"ফোকাস দূরত্ব 1000 cm হলে উত্তল লেন্সের ক্ষমতা কত?","options":{"A":"+10 D","B":"+100 D","C":"+0.1 D","D":"-0.1 D"},"answer":"C","explanation":"P = 1/f(m) = 1/10 = +0.1 D"},
    {"type":"mcq","subject":"Physics","question":"সুষম ত্বরণে চলা বস্তুর ৪র্থ ও ৩য় সেকেন্ডে অতিক্রান্ত দূরত্বের অনুপাত?","options":{"A":"26:9","B":"4:3","C":"7:5","D":"2:1"},"answer":"C","explanation":"nth সেকেন্ডে দূরত্ব ∝ (2n-1); ৪র্থ=7k, ৩য়=5k; অনুপাত=7:5"},
    {"type":"mcq","subject":"Physics","question":"একটি বস্তু 4.9 ms⁻¹ বেগে খাড়া উপরে নিক্ষিপ্ত হলে কত সময় শূন্যে থাকবে?","options":{"A":"2 সেকেন্ড","B":"1 সেকেন্ড","C":"4 সেকেন্ড","D":"3 সেকেন্ড"},"answer":"B","explanation":"মোট সময় = 2u/g = 2×4.9/9.8 = 1 সেকেন্ড"},
    {"type":"mcq","subject":"Physics","question":"দুটি ভেক্টর 8 ও 6 একক, 30° কোণে ক্রিয়াশীল হলে ভেক্টর গুণফল কত?","options":{"A":"16","B":"20","C":"48","D":"24"},"answer":"D","explanation":"A×B = |A||B|sinθ = 8×6×sin30° = 24"},
    {"type":"mcq","subject":"Physics","question":"গ্যালভানোমিটারের সাথে শান্ট ব্যবহারের উদ্দেশ্য?","options":{"A":"বিদ্যুৎ প্রবাহ কমানো","B":"বিদ্যুৎ প্রবাহ বাড়ানো","C":"বিভব পার্থক্য কমানো","D":"বিভব পার্থক্য বাড়ানো"},"answer":"A","explanation":"শান্ট রেজিস্ট্যান্স অতিরিক্ত তড়িৎ প্রবাহ সরিয়ে দেয়।"},
    {"type":"mcq","subject":"Physics","question":"তাপীয় ইঞ্জিন ও রেফ্রিজারেটর কোন সূত্রের উপর নির্ভর করে?","options":{"A":"তাপগতিবিদ্যার তৃতীয় সূত্র","B":"তাপগতিবিদ্যার দ্বিতীয় সূত্র","C":"তাপগতিবিদ্যার প্রথম সূত্র","D":"তাপগতিবিদ্যার শূন্যতম সূত্র"},"answer":"B","explanation":"তাপগতিবিদ্যার দ্বিতীয় সূত্র তাপ ইঞ্জিন ও রেফ্রিজারেটরের ভিত্তি।"},
    {"type":"mcq","subject":"Physics","question":"কোন তাপমাত্রায় সেলসিয়াস ও ফারেনহাইট একই মান দেখায়?","options":{"A":"-40°","B":"32°","C":"40°","D":"-32°"},"answer":"A","explanation":"C=F হলে, C = 9C/5+32 → C = -40°"},
    {"type":"mcq","subject":"Physics","question":"100m ট্রেন 45 kmh⁻¹ বেগে 1 km ব্রিজ পার হতে কত সময় লাগবে?","options":{"A":"88 সেকেন্ড","B":"18 সেকেন্ড","C":"80 সেকেন্ড","D":"24 সেকেন্ড"},"answer":"A","explanation":"মোট দূরত্ব=1100m; বেগ=12.5m/s; সময়=88s"},
    {"type":"mcq","subject":"Physics","question":"ভূপৃষ্ঠ হতে 1000 km উচ্চতে অভিকর্ষ ত্বরণ কত?","options":{"A":"8.1 ms⁻²","B":"3.8 ms⁻²","C":"7.33 ms⁻²","D":"9.8 ms⁻²"},"answer":"C","explanation":"g' = g(R/(R+h))² = 9.8×(6400/7400)² ≈ 7.33 ms⁻²"},
    {"type":"mcq","subject":"English","question":"Active form of: 'My book has been lost by me.'","options":{"A":"I had lost my book.","B":"I lost my book.","C":"I have lost my book.","D":"A book of mine is lost."},"answer":"C","explanation":"Present perfect passive → active: 'I have lost my book.'"},
    {"type":"mcq","subject":"English","question":"Synonym of 'anarchy'—","options":{"A":"serenity","B":"placidity","C":"lawlessness","D":"discipline"},"answer":"C","explanation":"Anarchy = a state of disorder/lawlessness."},
    {"type":"mcq","subject":"English","question":"Antonym of 'impediment'—","options":{"A":"useful","B":"hindrance","C":"obstacle","D":"helpful"},"answer":"D","explanation":"Impediment = obstacle; antonym = helpful."},
    {"type":"mcq","subject":"English","question":"'Keep your chin up' means—","options":{"A":"be cheerful","B":"be careful","C":"be brave","D":"be smart"},"answer":"A","explanation":"'Keep your chin up' = stay positive/be cheerful."},
    {"type":"mcq","subject":"English","question":"'Call it a day' means—","options":{"A":"finish work","B":"fix an appointment","C":"spend time","D":"open an event"},"answer":"A","explanation":"'Call it a day' = stop working for the day."},
    {"type":"mcq","subject":"GK","question":"বাংলাদেশের ১০০ টাকার নোটে কোন মসজিদের ছবি আছে?","options":{"A":"মডেল মসজিদ","B":"ষাট গম্বুজ মসজিদ","C":"আতিয়া মসজিদ","D":"তারা মসজিদ"},"answer":"B","explanation":"১০০ টাকার নোটে ষাট গম্বুজ মসজিদ।"},
    {"type":"mcq","subject":"GK","question":"বৈষম্যবিরোধী আন্দোলনে আবু সাইদ কবে শহীদ হন?","options":{"A":"২১ জুলাই ২০২৪","B":"১৬ জুলাই ২০২৪","C":"২০ জুলাই ২০২৪","D":"১৫ জুলাই ২০২৪"},"answer":"B","explanation":"আবু সাইদ ১৬ জুলাই ২০২৪ সালে শহীদ হন।"},
    {"type":"mcq","subject":"GK","question":"WHO কালাজ্বরমুক্ত দেশ হিসেবে বাংলাদেশকে স্বীকৃতি দেয় কবে?","options":{"A":"৩০ সেপ্টেম্বর ২০২৩","B":"৩১ অক্টোবর ২০২৩","C":"০১ নভেম্বর ২০২৩","D":"৩০ নভেম্বর ২০২৩"},"answer":"B","explanation":"৩১ অক্টোবর ২০২৩ সালে WHO এই স্বীকৃতি দেয়।"},
    {"type":"mcq","subject":"GK","question":"ঢাকা মেডিকেল কলেজ প্রতিষ্ঠিত হয় কোন সালে?","options":{"A":"১৯৪৫","B":"১৯৩৫","C":"১৯৫২","D":"১৯৪৬"},"answer":"A","explanation":"ঢাকা মেডিকেল কলেজ ১৯৪৫ সালে প্রতিষ্ঠিত।"},
    {"type":"mcq","subject":"GK","question":"মুক্তিযুদ্ধকালীন সর্বদলীয় উপদেষ্টা কমিটির চেয়ারম্যান কে ছিলেন?","options":{"A":"সৈয়দ নজরুল ইসলাম","B":"তাজউদ্দিন আহমদ","C":"কমরেড মণি সিংহ","D":"মৌলানা ভাসানী"},"answer":"D","explanation":"মৌলানা ভাসানী এই কমিটির চেয়ারম্যান ছিলেন।"},
]
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
    "Physics":   {"emoji": "⚡", "color": 0x5865F2, "label": "PHYSICS"},
    "Chemistry": {"emoji": "⚗️", "color": 0xED4245, "label": "CHEMISTRY"},
    "Math":      {"emoji": "∑",  "color": 0x57F287, "label": "MATHEMATICS"},
    "Biology":   {"emoji": "🔬", "color": 0xFEE75C, "label": "BIOLOGY"},
    "English":   {"emoji": "📖", "color": 0x00B4FF, "label": "ENGLISH"},
    "GK":        {"emoji": "🌐", "color": 0xFF8C00, "label": "GENERAL KNOWLEDGE"},
}

def get_subject(subject: str) -> dict:
    return SUBJECT_META.get(subject, {"emoji": "📋", "color": 0x5865F2, "label": subject.upper()})

def get_rank_title(points: int) -> str:
    if points >= 1000: return "ELITE"
    elif points >= 500: return "LEGEND"
    elif points >= 200: return "CHAMPION"
    elif points >= 100: return "SCHOLAR"
    elif points >= 50:  return "APPRENTICE"
    return "ROOKIE"

def get_rank_badge(points: int) -> str:
    if points >= 1000: return "💎"
    elif points >= 500: return "👑"
    elif points >= 200: return "🔥"
    elif points >= 100: return "⚡"
    elif points >= 50:  return "📚"
    return "🌱"

def ansi(text: str) -> str:
    """Wrap in ANSI code block for Discord."""
    return f"```ansi\n{text}\n```"

def build_scoreboard_embed(scores: dict) -> discord.Embed:
    now_bd = datetime.datetime.utcnow() + datetime.timedelta(hours=6)

    if not scores:
        embed = discord.Embed(color=0x2B2D31, timestamp=datetime.datetime.utcnow())
        embed.description = ansi(
            f"{A.GRAY}┌{'─'*36}┐\n"
            f"│{'NO PARTICIPANTS TODAY':^36}│\n"
            f"└{'─'*36}┘{A.RESET}"
        )
        return embed

    sorted_scores = sorted(scores.values(), key=lambda x: x["points"], reverse=True)
    max_pts = max(s["points"] for s in sorted_scores) or 1

    embed = discord.Embed(
        color=0xFFD700,
        timestamp=datetime.datetime.utcnow()
    )

    # Header
    top = sorted_scores[0]
    top_acc = round(100*top["correct"]/top["total"]) if top["total"] > 0 else 0
    header = (
        f"{A.YELLOW}{A.BOLD}{'LEADERBOARD':^38}{A.RESET}\n"
        f"{A.GRAY}{now_bd.strftime('%d %B %Y  ·  %H:%M')}{A.RESET}\n"
        f"{A.GRAY}{'─'*38}{A.RESET}\n"
        f"{A.YELLOW}  CHAMPION  {A.RESET}{A.BOLD}{top['username']}{A.RESET}\n"
        f"{A.GRAY}  {top['points']} pts  ·  {top_acc}% accuracy{A.RESET}\n"
        f"{A.GRAY}{'─'*38}{A.RESET}"
    )
    embed.description = ansi(header)

    # Rank rows
    rank_nums = ["01","02","03","04","05","06","07","08","09","10"]
    rows = []
    for i, s in enumerate(sorted_scores[:10]):
        acc = round(100*s["correct"]/s["total"]) if s["total"] > 0 else 0
        badge = get_rank_badge(s["points"])
        num = rank_nums[i] if i < len(rank_nums) else f"{i+1:02d}"
        filled = round((s["points"]/max_pts)*12)
        bar = "█"*filled + "░"*(12-filled)
        name_col = s["username"][:18].ljust(18)

        if i == 0:
            color = A.YELLOW + A.BOLD
        elif i == 1:
            color = A.WHITE
        elif i == 2:
            color = A.CYAN
        else:
            color = A.GRAY

        rows.append(
            f"{color}{num}  {name_col}  {bar}  {s['points']:>5} pts{A.RESET}"
        )

    embed.add_field(name="Rankings", value=ansi("\n".join(rows)), inline=False)

    # Stats
    total_p = len(sorted_scores)
    total_a = sum(s["total"] for s in sorted_scores)
    avg_acc = round(sum(100*s["correct"]/s["total"] for s in sorted_scores if s["total"]>0)/max(total_p,1))
    stats = (
        f"{A.GRAY}Players  {A.RESET}{A.WHITE}{total_p:>4}{A.RESET}   "
        f"{A.GRAY}Answers  {A.RESET}{A.WHITE}{total_a:>4}{A.RESET}   "
        f"{A.GRAY}Avg Acc  {A.RESET}{A.WHITE}{avg_acc:>3}%{A.RESET}"
    )
    embed.add_field(name="Session Stats", value=ansi(stats), inline=False)
    embed.set_footer(text="💎1000  👑500  🔥200  ⚡100  📚50  🌱0")
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
    return pool[:count]


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

                if user_id in self.user_start_times:
                    elapsed = (now - self.user_start_times[user_id]).total_seconds()
                    if elapsed > PERSONAL_TIMER_MIN * 60:
                        e = discord.Embed(
                            description=ansi(f"{A.RED}TIME EXPIRED\n{A.GRAY}Your {PERSONAL_TIMER_MIN}-minute window has closed.{A.RESET}"),
                            color=0x2B2D31
                        )
                        await interaction.response.send_message(embed=e, ephemeral=True)
                        return

                if user_id in self.answered_users:
                    e = discord.Embed(
                        description=ansi(f"{A.YELLOW}ALREADY ANSWERED\n{A.GRAY}You have already responded to this question.{A.RESET}"),
                        color=0x2B2D31
                    )
                    await interaction.response.send_message(embed=e, ephemeral=True)
                    return

                if user_id not in self.user_start_times:
                    self.user_start_times[user_id] = now

                self.answered_users.add(user_id)
                correct = self.question["answer"]
                is_correct = label == correct
                explanation = self.question.get("explanation", "")
                new_points = await update_score(user_id, username, is_correct)
                rank_title = get_rank_title(new_points)
                rank_badge = get_rank_badge(new_points)

                if is_correct:
                    body = (
                        f"{A.GREEN}{A.BOLD}  CORRECT{A.RESET}\n"
                        f"{A.GRAY}{'─'*36}{A.RESET}\n"
                        f"{A.WHITE}  {label}.  {self.question['options'][label]}{A.RESET}\n"
                        f"{A.GRAY}{'─'*36}{A.RESET}\n"
                        + (f"{A.GRAY}  {explanation}{A.RESET}\n{A.GRAY}{'─'*36}{A.RESET}\n" if explanation else "")
                        + f"{A.GREEN}  +10 pts{A.RESET}   {A.WHITE}{new_points} total{A.RESET}   {A.GRAY}{rank_title}{A.RESET}"
                    )
                    e = discord.Embed(description=ansi(body), color=0x57F287)
                else:
                    body = (
                        f"{A.RED}{A.BOLD}  INCORRECT{A.RESET}\n"
                        f"{A.GRAY}{'─'*36}{A.RESET}\n"
                        f"{A.GRAY}  Your answer:   {label}.  {self.question['options'][label]}{A.RESET}\n"
                        f"{A.GREEN}  Correct:       {correct}.  {self.question['options'][correct]}{A.RESET}\n"
                        f"{A.GRAY}{'─'*36}{A.RESET}\n"
                        + (f"{A.GRAY}  {explanation}{A.RESET}\n{A.GRAY}{'─'*36}{A.RESET}\n" if explanation else "")
                        + f"{A.GRAY}  {new_points} pts total   {rank_title}{A.RESET}"
                    )
                    e = discord.Embed(description=ansi(body), color=0xED4245)

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
                    e = discord.Embed(
                        description=ansi(f"{A.RED}TIME EXPIRED{A.RESET}"),
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
            rank_title = get_rank_title(new_points or 0)

            body = (
                f"{A.CYAN}{A.BOLD}  ANSWER{A.RESET}\n"
                f"{A.GRAY}{'─'*36}{A.RESET}\n"
                f"{A.WHITE}  {self.question['answer']}{A.RESET}\n"
                f"{A.GRAY}{'─'*36}{A.RESET}\n"
                + (f"{A.GRAY}  {self.question['explanation']}{A.RESET}\n{A.GRAY}{'─'*36}{A.RESET}\n" if self.question.get("explanation") else "")
                + (f"{A.CYAN}  +5 pts{A.RESET}   {A.WHITE}{new_points} total{A.RESET}   {A.GRAY}{rank_title}{A.RESET}" if not already
                   else f"{A.GRAY}  {new_points} pts total   {rank_title}{A.RESET}")
            )
            e = discord.Embed(description=ansi(body), color=0x5865F2)
            await interaction.response.send_message(embed=e, ephemeral=True)
        except discord.errors.NotFound:
            pass
        except Exception as ex:
            print(f"Flashcard error: {ex}")


# ─── QUIZ SESSION ────────────────────────────────────────────────────────────────

async def run_quiz_session(channel: discord.TextChannel):
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=6)
    date_str = now.strftime("%d %B %Y")

    # Opening card
    header_text = (
        f"{A.WHITE}{A.BOLD}{'DAILY QUIZ':^38}{A.RESET}\n"
        f"{A.GRAY}{date_str:^38}{A.RESET}\n"
        f"{A.GRAY}{'─'*38}{A.RESET}\n"
        f"{A.GRAY}  Questions     {A.RESET}{A.WHITE}{QUESTIONS_PER_SESSION}{A.RESET}\n"
        f"{A.GRAY}  MCQ           {A.RESET}{A.WHITE}+10 pts{A.RESET}\n"
        f"{A.GRAY}  Flashcard     {A.RESET}{A.WHITE}+5 pts{A.RESET}\n"
        f"{A.GRAY}  Timer         {A.RESET}{A.WHITE}{PERSONAL_TIMER_MIN} min from first tap{A.RESET}\n"
        f"{A.GRAY}{'─'*38}{A.RESET}\n"
        f"{A.GRAY}  Your answers are visible only to you.{A.RESET}"
    )
    announce = discord.Embed(description=ansi(header_text), color=0x5865F2)
    await channel.send(embed=announce)
    await asyncio.sleep(1.5)

    questions = pick_questions(QUESTIONS_PER_SESSION)

    for i, q in enumerate(questions, 1):
        meta = get_subject(q.get("subject", "General"))

        if q["type"] == "mcq":
            embed = discord.Embed(title=q["question"], color=meta["color"])
            embed.set_author(name=f"{meta['emoji']}  {meta['label']}  ·  Q{i} of {len(questions)}")
            embed.add_field(name="A", value=q["options"]["A"], inline=True)
            embed.add_field(name="B", value=q["options"]["B"], inline=True)
            embed.add_field(name="C", value=q["options"]["C"], inline=True)
            embed.add_field(name="D", value=q["options"]["D"], inline=True)
            embed.set_footer(text=f"Timer starts on first tap  ·  {PERSONAL_TIMER_MIN} min window  ·  Only you see your result")
            await channel.send(embed=embed, view=MCQView(q))
        else:
            embed = discord.Embed(title=q["question"], color=meta["color"])
            embed.set_author(name=f"{meta['emoji']}  {meta['label']}  ·  FLASHCARD  {i}/{len(questions)}")
            embed.set_footer(text="Think of your answer, then tap Reveal")
            await channel.send(embed=embed, view=FlashcardView(q))

        await asyncio.sleep(1.5)

    # Closing
    close_text = (
        f"{A.GRAY}{'─'*38}{A.RESET}\n"
        f"{A.WHITE}  All questions posted.{A.RESET}\n"
        f"{A.GRAY}  Tap any button to start your {PERSONAL_TIMER_MIN}-min window.\n"
        f"  Leaderboard posts in {ALIVE_MINUTES} minutes.{A.RESET}\n"
        f"{A.GRAY}{'─'*38}{A.RESET}"
    )
    closing = discord.Embed(description=ansi(close_text), color=0x2B2D31)
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
