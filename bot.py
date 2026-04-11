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
DISCORD_TOKEN   = os.environ.get("DISCORD_TOKEN")
CHANNEL_ID      = int(os.environ.get("CHANNEL_ID", "0"))
GIST_TOKEN      = os.environ.get("GIST_TOKEN")   # GitHub personal access token
GIST_ID         = os.environ.get("GIST_ID")      # Gist ID
QUESTIONS_PER_SESSION = 10
ALIVE_MINUTES   = 60  # 1 hour = fits whole month in GitHub free tier
# ────────────────────────────────────────────────────────────────────────────────

# ─── QUESTION BANK ─────────────────────────────────────────────────────────────
QUESTION_BANK = [
    # ── MEDICAL COLLEGE ENTRANCE (Hard) ──────────────────────────────────────────
    # Biology - Hard
    {"type":"mcq","subject":"Biology","question":"নিচের কোনটিতে হাইড্রার বহিঃকোষীয় পরিপাক সংঘটিত হয়?","options":{"A":"গ্যাস্ট্রোডার্মিস","B":"হাইপোস্টোম","C":"সিলেন্টেরন","D":"কর্ষিকা"},"answer":"C","explanation":"হাইড্রার সিলেন্টেরনে বহিঃকোষীয় পরিপাক ঘটে।"},
    {"type":"mcq","subject":"Biology","question":"কোষ বিভাজনের সময় কোষপ্লেট তৈরিতে সাহায্য করে কোন অঙ্গাণু?","options":{"A":"লাইসোসোম","B":"গলগি বস্তু","C":"মাইটোকন্ড্রিয়া","D":"রাইবোসোম"},"answer":"B","explanation":"গলগি বস্তু কোষ বিভাজনের সময় কোষপ্লেট গঠনে সাহায্য করে।"},
    {"type":"mcq","subject":"Biology","question":"রেস্ট্রিকশন এনজাইমের কাজ কী?","options":{"A":"DNA অণু বৃদ্ধিকরণ","B":"DNA খণ্ডকে জোড়া লাগানো","C":"নির্দিষ্ট জীবে রিকম্বিনেন্ট DNA প্রবেশ করানো","D":"কাঙ্ক্ষিত DNA কে নির্দিষ্ট স্থানে ছেদন করা"},"answer":"D","explanation":"রেস্ট্রিকশন এনজাইম নির্দিষ্ট স্থানে DNA ছেদন করে — জেনেটিক ইঞ্জিনিয়ারিংয়ের মূল হাতিয়ার।"},
    {"type":"mcq","subject":"Biology","question":"কোন অ্যান্টিবডি প্রধান অ্যালার্জির সাথে সংশ্লিষ্ট?","options":{"A":"IgA","B":"IgM","C":"IgG","D":"IgE"},"answer":"D","explanation":"IgE অ্যান্টিবডি অ্যালার্জিক প্রতিক্রিয়া ও পরজীবী সংক্রমণে মুখ্য ভূমিকা রাখে।"},
    {"type":"mcq","subject":"Biology","question":"জেনেটিকভাবে নিয়ন্ত্রিত কোষের মৃত্যুকে কী বলে?","options":{"A":"অ্যাপোপটসিস","B":"নেক্রোসিস","C":"মেটাস্টেসিস","D":"অ্যাপোফাইসিস"},"answer":"A","explanation":"অ্যাপোপটসিস হলো প্রোগ্রামড সেল ডেথ — জেনেটিকভাবে নিয়ন্ত্রিত স্বাভাবিক কোষ মৃত্যু।"},
    {"type":"mcq","subject":"Biology","question":"ভাইরাসের বংশবৃদ্ধিতে গোষকের কোন অঙ্গাণুতে প্রোটিন তৈরি হয়?","options":{"A":"নিউক্লিয়াস","B":"কোষ আবরণী","C":"রাইবোসোম","D":"মাইটোকন্ড্রিয়া"},"answer":"C","explanation":"ভাইরাসের প্রোটিন কোট পোষকের রাইবোসোমে তৈরি হয়।"},
    {"type":"mcq","subject":"Biology","question":"কোন ব্যাকটেরিয়া মুক্ত অক্সিজেন ছাড়া বাঁচে?","options":{"A":"Salmonella typhi","B":"Mycobacterium","C":"Clostridium","D":"Vibrio cholerae"},"answer":"C","explanation":"Clostridium বাধ্যতামূলক অবায়বীয় — মুক্ত অক্সিজেন ছাড়া বাঁচে।"},
    {"type":"mcq","subject":"Biology","question":"কোন রক্ত কণিকা 'cell-mediated immunity'-র সাথে সম্পর্কিত?","options":{"A":"ইওসিনোফিল","B":"টি-লিম্ফোসাইট","C":"নিউট্রোফিল","D":"বেসোফিল"},"answer":"B","explanation":"টি-লিম্ফোসাইট সেল-মিডিয়েটেড ইমিউনিটির মূল কোষ।"},
    {"type":"mcq","subject":"Biology","question":"হিমোগ্লোবিনের কোন অংশে CO₂ যুক্ত হয়?","options":{"A":"−OH","B":"−COOH","C":"−HCO₃","D":"−NH₂"},"answer":"D","explanation":"CO₂ হিমোগ্লোবিনের −NH₂ (অ্যামিনো) গ্রুপের সাথে যুক্ত হয়ে কার্বামিনোহিমোগ্লোবিন তৈরি করে।"},
    {"type":"mcq","subject":"Biology","question":"ম্যালেরিয়া রোগীর রক্তশূন্যতার প্রধান কারণ কোনটি?","options":{"A":"প্লীহা নিঃসৃত lysolecithin দ্বারা লোহিত কণিকা ধ্বংস","B":"এরিথ্রোসাইটিক সাইজোগনি চক্রে লোহিত কণিকা ধ্বংস","C":"Haemolysin এন্টিবডি দ্বারা লোহিত কণিকা ধ্বংস","D":"পুষ্টির অভাবে রক্তকণিকা তৈরি হয় না"},"answer":"B","explanation":"এরিথ্রোসাইটিক সাইজোগনি চক্রে প্লাজমোডিয়াম লোহিত কণিকা ভেঙে বের হয়, ফলে রক্তশূন্যতা হয়।"},
    {"type":"mcq","subject":"Biology","question":"কোষ চক্রের কোন দশায় DNA সংশ্লেষণ ঘটে?","options":{"A":"M দশায","B":"G₁ দশায়","C":"S দশায়","D":"G₂ দশায়"},"answer":"C","explanation":"S (Synthesis) দশায় DNA প্রতিলিপি তৈরি হয়।"},
    {"type":"mcq","subject":"Biology","question":"ট্রান্সজেনিক সয়াবিনের বৈশিষ্ট্য কোনটি?","options":{"A":"কীটপতঙ্গ ও ভাইরাস প্রতিরোধী","B":"আগাছানাশক সহনশীল","C":"ভিটামিন সমৃদ্ধ","D":"উচ্চ অলিয়েক অ্যাসিড সমৃদ্ধ"},"answer":"B","explanation":"ট্রান্সজেনিক সয়াবিন হার্বিসাইড (আগাছানাশক) সহনশীল করা হয়েছে।"},

    # Chemistry - Hard
    {"type":"mcq","subject":"Chemistry","question":"18°C তাপমাত্রায় 0.8 atm চাপে একটি গ্যাসের ঘনত্ব 2.25gL⁻¹ হলে এর আণবিক ভর কত?","options":{"A":"36.63 g mol⁻¹","B":"36.24 g mol⁻¹","C":"24.36 g mol⁻¹","D":"67.11 g mol⁻¹"},"answer":"A","explanation":"PV=nRT ব্যবহার করে: M = dRT/P = 2.25×8.314×291/(0.8×101325) ≈ 36.63 g/mol"},
    {"type":"mcq","subject":"Chemistry","question":"250 mL 0.1 M Na₂CO₃ দ্রবণ প্রস্তুত করতে কত গ্রাম Na₂CO₃ দরকার?","options":{"A":"10.6 g","B":"1.60 g","C":"2.65 g","D":"26.5 g"},"answer":"C","explanation":"মোল = 0.1 × 0.25 = 0.025 mol; ভর = 0.025 × 106 = 2.65 g"},
    {"type":"mcq","subject":"Chemistry","question":"কোন যৌগটি জলীয় NaOH এর সাথে বিক্রিয়া করে না?","options":{"A":"C₂H₅OH","B":"C₂H₅COOH","C":"C₆H₅COOH","D":"C₆H₅OH"},"answer":"A","explanation":"ইথানল (C₂H₅OH) অত্যন্ত দুর্বল অ্যাসিড, NaOH এর সাথে উল্লেখযোগ্য বিক্রিয়া করে না।"},
    {"type":"mcq","subject":"Chemistry","question":"কোন দ্রবণের OH⁻ আয়নের ঘনমাত্রা 3.5×10⁻⁴ M হলে তার pH কত?","options":{"A":"12.50","B":"13.55","C":"10.54","D":"3.55"},"answer":"C","explanation":"pOH = -log(3.5×10⁻⁴) ≈ 3.46; pH = 14 - 3.46 = 10.54"},
    {"type":"mcq","subject":"Chemistry","question":"10% Na₂CO₃ দ্রবণের মোলারিটি কত?","options":{"A":"0.95","B":"9.15","C":"1.94","D":"0.94"},"answer":"D","explanation":"10g Na₂CO₃ প্রতি 100g দ্রবণে; ঘনত্ব≈1g/mL ধরলে, M = (10/106)/(100/1000) = 0.943 ≈ 0.94 M"},
    {"type":"mcq","subject":"Chemistry","question":"ইথাইল অ্যালকোহল ও KOH(aq) এর বিক্রিয়ায় কোনটি উৎপন্ন হয়?","options":{"A":"ethene","B":"ethane","C":"ethyne","D":"ethanol"},"answer":"A","explanation":"অ্যালকোহলিক KOH ইলিমিনেশন বিক্রিয়ায় ইথিন উৎপন্ন করে।"},
    {"type":"mcq","subject":"Chemistry","question":"ফরমালডিহাইড এবং পটাশিয়াম একসাথে উত্তপ্ত করলে কী পাওয়া যায়?","options":{"A":"ethyl formate","B":"methyl alcohol","C":"methane","D":"acetylene"},"answer":"B","explanation":"HCHO + 2[H] → CH₃OH (মিথাইল অ্যালকোহল), পটাশিয়াম বিজারক হিসেবে কাজ করে।"},
    {"type":"mcq","subject":"Chemistry","question":"সমায়তনের 0.1M NaOH এবং 0.1M H₂SO₄ মিশ্রণের প্রকৃতি কিরূপ হবে?","options":{"A":"উভধর্মী","B":"নিরপেক্ষ","C":"অম্লীয়","D":"ক্ষারীয়"},"answer":"C","explanation":"H₂SO₄ দ্বিক্ষারীয়, তাই সমআয়তনে NaOH কম পড়ে — মিশ্রণ অম্লীয় হয়।"},
    {"type":"mcq","subject":"Chemistry","question":"35°C পানিতে O₂ এর দ্রাব্যতা 2.3×10⁻⁴ M হলে ppm একক তা কত?","options":{"A":"6.90","B":"0.74","C":"7.01","D":"7.36"},"answer":"D","explanation":"ppm = mg/L = 2.3×10⁻⁴ mol/L × 32 g/mol × 1000 mg/g = 7.36 ppm"},
    {"type":"mcq","subject":"Chemistry","question":"Ca(OCl)Cl যৌগে Cl এর oxidation number কত?","options":{"A":"-1,-1","B":"+1,-2","C":"+1,-1","D":"-1,+2"},"answer":"C","explanation":"ব্লিচিং পাউডারে দুটি Cl আছে: OCl⁻ এ Cl হল +1 এবং Cl⁻ হল -1।"},
    {"type":"mcq","subject":"Chemistry","question":"বর্জ্য রিসাইক্লিং থেকে প্রধান কি সুফল পাওয়া যায়?","options":{"A":"দূষণ হ্রাস পায়","B":"বিদ্যুৎ খরচ কমে","C":"কাঁচামালের ব্যবহার বাড়ে","D":"পণ্য উৎপাদন খরচ কমে"},"answer":"A","explanation":"বর্জ্য রিসাইক্লিং মূলত পরিবেশ দূষণ হ্রাস করে।"},

    # Physics - Hard
    {"type":"mcq","subject":"Physics","question":"ফোকাস দূরত্ব 1000 cm হলে উত্তল লেন্সের ক্ষমতা কত?","options":{"A":"+10 D","B":"+100 D","C":"+0.1 D","D":"-0.1 D"},"answer":"C","explanation":"P = 1/f(m) = 1/10 = +0.1 D"},
    {"type":"mcq","subject":"Physics","question":"স্থিরাবস্থা থেকে কোন বস্তুকণা সুষম ত্বরণে অনুভূমিক সরলরেখা বরাবর যাত্রা শুরু করল। চতুর্থ ও তৃতীয় সেকেন্ডে তার অতিক্রান্ত দূরত্বের অনুপাত হবে-","options":{"A":"26:9","B":"4:3","C":"7:5","D":"2:1"},"answer":"C","explanation":"nth সেকেন্ডে দূরত্ব ∝ (2n-1); 4র্থ সেকেন্ডে = 7k, 3য় সেকেন্ডে = 5k; অনুপাত = 7:5"},
    {"type":"mcq","subject":"Physics","question":"শূন্য ডিগ্রি সেন্টিগ্রেড তাপমাত্রায় সম্পৃক্ত জলীয় বাষ্পের চাপ 4.5 মিঃ মিঃ পারদ হলে 40 ডিগ্রি সেন্টিগ্রেড তাপমাত্রায় জলীয় বাষ্পের চাপ কত?","options":{"A":"55 মিঃ মিঃ পারদ","B":"35 মিঃ মিঃ পারদ","C":"25 মিঃ মিঃ পারদ","D":"9 মিঃ মিঃ পারদ"},"answer":"A","explanation":"তাপমাত্রা বৃদ্ধিতে সম্পৃক্ত বাষ্পচাপ বৃদ্ধি পায়; 40°C তে ≈ 55 mmHg"},
    {"type":"mcq","subject":"Physics","question":"একটি বস্তু 4.9 ms⁻¹ বেগে খাড়া উপরের দিকে নিক্ষিপ্ত হলে এটি কত সময় শূন্যে থাকবে?","options":{"A":"2 সেকেন্ড","B":"1 সেকেন্ড","C":"4 সেকেন্ড","D":"3 সেকেন্ড"},"answer":"B","explanation":"মোট সময় = 2u/g = 2×4.9/9.8 = 1 সেকেন্ড"},
    {"type":"mcq","subject":"Physics","question":"দুটি ভেক্টর রাশির মান যথাক্রমে 8 ও 6 একক। এরা পরস্পর 30° কোণে ক্রিয়াশীল হলে এদের ভেক্টর গুণফল কত?","options":{"A":"16","B":"20","C":"48","D":"24"},"answer":"D","explanation":"A×B = |A||B|sinθ = 8×6×sin30° = 48×0.5 = 24"},
    {"type":"mcq","subject":"Physics","question":"গ্যালভানোমিটারের তড়িৎ বর্তনীতে শান্ট ব্যবহারের উদ্দেশ্য-","options":{"A":"বিদ্যুৎ প্রবাহ কমানো","B":"বিদ্যুৎ প্রবাহ বাড়ানো","C":"বিভব পার্থক্য কমানো","D":"বিভব পার্থক্য বাড়ানো"},"answer":"A","explanation":"শান্ট রেজিস্ট্যান্স গ্যালভানোমিটারের সাথে সমান্তরালে যুক্ত করে অতিরিক্ত তড়িৎ প্রবাহ সরিয়ে দেয়।"},
    {"type":"mcq","subject":"Physics","question":"কোন সূত্রের উপর নির্ভর করে তাপীয় ইঞ্জিন ও রেফ্রিজারেটর তৈরি করা হয়?","options":{"A":"তাপগতিবিদ্যার তৃতীয় সূত্র","B":"তাপগতিবিদ্যার দ্বিতীয় সূত্র","C":"তাপগতিবিদ্যার প্রথম সূত্র","D":"তাপগতিবিদ্যার শূন্যতম সূত্র"},"answer":"B","explanation":"তাপগতিবিদ্যার দ্বিতীয় সূত্র তাপের প্রবাহের দিক নির্ধারণ করে — তাপ ইঞ্জিন ও রেফ্রিজারেটরের ভিত্তি।"},
    {"type":"mcq","subject":"Physics","question":"কোন তাপমাত্রায় সেলসিয়াস ও ফারেনহাইট একই মান দেখায়?","options":{"A":"-40°","B":"32°","C":"40°","D":"-32°"},"answer":"A","explanation":"C = F হলে, C = 9C/5 + 32 → -4C/5 = 32 → C = -40°"},
    {"type":"mcq","subject":"Physics","question":"100m দীর্ঘ একটি ট্রেন 45kmh⁻¹ বেগে চলে 1km দীর্ঘ একটি ব্রিজ অতিক্রম করে। ব্রিজটি অতিক্রম করতে ট্রেনটির কত সময় লাগবে?","options":{"A":"88 সেকেন্ড","B":"18 সেকেন্ড","C":"80 সেকেন্ড","D":"24 সেকেন্ড"},"answer":"A","explanation":"মোট দূরত্ব = 1000+100 = 1100m; বেগ = 45×1000/3600 = 12.5 m/s; সময় = 1100/12.5 = 88s"},
    {"type":"mcq","subject":"Physics","question":"ভূপৃষ্ঠ হতে 1000 কিলোমিটার উচ্চতে অভিকর্ষ ত্বরণের মান কত?","options":{"A":"8.1 ms⁻²","B":"3.8 ms⁻²","C":"7.33 ms⁻²","D":"9.8 ms⁻²"},"answer":"C","explanation":"g' = g(R/(R+h))² = 9.8×(6400/7400)² ≈ 7.33 ms⁻²"},

    # English - Hard
    {"type":"mcq","subject":"English","question":"Which of the following is the active form of: 'My book has been lost by me.'","options":{"A":"I had lost my book.","B":"I lost my book.","C":"I have lost my book.","D":"A book of mine is lost."},"answer":"C","explanation":"Present perfect passive → present perfect active: 'I have lost my book.'"},
    {"type":"mcq","subject":"English","question":"Which of the following is the passive form of: 'You have to admit this.'","options":{"A":"You are to have admitted this.","B":"You has to be admitted by you.","C":"This had to be admitted by you.","D":"This is to be admitted by you."},"answer":"D","explanation":"'Have to' passive form: subject + is/are + to be + V3. Correct: 'This is to be admitted by you.'"},
    {"type":"mcq","subject":"English","question":"The synonym of the word 'anarchy' is-","options":{"A":"serenity","B":"placidity","C":"lawlessness","D":"discipline"},"answer":"C","explanation":"Anarchy = a state of disorder/lawlessness."},
    {"type":"mcq","subject":"English","question":"The antonym of the word 'impediment' is-","options":{"A":"useful","B":"hindrance","C":"obstacle","D":"helpful"},"answer":"D","explanation":"Impediment = obstacle/hindrance; antonym = helpful/aid."},
    {"type":"mcq","subject":"English","question":"What does the phrase 'keep your chin up' mean?","options":{"A":"be cheerful","B":"be careful","C":"be brave","D":"be smart"},"answer":"A","explanation":"'Keep your chin up' is an idiom meaning stay positive/be cheerful."},
    {"type":"mcq","subject":"English","question":"'Call it a day' means-","options":{"A":"finish work","B":"fix an appointment","C":"spend the time","D":"open an event"},"answer":"A","explanation":"'Call it a day' = stop working for the day/finish work."},
    {"type":"mcq","subject":"English","question":"Which of the following sentences has the correct subject-verb agreement?","options":{"A":"Traffic jams in the parking area was one difficulty","B":"Not only Sufia, but also Nasima, want to visit grandma","C":"One problem for the players was unexpected threats of injury","D":"Somebody want to speak with you"},"answer":"C","explanation":"'One problem... was' — singular subject takes singular verb. This is the only correct option."},

    # General Knowledge (Bangladesh & World)
    {"type":"mcq","subject":"GK","question":"বাংলাদেশের ১০০ টাকার নোটে কোন মসজিদের ছবি আছে?","options":{"A":"মডেল মসজিদ","B":"ষাট গম্বুজ মসজিদ","C":"আতিয়া মসজিদ","D":"তারা মসজিদ"},"answer":"B","explanation":"১০০ টাকার নোটে ষাট গম্বুজ মসজিদের ছবি রয়েছে।"},
    {"type":"mcq","subject":"GK","question":"বৈষম্যবিরোধী আন্দোলন চলাকালে আবু সাইদ কবে শহীদ হন?","options":{"A":"২১ জুলাই ২০২৪","B":"১৬ জুলাই ২০২৪","C":"২০ জুলাই ২০২৪","D":"১৫ জুলাই ২০২৪"},"answer":"B","explanation":"আবু সাইদ ১৬ জুলাই ২০২৪ সালে রাজশাহীতে শহীদ হন।"},
    {"type":"mcq","subject":"GK","question":"বিশ্ব স্বাস্থ্য সংস্থা কর্তৃক কালাজ্বর নির্মূল করার ক্ষেত্রে বাংলাদেশ বিশ্বের প্রথম দেশ হিসেবে স্বীকৃতি লাভ করে কোন তারিখে?","options":{"A":"৩০ সেপ্টেম্বর ২০২৩","B":"৩১ অক্টোবর ২০২৩","C":"০১ নভেম্বর ২০২৩","D":"৩০ নভেম্বর ২০২৩"},"answer":"B","explanation":"৩১ অক্টোবর ২০২৩ সালে WHO বাংলাদেশকে কালাজ্বরমুক্ত দেশ হিসেবে স্বীকৃতি দেয়।"},
    {"type":"mcq","subject":"GK","question":"ঢাকা মেডিকেল কলেজ প্রতিষ্ঠিত হয় কোন সালে?","options":{"A":"১৯৪৫","B":"১৯৩৫","C":"১৯৫২","D":"১৯৪৬"},"answer":"A","explanation":"ঢাকা মেডিকেল কলেজ ১৯৪৫ সালে প্রতিষ্ঠিত হয়।"},
    {"type":"mcq","subject":"GK","question":"মুক্তিযুদ্ধকালীন বাংলাদেশ সরকারের সর্বদলীয় উপদেষ্টা কমিটির চেয়ারম্যান কে ছিলেন?","options":{"A":"সৈয়দ নজরুল ইসলাম","B":"তাজউদ্দিন আহমদ","C":"কমরেড মণি সিংহ","D":"মৌলানা ভাসানী"},"answer":"D","explanation":"মুক্তিযুদ্ধকালীন সর্বদলীয় উপদেষ্টা কমিটির চেয়ারম্যান ছিলেন মৌলানা আব্দুল হামিদ খান ভাসানী।"},
]
# ────────────────────────────────────────────────────────────────────────────────


# ─── GIST SCOREBOARD ────────────────────────────────────────────────────────────

def _load_scores_sync() -> dict:
    try:
        req = urllib.request.Request(
            f"https://api.github.com/gists/{GIST_ID}",
            headers={
                "Authorization": f"token {GIST_TOKEN}",
                "Accept": "application/vnd.github.v3+json"
            }
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            content = data["files"]["scores.json"]["content"]
            return json.loads(content)
    except Exception as e:
        print(f"Gist load error: {e}")
        return {}


def _save_scores_sync(scores: dict) -> bool:
    try:
        payload = json.dumps({
            "files": {
                "scores.json": {
                    "content": json.dumps(scores, ensure_ascii=False, indent=2)
                }
            }
        }).encode("utf-8")
        req = urllib.request.Request(
            f"https://api.github.com/gists/{GIST_ID}",
            data=payload,
            headers={
                "Authorization": f"token {GIST_TOKEN}",
                "Accept": "application/vnd.github.v3+json",
                "Content-Type": "application/json"
            },
            method="PATCH"
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            print(f"Gist saved OK, players={len(scores)}")
            return True
    except urllib.error.HTTPError as e:
        print(f"Gist save error {e.code}: {e.read().decode()}")
        return False
    except Exception as e:
        print(f"Gist save exception: {e}")
        return False


async def load_scores() -> dict:
    if not GIST_TOKEN or not GIST_ID:
        print("WARNING: Gist credentials missing!")
        return {}
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, _load_scores_sync)


async def save_scores(scores: dict) -> bool:
    if not GIST_TOKEN or not GIST_ID:
        return False
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, _save_scores_sync, scores)


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
                for q in external:
                    if "type" not in q:
                        q["type"] = "mcq"
                    if "subject" not in q:
                        q["subject"] = "General"
                print(f"Loaded {len(external)} questions from questions.json")
                # Shuffle fully then pick — ensures even distribution over time
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
                new_points = await update_score(user_id, username, is_correct)
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
                new_points = await update_score(user_id, username, True, points_to_add=5)
            else:
                scores = await load_scores()
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
    scores = await load_scores()
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

    # Diagnostics
    print(f"CHANNEL_ID: {CHANNEL_ID}")
    print(f"GIST_ID: {GIST_ID}")
    print(f"GIST_TOKEN length: {len(GIST_TOKEN) if GIST_TOKEN else 0}")
    test = await load_scores()
    print(f"Gist test load: {test}")

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
