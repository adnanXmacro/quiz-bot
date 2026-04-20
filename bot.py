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

# Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂ CONFIG Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
DISCORD_TOKEN         = os.environ.get("DISCORD_TOKEN")
CHANNEL_ID            = int(os.environ.get("CHANNEL_ID", "1493121034226761758"))
GIST_TOKEN            = os.environ.get("GIST_TOKEN")
GIST_ID               = os.environ.get("GIST_ID")
QUESTIONS_PER_SESSION = 10
ALIVE_MINUTES         = 60
PERSONAL_TIMER_MIN    = 10
# Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ

# Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂ QUESTION BANK Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
# Ã¢ÂÂ¼Ã¢ÂÂ¼Ã¢ÂÂ¼ PASTE YOUR QUESTIONS HERE Ã¢ÂÂ replace the placeholder below Ã¢ÂÂ¼Ã¢ÂÂ¼Ã¢ÂÂ¼
QUESTION_BANK = [
    {"type":"mcq","subject":"Biology","question":"Ã Â¦Â¨Ã Â¦Â¿Ã Â¦ÂÃ Â§ÂÃ Â¦Â° Ã Â¦ÂÃ Â§ÂÃ Â¦Â¨Ã Â¦ÂÃ Â¦Â¿Ã Â¦Â¤Ã Â§Â Ã Â¦Â¹Ã Â¦Â¾Ã Â¦ÂÃ Â¦Â¡Ã Â§ÂÃ Â¦Â°Ã Â¦Â¾Ã Â¦Â° Ã Â¦Â¬Ã Â¦Â¹Ã Â¦Â¿Ã Â¦ÂÃ Â¦ÂÃ Â§ÂÃ Â¦Â·Ã Â§ÂÃ Â¦Â¯Ã Â¦Â¼ Ã Â¦ÂªÃ Â¦Â°Ã Â¦Â¿Ã Â¦ÂªÃ Â¦Â¾Ã Â¦Â Ã Â¦Â¸Ã Â¦ÂÃ Â¦ÂÃ Â¦ÂÃ Â¦Â¿Ã Â¦Â¤ Ã Â¦Â¹Ã Â¦Â¯Ã Â¦Â¼?","options":{"A":"Ã Â¦ÂÃ Â§ÂÃ Â¦Â¯Ã Â¦Â¾Ã Â¦Â¸Ã Â§ÂÃ Â¦ÂÃ Â§ÂÃ Â¦Â°Ã Â§ÂÃ Â¦Â¡Ã Â¦Â¾Ã Â¦Â°Ã Â§ÂÃ Â¦Â®Ã Â¦Â¿Ã Â¦Â¸","B":"Ã Â¦Â¹Ã Â¦Â¾Ã Â¦ÂÃ Â¦ÂªÃ Â§ÂÃ Â¦Â¸Ã Â§ÂÃ Â¦ÂÃ Â§ÂÃ Â¦Â®","C":"Ã Â¦Â¸Ã Â¦Â¿Ã Â¦Â²Ã Â§ÂÃ Â¦Â¨Ã Â§ÂÃ Â¦ÂÃ Â§ÂÃ Â¦Â°Ã Â¦Â¨","D":"Ã Â¦ÂÃ Â¦Â°Ã Â§ÂÃ Â¦Â·Ã Â¦Â¿Ã Â¦ÂÃ Â¦Â¾"},"answer":"C","explanation":"Ã Â¦Â¹Ã Â¦Â¾Ã Â¦ÂÃ Â¦Â¡Ã Â§ÂÃ Â¦Â°Ã Â¦Â¾Ã Â¦Â° Ã Â¦Â¸Ã Â¦Â¿Ã Â¦Â²Ã Â§ÂÃ Â¦Â¨Ã Â§ÂÃ Â¦ÂÃ Â§ÂÃ Â¦Â°Ã Â¦Â¨Ã Â§Â Ã Â¦Â¬Ã Â¦Â¹Ã Â¦Â¿Ã Â¦ÂÃ Â¦ÂÃ Â§ÂÃ Â¦Â·Ã Â§ÂÃ Â¦Â¯Ã Â¦Â¼ Ã Â¦ÂªÃ Â¦Â°Ã Â¦Â¿Ã Â¦ÂªÃ Â¦Â¾Ã Â¦Â Ã Â¦ÂÃ Â¦ÂÃ Â§ÂÃ Â¥Â¤"},
    {"type":"mcq","subject":"Biology","question":"Ã Â¦ÂÃ Â§ÂÃ Â¦Â· Ã Â¦Â¬Ã Â¦Â¿Ã Â¦Â­Ã Â¦Â¾Ã Â¦ÂÃ Â¦Â¨Ã Â§ÂÃ Â¦Â° Ã Â¦Â¸Ã Â¦Â®Ã Â¦Â¯Ã Â¦Â¼ Ã Â¦ÂÃ Â§ÂÃ Â¦Â·Ã Â¦ÂªÃ Â§ÂÃ Â¦Â²Ã Â§ÂÃ Â¦Â Ã Â¦Â¤Ã Â§ÂÃ Â¦Â°Ã Â¦Â¿Ã Â¦Â¤Ã Â§Â Ã Â¦Â¸Ã Â¦Â¾Ã Â¦Â¹Ã Â¦Â¾Ã Â¦Â¯Ã Â§ÂÃ Â¦Â¯ Ã Â¦ÂÃ Â¦Â°Ã Â§Â Ã Â¦ÂÃ Â§ÂÃ Â¦Â¨ Ã Â¦ÂÃ Â¦ÂÃ Â§ÂÃ Â¦ÂÃ Â¦Â¾Ã Â¦Â£Ã Â§Â?","options":{"A":"Ã Â¦Â²Ã Â¦Â¾Ã Â¦ÂÃ Â¦Â¸Ã Â§ÂÃ Â¦Â¸Ã Â§ÂÃ Â¦Â®","B":"Ã Â¦ÂÃ Â¦Â²Ã Â¦ÂÃ Â¦Â¿ Ã Â¦Â¬Ã Â¦Â¸Ã Â§ÂÃ Â¦Â¤Ã Â§Â","C":"Ã Â¦Â®Ã Â¦Â¾Ã Â¦ÂÃ Â¦ÂÃ Â§ÂÃ Â¦ÂÃ Â¦Â¨Ã Â§ÂÃ Â¦Â¡Ã Â§ÂÃ Â¦Â°Ã Â¦Â¿Ã Â¦Â¯Ã Â¦Â¼Ã Â¦Â¾","D":"Ã Â¦Â°Ã Â¦Â¾Ã Â¦ÂÃ Â¦Â¬Ã Â§ÂÃ Â¦Â¸Ã Â§ÂÃ Â¦Â®"},"answer":"B","explanation":"Ã Â¦ÂÃ Â¦Â²Ã Â¦ÂÃ Â¦Â¿ Ã Â¦Â¬Ã Â¦Â¸Ã Â§ÂÃ Â¦Â¤Ã Â§Â Ã Â¦ÂÃ Â§ÂÃ Â¦Â· Ã Â¦Â¬Ã Â¦Â¿Ã Â¦Â­Ã Â¦Â¾Ã Â¦ÂÃ Â¦Â¨Ã Â§ÂÃ Â¦Â° Ã Â¦Â¸Ã Â¦Â®Ã Â¦Â¯Ã Â¦Â¼ Ã Â¦ÂÃ Â§ÂÃ Â¦Â·Ã Â¦ÂªÃ Â§ÂÃ Â¦Â²Ã Â§ÂÃ Â¦Â Ã Â¦ÂÃ Â¦Â Ã Â¦Â¨Ã Â§Â Ã Â¦Â¸Ã Â¦Â¾Ã Â¦Â¹Ã Â¦Â¾Ã Â¦Â¯Ã Â§ÂÃ Â¦Â¯ Ã Â¦ÂÃ Â¦Â°Ã Â§ÂÃ Â¥Â¤"},
    {"type":"mcq","subject":"Biology","question":"Ã Â¦Â°Ã Â§ÂÃ Â¦Â¸Ã Â§ÂÃ Â¦ÂÃ Â§ÂÃ Â¦Â°Ã Â¦Â¿Ã Â¦ÂÃ Â¦Â¶Ã Â¦Â¨ Ã Â¦ÂÃ Â¦Â¨Ã Â¦ÂÃ Â¦Â¾Ã Â¦ÂÃ Â¦Â®Ã Â§ÂÃ Â¦Â° Ã Â¦ÂÃ Â¦Â¾Ã Â¦Â Ã Â¦ÂÃ Â§Â?","options":{"A":"DNA Ã Â¦ÂÃ Â¦Â£Ã Â§Â Ã Â¦Â¬Ã Â§ÂÃ Â¦Â¦Ã Â§ÂÃ Â¦Â§Ã Â¦Â¿Ã Â¦ÂÃ Â¦Â°Ã Â¦Â£","B":"DNA Ã Â¦ÂÃ Â¦Â£Ã Â§ÂÃ Â¦Â¡Ã Â¦ÂÃ Â§Â Ã Â¦ÂÃ Â§ÂÃ Â¦Â¡Ã Â¦Â¼Ã Â¦Â¾ Ã Â¦Â²Ã Â¦Â¾Ã Â¦ÂÃ Â¦Â¾Ã Â¦Â¨Ã Â§Â","C":"Ã Â¦Â¨Ã Â¦Â¿Ã Â¦Â°Ã Â§ÂÃ Â¦Â¦Ã Â¦Â¿Ã Â¦Â·Ã Â§ÂÃ Â¦Â Ã Â¦ÂÃ Â§ÂÃ Â¦Â¬Ã Â§Â Ã Â¦Â°Ã Â¦Â¿Ã Â¦ÂÃ Â¦Â®Ã Â§ÂÃ Â¦Â¬Ã Â¦Â¿Ã Â¦Â¨Ã Â§ÂÃ Â¦Â¨Ã Â§ÂÃ Â¦Â DNA Ã Â¦ÂªÃ Â§ÂÃ Â¦Â°Ã Â¦Â¬Ã Â§ÂÃ Â¦Â¶ Ã Â¦ÂÃ Â¦Â°Ã Â¦Â¾Ã Â¦Â¨Ã Â§Â","D":"Ã Â¦ÂÃ Â¦Â¾Ã Â¦ÂÃ Â§ÂÃ Â¦ÂÃ Â§ÂÃ Â¦Â·Ã Â¦Â¿Ã Â¦Â¤ DNA Ã Â¦ÂÃ Â§Â Ã Â¦Â¨Ã Â¦Â¿Ã Â¦Â°Ã Â§ÂÃ Â¦Â¦Ã Â¦Â¿Ã Â¦Â·Ã Â§ÂÃ Â¦Â Ã Â¦Â¸Ã Â§ÂÃ Â¦Â¥Ã Â¦Â¾Ã Â¦Â¨Ã Â§Â Ã Â¦ÂÃ Â§ÂÃ Â¦Â¦Ã Â¦Â¨ Ã Â¦ÂÃ Â¦Â°Ã Â¦Â¾"},"answer":"D","explanation":"Ã Â¦Â°Ã Â§ÂÃ Â¦Â¸Ã Â§ÂÃ Â¦ÂÃ Â§ÂÃ Â¦Â°Ã Â¦Â¿Ã Â¦ÂÃ Â¦Â¶Ã Â¦Â¨ Ã Â¦ÂÃ Â¦Â¨Ã Â¦ÂÃ Â¦Â¾Ã Â¦ÂÃ Â¦Â® Ã Â¦Â¨Ã Â¦Â¿Ã Â¦Â°Ã Â§ÂÃ Â¦Â¦Ã Â¦Â¿Ã Â¦Â·Ã Â§ÂÃ Â¦Â Ã Â¦Â¸Ã Â§ÂÃ Â¦Â¥Ã Â¦Â¾Ã Â¦Â¨Ã Â§Â DNA Ã Â¦ÂÃ Â§ÂÃ Â¦Â¦Ã Â¦Â¨ Ã Â¦ÂÃ Â¦Â°Ã Â§ÂÃ Â¥Â¤"},
    {"type":"mcq","subject":"Chemistry","question":"18ÃÂ°C Ã Â¦Â¤Ã Â¦Â¾Ã Â¦ÂªÃ Â¦Â®Ã Â¦Â¾Ã Â¦Â¤Ã Â§ÂÃ Â¦Â°Ã Â¦Â¾Ã Â¦Â¯Ã Â¦Â¼ 0.8 atm Ã Â¦ÂÃ Â¦Â¾Ã Â¦ÂªÃ Â§Â Ã Â¦ÂÃ Â¦ÂÃ Â¦ÂÃ Â¦Â¿ Ã Â¦ÂÃ Â§ÂÃ Â¦Â¯Ã Â¦Â¾Ã Â¦Â¸Ã Â§ÂÃ Â¦Â° Ã Â¦ÂÃ Â¦Â¨Ã Â¦Â¤Ã Â§ÂÃ Â¦Â¬ 2.25 gLÃ¢ÂÂ»ÃÂ¹ Ã Â¦Â¹Ã Â¦Â²Ã Â§Â Ã Â¦ÂÃ Â¦Â£Ã Â¦Â¬Ã Â¦Â¿Ã Â¦Â Ã Â¦Â­Ã Â¦Â° Ã Â¦ÂÃ Â¦Â¤?","options":{"A":"36.63 g molÃ¢ÂÂ»ÃÂ¹","B":"36.24 g molÃ¢ÂÂ»ÃÂ¹","C":"24.36 g molÃ¢ÂÂ»ÃÂ¹","D":"67.11 g molÃ¢ÂÂ»ÃÂ¹"},"answer":"A","explanation":"PV=nRT Ã Â¦Â¬Ã Â§ÂÃ Â¦Â¯Ã Â¦Â¬Ã Â¦Â¹Ã Â¦Â¾Ã Â¦Â° Ã Â¦ÂÃ Â¦Â°Ã Â§Â M = dRT/P Ã¢ÂÂ 36.63 g/mol"},
    {"type":"mcq","subject":"Chemistry","question":"Ã Â¦ÂÃ Â§ÂÃ Â¦Â¨ Ã Â¦Â¦Ã Â§ÂÃ Â¦Â°Ã Â¦Â¬Ã Â¦Â£Ã Â§ÂÃ Â¦Â° OHÃ¢ÂÂ» Ã Â¦ÂÃ Â¦Â¯Ã Â¦Â¼Ã Â¦Â¨Ã Â§ÂÃ Â¦Â° Ã Â¦ÂÃ Â¦Â¨Ã Â¦Â®Ã Â¦Â¾Ã Â¦Â¤Ã Â§ÂÃ Â¦Â°Ã Â¦Â¾ 3.5ÃÂ10Ã¢ÂÂ»Ã¢ÂÂ´ M Ã Â¦Â¹Ã Â¦Â²Ã Â§Â pH Ã Â¦ÂÃ Â¦Â¤?","options":{"A":"12.50","B":"13.55","C":"10.54","D":"3.55"},"answer":"C","explanation":"pOH = -log(3.5ÃÂ10Ã¢ÂÂ»Ã¢ÂÂ´) Ã¢ÂÂ 3.46; pH = 14-3.46 = 10.54"},
    {"type":"mcq","subject":"Physics","question":"Ã Â¦Â«Ã Â§ÂÃ Â¦ÂÃ Â¦Â¾Ã Â¦Â¸ Ã Â¦Â¦Ã Â§ÂÃ Â¦Â°Ã Â¦Â¤Ã Â§ÂÃ Â¦Â¬ 1000 cm Ã Â¦Â¹Ã Â¦Â²Ã Â§Â Ã Â¦ÂÃ Â¦Â¤Ã Â§ÂÃ Â¦Â¤Ã Â¦Â² Ã Â¦Â²Ã Â§ÂÃ Â¦Â¨Ã Â§ÂÃ Â¦Â¸Ã Â§ÂÃ Â¦Â° Ã Â¦ÂÃ Â§ÂÃ Â¦Â·Ã Â¦Â®Ã Â¦Â¤Ã Â¦Â¾ Ã Â¦ÂÃ Â¦Â¤?","options":{"A":"+10 D","B":"+100 D","C":"+0.1 D","D":"-0.1 D"},"answer":"C","explanation":"P = 1/f(m) = 1/10 = +0.1 D"},
    {"type":"mcq","subject":"Physics","question":"Ã Â¦Â¦Ã Â§ÂÃ Â¦ÂÃ Â¦Â¿ Ã Â¦Â­Ã Â§ÂÃ Â¦ÂÃ Â§ÂÃ Â¦ÂÃ Â¦Â° 8 Ã Â¦Â 6 Ã Â¦ÂÃ Â¦ÂÃ Â¦Â, 30ÃÂ° Ã Â¦ÂÃ Â§ÂÃ Â¦Â£Ã Â§Â Ã Â¦ÂÃ Â§ÂÃ Â¦Â°Ã Â¦Â¿Ã Â¦Â¯Ã Â¦Â¼Ã Â¦Â¾Ã Â¦Â¶Ã Â§ÂÃ Â¦Â² Ã Â¦Â¹Ã Â¦Â²Ã Â§Â Ã Â¦Â­Ã Â§ÂÃ Â¦ÂÃ Â§ÂÃ Â¦ÂÃ Â¦Â° Ã Â¦ÂÃ Â§ÂÃ Â¦Â£Ã Â¦Â«Ã Â¦Â² Ã Â¦ÂÃ Â¦Â¤?","options":{"A":"16","B":"20","C":"48","D":"24"},"answer":"D","explanation":"AÃÂB = |A||B|sinÃÂ¸ = 8ÃÂ6ÃÂsin30ÃÂ° = 24"},
    {"type":"mcq","subject":"English","question":"Synonym of 'anarchy'Ã¢ÂÂ","options":{"A":"serenity","B":"placidity","C":"lawlessness","D":"discipline"},"answer":"C","explanation":"Anarchy = a state of disorder/lawlessness."},
    {"type":"mcq","subject":"GK","question":"Ã Â¦Â¬Ã Â¦Â¾Ã Â¦ÂÃ Â¦Â²Ã Â¦Â¾Ã Â¦Â¦Ã Â§ÂÃ Â¦Â¶Ã Â§ÂÃ Â¦Â° Ã Â§Â§Ã Â§Â¦Ã Â§Â¦ Ã Â¦ÂÃ Â¦Â¾Ã Â¦ÂÃ Â¦Â¾Ã Â¦Â° Ã Â¦Â¨Ã Â§ÂÃ Â¦ÂÃ Â§Â Ã Â¦ÂÃ Â§ÂÃ Â¦Â¨ Ã Â¦Â®Ã Â¦Â¸Ã Â¦ÂÃ Â¦Â¿Ã Â¦Â¦Ã Â§ÂÃ Â¦Â° Ã Â¦ÂÃ Â¦Â¬Ã Â¦Â¿ Ã Â¦ÂÃ Â¦ÂÃ Â§Â?","options":{"A":"Ã Â¦Â®Ã Â¦Â¡Ã Â§ÂÃ Â¦Â² Ã Â¦Â®Ã Â¦Â¸Ã Â¦ÂÃ Â¦Â¿Ã Â¦Â¦","B":"Ã Â¦Â·Ã Â¦Â¾Ã Â¦Â Ã Â¦ÂÃ Â¦Â®Ã Â§ÂÃ Â¦Â¬Ã Â§ÂÃ Â¦Â Ã Â¦Â®Ã Â¦Â¸Ã Â¦ÂÃ Â¦Â¿Ã Â¦Â¦","C":"Ã Â¦ÂÃ Â¦Â¤Ã Â¦Â¿Ã Â¦Â¯Ã Â¦Â¼Ã Â¦Â¾ Ã Â¦Â®Ã Â¦Â¸Ã Â¦ÂÃ Â¦Â¿Ã Â¦Â¦","D":"Ã Â¦Â¤Ã Â¦Â¾Ã Â¦Â°Ã Â¦Â¾ Ã Â¦Â®Ã Â¦Â¸Ã Â¦ÂÃ Â¦Â¿Ã Â¦Â¦"},"answer":"B","explanation":"Ã Â§Â§Ã Â§Â¦Ã Â§Â¦ Ã Â¦ÂÃ Â¦Â¾Ã Â¦ÂÃ Â¦Â¾Ã Â¦Â° Ã Â¦Â¨Ã Â§ÂÃ Â¦ÂÃ Â§Â Ã Â¦Â·Ã Â¦Â¾Ã Â¦Â Ã Â¦ÂÃ Â¦Â®Ã Â§ÂÃ Â¦Â¬Ã Â§ÂÃ Â¦Â Ã Â¦Â®Ã Â¦Â¸Ã Â¦ÂÃ Â¦Â¿Ã Â¦Â¦Ã Â¥Â¤"},
    {"type":"mcq","subject":"GK","question":"WHO Ã Â¦ÂÃ Â¦Â¾Ã Â¦Â²Ã Â¦Â¾Ã Â¦ÂÃ Â§ÂÃ Â¦Â¬Ã Â¦Â°Ã Â¦Â®Ã Â§ÂÃ Â¦ÂÃ Â§ÂÃ Â¦Â¤ Ã Â¦Â¦Ã Â§ÂÃ Â¦Â¶ Ã Â¦Â¹Ã Â¦Â¿Ã Â¦Â¸Ã Â§ÂÃ Â¦Â¬Ã Â§Â Ã Â¦Â¬Ã Â¦Â¾Ã Â¦ÂÃ Â¦Â²Ã Â¦Â¾Ã Â¦Â¦Ã Â§ÂÃ Â¦Â¶Ã Â¦ÂÃ Â§Â Ã Â¦Â¸Ã Â§ÂÃ Â¦Â¬Ã Â§ÂÃ Â¦ÂÃ Â§ÂÃ Â¦Â¤Ã Â¦Â¿ Ã Â¦Â¦Ã Â§ÂÃ Â¦Â¯Ã Â¦Â¼ Ã Â¦ÂÃ Â¦Â¬Ã Â§Â?","options":{"A":"Ã Â§Â©Ã Â§Â¦ Ã Â¦Â¸Ã Â§ÂÃ Â¦ÂªÃ Â§ÂÃ Â¦ÂÃ Â§ÂÃ Â¦Â®Ã Â§ÂÃ Â¦Â¬Ã Â¦Â° Ã Â§Â¨Ã Â§Â¦Ã Â§Â¨Ã Â§Â©","B":"Ã Â§Â©Ã Â§Â§ Ã Â¦ÂÃ Â¦ÂÃ Â§ÂÃ Â¦ÂÃ Â§ÂÃ Â¦Â¬Ã Â¦Â° Ã Â§Â¨Ã Â§Â¦Ã Â§Â¨Ã Â§Â©","C":"Ã Â§Â¦Ã Â§Â§ Ã Â¦Â¨Ã Â¦Â­Ã Â§ÂÃ Â¦Â®Ã Â§ÂÃ Â¦Â¬Ã Â¦Â° Ã Â§Â¨Ã Â§Â¦Ã Â§Â¨Ã Â§Â©","D":"Ã Â§Â©Ã Â§Â¦ Ã Â¦Â¨Ã Â¦Â­Ã Â§ÂÃ Â¦Â®Ã Â§ÂÃ Â¦Â¬Ã Â¦Â° Ã Â§Â¨Ã Â§Â¦Ã Â§Â¨Ã Â§Â©"},"answer":"B","explanation":"Ã Â§Â©Ã Â§Â§ Ã Â¦ÂÃ Â¦ÂÃ Â§ÂÃ Â¦ÂÃ Â§ÂÃ Â¦Â¬Ã Â¦Â° Ã Â§Â¨Ã Â§Â¦Ã Â§Â¨Ã Â§Â© Ã Â¦Â¸Ã Â¦Â¾Ã Â¦Â²Ã Â§Â WHO Ã Â¦ÂÃ Â¦Â Ã Â¦Â¸Ã Â§ÂÃ Â¦Â¬Ã Â§ÂÃ Â¦ÂÃ Â§ÂÃ Â¦Â¤Ã Â¦Â¿ Ã Â¦Â¦Ã Â§ÂÃ Â¦Â¯Ã Â¦Â¼Ã Â¥Â¤"},
    {"type":"mcq","subject":"Math","question":"Ã Â¦ÂÃ Â§ÂÃ Â¦Â¨ Ã Â¦Â¤Ã Â¦Â¾Ã Â¦ÂªÃ Â¦Â®Ã Â¦Â¾Ã Â¦Â¤Ã Â§ÂÃ Â¦Â°Ã Â¦Â¾Ã Â¦Â¯Ã Â¦Â¼ Ã Â¦Â¸Ã Â§ÂÃ Â¦Â²Ã Â¦Â¸Ã Â¦Â¿Ã Â¦Â¯Ã Â¦Â¼Ã Â¦Â¾Ã Â¦Â¸ Ã Â¦Â Ã Â¦Â«Ã Â¦Â¾Ã Â¦Â°Ã Â§ÂÃ Â¦Â¨Ã Â¦Â¹Ã Â¦Â¾Ã Â¦ÂÃ Â¦Â Ã Â¦ÂÃ Â¦ÂÃ Â¦Â Ã Â¦Â®Ã Â¦Â¾Ã Â¦Â¨ Ã Â¦Â¦Ã Â§ÂÃ Â¦ÂÃ Â¦Â¾Ã Â¦Â¯Ã Â¦Â¼?","options":{"A":"-40ÃÂ°","B":"32ÃÂ°","C":"40ÃÂ°","D":"-32ÃÂ°"},"answer":"A","explanation":"C=F Ã Â¦Â¹Ã Â¦Â²Ã Â§Â, C = 9C/5+32 Ã¢ÂÂ C = -40ÃÂ°"},
    {"type":"mcq","subject":"Biology","question":"Ã Â¦Â¹Ã Â¦Â¿Ã Â¦Â®Ã Â§ÂÃ Â¦ÂÃ Â§ÂÃ Â¦Â²Ã Â§ÂÃ Â¦Â¬Ã Â¦Â¿Ã Â¦Â¨Ã Â§ÂÃ Â¦Â° Ã Â¦ÂÃ Â§ÂÃ Â¦Â¨ Ã Â¦ÂÃ Â¦ÂÃ Â¦Â¶Ã Â§Â COÃ¢ÂÂ Ã Â¦Â¯Ã Â§ÂÃ Â¦ÂÃ Â§ÂÃ Â¦Â¤ Ã Â¦Â¹Ã Â¦Â¯Ã Â¦Â¼?","options":{"A":"Ã¢ÂÂOH","B":"Ã¢ÂÂCOOH","C":"Ã¢ÂÂHCOÃ¢ÂÂ","D":"Ã¢ÂÂNHÃ¢ÂÂ"},"answer":"D","explanation":"COÃ¢ÂÂ, Ã Â¦Â¹Ã Â¦Â¿Ã Â¦Â®Ã Â§ÂÃ Â¦ÂÃ Â§ÂÃ Â¦Â²Ã Â§ÂÃ Â¦Â¬Ã Â¦Â¿Ã Â¦Â¨Ã Â§ÂÃ Â¦Â° Ã¢ÂÂNHÃ¢ÂÂ Ã Â¦ÂÃ Â§ÂÃ Â¦Â°Ã Â§ÂÃ Â¦ÂªÃ Â§ÂÃ Â¦Â° Ã Â¦Â¸Ã Â¦Â¾Ã Â¦Â¥Ã Â§Â Ã Â¦Â¯Ã Â§ÂÃ Â¦ÂÃ Â§ÂÃ Â¦Â¤ Ã Â¦Â¹Ã Â¦Â¯Ã Â¦Â¼Ã Â¥Â¤"},
]
# Ã¢ÂÂ²Ã¢ÂÂ²Ã¢ÂÂ² END OF QUESTION BANK Ã¢ÂÂ²Ã¢ÂÂ²Ã¢ÂÂ²
# Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ


# Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂ GIST DATA STORAGE Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
# Saves to Gist on every answer using a lock to prevent 409 conflicts.

SESSION_DATA = {"scores": {}, "asked": [], "streaks": {}, "session_count": 0}
_save_lock   = None  # asyncio.Lock Ã¢ÂÂ initialized in on_ready

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
    """Save to Gist Ã¢ÂÂ queued via lock so only one write at a time, no 409."""
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
    if streak >= 14: return "Ã°ÂÂÂ¥Ã°ÂÂÂ¥Ã°ÂÂÂ¥"
    elif streak >= 7: return "Ã°ÂÂÂ¥Ã°ÂÂÂ¥"
    elif streak >= 3: return "Ã°ÂÂÂ¥"
    return ""

async def update_score(user_id: str, username: str, correct: bool,
                       subject: str = "General", points_to_add: int = 10) -> int:
    """Update memory AND save to Gist immediately (queued)."""
    pts = update_score_sync(user_id, username, correct, subject, points_to_add)
    await save_to_gist()
    return pts

async def load_scores() -> dict:
    return SESSION_DATA.get("scores", {})


# Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂ UI HELPERS Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ

SUBJECT_META = {
    "Physics":   {"emoji": "Ã¢ÂÂ¡", "color": 0x5865F2, "label": "Physics"},
    "Chemistry": {"emoji": "Ã¢ÂÂÃ¯Â¸Â",  "color": 0xED4245, "label": "Chemistry"},
    "Math":      {"emoji": "Ã°ÂÂÂ", "color": 0x57F287, "label": "Mathematics"},
    "Biology":   {"emoji": "Ã°ÂÂÂ¬", "color": 0xFEE75C, "label": "Biology"},
    "English":   {"emoji": "Ã°ÂÂÂ", "color": 0x00B4FF, "label": "English"},
    "GK":        {"emoji": "Ã°ÂÂÂ", "color": 0xFF8C00, "label": "General Knowledge"},
}

def get_subject(subject: str) -> dict:
    return SUBJECT_META.get(subject, {"emoji": "Ã°ÂÂÂ", "color": 0x5865F2, "label": subject})

def get_rank(points: int) -> tuple:
    """Returns (badge_emoji, title, color_hex)"""
    if points >= 1000: return ("Ã°ÂÂÂ", "ELITE",      0xA8D8EA)
    elif points >= 500: return ("Ã°ÂÂÂ", "LEGEND",     0xFFD700)
    elif points >= 200: return ("Ã°ÂÂÂ¥", "CHAMPION",   0xFF6B35)
    elif points >= 100: return ("Ã¢ÂÂ¡", "SCHOLAR",    0x5865F2)
    elif points >= 50:  return ("Ã°ÂÂÂ", "APPRENTICE", 0x57F287)
    return                     ("Ã°ÂÂÂ±", "ROOKIE",     0x99AAB5)

SESSIONS_PER_CYCLE = 10  # Scoreboard resets every 10 sessions

def build_scoreboard_embed(scores: dict, streaks: dict = None, session_count: int = 0) -> discord.Embed:
    now_bd   = datetime.datetime.utcnow() + datetime.timedelta(hours=6)
    streaks  = streaks or {}
    sessions_left = SESSIONS_PER_CYCLE - (session_count % SESSIONS_PER_CYCLE)
    cycle_num     = (session_count // SESSIONS_PER_CYCLE) + 1

    if not scores:
        embed = discord.Embed(
            title="Ã°ÂÂÂ  Leaderboard",
            description=(
                f"No participants yet.\n\n"
                f"**Cycle #{cycle_num}**  ÃÂ·  Session `{session_count % SESSIONS_PER_CYCLE}/{SESSIONS_PER_CYCLE}`\n"
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
        title=f"Ã°ÂÂÂ  Leaderboard  ÃÂ·  {now_bd.strftime('%d %B %Y')}",
        color=0xFFD700,
        timestamp=datetime.datetime.utcnow()
    )

    # Cycle progress bar
    filled_cycle = round(((session_count % SESSIONS_PER_CYCLE) / SESSIONS_PER_CYCLE) * 10)
    cycle_bar    = "Ã¢ÂÂ" * filled_cycle + "Ã¢ÂÂ" * (10 - filled_cycle)
    embed.description = (
        f"**Cycle #{cycle_num}**  `{cycle_bar}`  "
        f"Session **{session_count % SESSIONS_PER_CYCLE}/{SESSIONS_PER_CYCLE}**"
        f"  ÃÂ·  Resets in `{sessions_left}` sessions"
    )

    # Podium top 3 with ties Ã¢ÂÂ same score = same rank, next rank = rank+1 (not skipped)
    rank      = 0
    prev_pts  = None
    podium_lines = []
    rest_lines   = []
    podium_icons = ["Ã°ÂÂ¥Â", "Ã°ÂÂ¥Â", "Ã°ÂÂ¥Â"]

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
                f"Ã£ÂÂ`{s['points']} pts`  ÃÂ·  **{acc}%** accuracy  ÃÂ·  {s['correct']}/{s['total']} Ã¢ÂÂ"
            )
        else:
            filled = round((s["points"] / max_pts) * 10)
            bar    = "Ã¢ÂÂ°" * filled + "Ã¢ÂÂ±" * (10 - filled)
            rest_lines.append(
                f"`#{rank:02d}` **{s['username'][:14]}**  {bar}  `{s['points']} pts`  ÃÂ·  {acc}%{st}"
            )

    if podium_lines:
        embed.add_field(name="Ã°ÂÂÂ Podium", value="\n\n".join(podium_lines), inline=False)
    if rest_lines:
        embed.add_field(name="Ã°ÂÂÂ Rankings", value="\n".join(rest_lines), inline=False)

    # Session stats
    total_p = len(sorted_scores)
    total_a = sum(s["total"] for s in sorted_scores)
    avg_acc = round(sum(
        100 * s["correct"] / s["total"] for s in sorted_scores if s["total"] > 0
    ) / max(total_p, 1))

    embed.add_field(
        name="Ã°ÂÂÂ This Session",
        value=f"`{total_p}` players  ÃÂ·  `{total_a}` answers  ÃÂ·  `{avg_acc}%` avg accuracy",
        inline=False
    )
    embed.set_footer(text="Ã°ÂÂÂ¥3d ÃÂ· Ã°ÂÂÂ¥Ã°ÂÂÂ¥7d ÃÂ· Ã°ÂÂÂ¥Ã°ÂÂÂ¥Ã°ÂÂÂ¥14d  |  Ã°ÂÂÂ1000 ÃÂ· Ã°ÂÂÂ500 ÃÂ· Ã°ÂÂÂ¥200 ÃÂ· Ã¢ÂÂ¡100 ÃÂ· Ã°ÂÂÂ50 ÃÂ· Ã°ÂÂÂ±0")
    return embed


# Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂ QUESTION PICKER Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ

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
        print("Full cycle complete Ã¢ÂÂ resetting asked history!")
        asked = set()
        fresh = pool.copy()
        SESSION_DATA["asked"] = []

    random.shuffle(fresh)
    selected = fresh[:min(count, len(fresh))]
    SESSION_DATA["asked"] = list(asked | {q["question"] for q in selected})
    return selected


# Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂ DISCORD VIEWS Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ

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
                            title="Ã¢ÂÂ°  Time's Up",
                            description=f"Your {PERSONAL_TIMER_MIN}-minute window expired at **{expiry.strftime('%H:%M')} UTC**.",
                            color=0x2B2D31
                        )
                        await interaction.response.send_message(embed=e, ephemeral=True)
                        return

                if user_id in self.answered_users:
                    e = discord.Embed(
                        title="Ã¢ÂÂ Ã¯Â¸Â  Already Answered",
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
                        name="Ã¢ÂÂ  Correct",
                        value=f"**{label}.  {self.question['options'][label]}**",
                        inline=False
                    )
                    if explanation:
                        e.add_field(name="Ã°ÂÂÂ¡ Explanation", value=explanation, inline=False)
                    e.add_field(
                        name="Score",
                        value=f"`+10 pts` Ã¢ÂÂ **{new_points} pts total**  ÃÂ·  {badge} {rank_title}{streak_text}",
                        inline=False
                    )
                else:
                    e = discord.Embed(color=0xED4245)
                    e.add_field(
                        name="Ã¢ÂÂ  Incorrect",
                        value=f"~~{label}.  {self.question['options'][label]}~~",
                        inline=False
                    )
                    e.add_field(
                        name="Ã¢ÂÂ  Correct Answer",
                        value=f"**{correct}.  {self.question['options'][correct]}**",
                        inline=False
                    )
                    if explanation:
                        e.add_field(name="Ã°ÂÂÂ¡ Explanation", value=explanation, inline=False)
                    e.add_field(
                        name="Score",
                        value=f"**{new_points} pts total**  ÃÂ·  {badge} {rank_title}{streak_text}",
                        inline=False
                    )
                e.set_footer(text=f"Your window closes at {expiry_str}  ÃÂ·  {PERSONAL_TIMER_MIN} min per session")
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
                        title="Ã¢ÂÂ°  Time's Up",
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
            e.add_field(name="Ã°ÂÂÂ¡  Answer", value=f"**{self.question['answer']}**", inline=False)
            if self.question.get("explanation"):
                e.add_field(name="Ã°ÂÂÂ Explanation", value=self.question["explanation"], inline=False)
            pts_text = f"`+5 pts` Ã¢ÂÂ **{new_points} pts total**  ÃÂ·  {badge} {rank_title}" if not already else f"**{new_points} pts total**  ÃÂ·  {badge} {rank_title}"
            e.add_field(name="Score", value=pts_text, inline=False)
            e.set_footer(text=f"Your window closes at {expiry_str}")
            await interaction.response.send_message(embed=e, ephemeral=True)
        except discord.errors.NotFound:
            pass
        except Exception as ex:
            print(f"Flashcard error: {ex}")


# Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂ QUIZ SESSION Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ

async def run_quiz_session(channel: discord.TextChannel):
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=6)
    date_str = now.strftime("%d %B %Y")
    end_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=ALIVE_MINUTES)

    announce = discord.Embed(
        title=f"Ã°ÂÂÂ  Daily Quiz  ÃÂ·  {date_str}",
        color=0x5865F2
    )
    announce.add_field(name="Questions",  value=f"`{QUESTIONS_PER_SESSION}`", inline=True)
    announce.add_field(name="MCQ",        value="`+10 pts`", inline=True)
    announce.add_field(name="Flashcard",  value="`+5 pts`",  inline=True)
    announce.add_field(name="Your Timer", value=f"`{PERSONAL_TIMER_MIN} min` from first tap", inline=True)
    announce.add_field(name="Session Ends", value=f"<t:{int(end_time.timestamp())}:R>", inline=True)
    announce.add_field(name="Visibility", value="Only you see your answers", inline=True)
    announce.set_footer(text="Ã°ÂÂÂ Elite ÃÂ· Ã°ÂÂÂ Legend ÃÂ· Ã°ÂÂÂ¥ Champion ÃÂ· Ã¢ÂÂ¡ Scholar ÃÂ· Ã°ÂÂÂ Apprentice ÃÂ· Ã°ÂÂÂ± Rookie")
    await channel.send(embed=announce)
    await asyncio.sleep(1.5)

    questions = await pick_questions_smart(QUESTIONS_PER_SESSION)
    print(f"Posting {len(questions)} questions")

    for i, q in enumerate(questions, 1):
        meta    = get_subject(q.get("subject", "General"))
        subject = q.get("subject", "General")

        if q["type"] == "mcq":
            opts = q.get("options", {})
            # Normalize keys Ã¢ÂÂ handle both uppercase and lowercase
            opts = {k.upper(): v for k, v in opts.items()}
            embed = discord.Embed(title=q["question"], color=meta["color"])
            embed.set_author(name=f"{meta['emoji']}  {meta['label']}  ÃÂ·  Question {i} of {len(questions)}")
            embed.add_field(
                name="",
                value=(
                    f"**A.**  {opts.get('A', 'Ã¢ÂÂ')}\n"
                    f"**B.**  {opts.get('B', 'Ã¢ÂÂ')}\n"
                    f"**C.**  {opts.get('C', 'Ã¢ÂÂ')}\n"
                    f"**D.**  {opts.get('D', 'Ã¢ÂÂ')}"
                ),
                inline=False
            )
            embed.set_footer(text=f"Ã¢ÂÂ± {PERSONAL_TIMER_MIN} min from first tap  ÃÂ·  Only you see your result")
            # Also normalize options in the question object for button callbacks
            q["options"] = opts
            await channel.send(embed=embed, view=MCQView(q))
        else:
            embed = discord.Embed(title=q["question"], color=meta["color"])
            embed.set_author(name=f"{meta['emoji']}  {meta['label']}  ÃÂ·  Flashcard {i} of {len(questions)}")
            embed.set_footer(text="Ã°ÂÂÂ­ Think of your answer, then tap Reveal  ÃÂ·  Only you see the result")
            await channel.send(embed=embed, view=FlashcardView(q))

        await asyncio.sleep(1.5)

    closing = discord.Embed(
        title="Ã¢ÂÂ³  Session Running",
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

    # Check if cycle complete Ã¢ÂÂ reset scores every 10 sessions
    if session_count % SESSIONS_PER_CYCLE == 0:
        cycle_num = session_count // SESSIONS_PER_CYCLE
        SESSION_DATA["scores"] = {}
        reset_embed = discord.Embed(
            title=f"Ã°ÂÂÂ  Cycle #{cycle_num} Complete!",
            description=(
                f"The **{SESSIONS_PER_CYCLE}-session scoreboard** has been reset.\n\n"
                f"All scores back to zero Ã¢ÂÂ a fresh start for everyone!\n"
                f"Streaks are preserved. Good luck in Cycle #{cycle_num + 1}! Ã°ÂÂÂ"
            ),
            color=0x5865F2,
            timestamp=datetime.datetime.utcnow()
        )
        await channel.send(embed=reset_embed)
        print(f"Cycle {cycle_num} complete Ã¢ÂÂ scores reset!")

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
            user_rank = rank_map.get(s["username"], "Ã¢ÂÂ")

            embed = discord.Embed(
                title=f"Ã°ÂÂÂ  Your Report Card",
                color=0x5865F2,
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_author(name=member.display_name, icon_url=member.display_avatar.url)

            # Overall
            embed.add_field(
                name="Overall",
                value=(
                    f"Rank: **#{user_rank}**  ÃÂ·  {badge} {rank_title}\n"
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
                    bar = "Ã¢ÂÂ°"*bar_f + "Ã¢ÂÂ±"*(10-bar_f)
                    meta = SUBJECT_META.get(subj, {"emoji":"Ã°ÂÂÂ"})
                    sub_lines.append(f"{meta['emoji']} **{subj}**  {bar}  {sub_acc}% ({stat['correct']}/{stat['total']})")

                embed.add_field(name="Ã°ÂÂÂ Subject Breakdown", value="\n".join(sub_lines), inline=False)
                embed.add_field(
                    name="Ã°ÂÂÂª Strength & Weakness",
                    value=f"Best: **{best_sub[0]}**  ÃÂ·  Needs work: **{worst_sub[0]}**",
                    inline=False
                )

            # Motivational line
            if acc >= 80:
                msg = "Excellent work! You're on fire Ã°ÂÂÂ¥"
            elif acc >= 60:
                msg = "Good job! Keep pushing Ã°ÂÂÂª"
            elif acc >= 40:
                msg = "Not bad Ã¢ÂÂ review your weak subjects Ã°ÂÂÂ"
            else:
                msg = "Don't give up! Consistency beats talent Ã°ÂÂÂ±"
            embed.set_footer(text=msg)

            await member.send(embed=embed)
            await asyncio.sleep(0.5)  # avoid rate limit
        except discord.Forbidden:
            print(f"Can't DM {user_id} Ã¢ÂÂ DMs closed")
        except Exception as ex:
            print(f"Report card error for {user_id}: {ex}")


# Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂ BOT Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ

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
        await interaction.followup.send("Ã¢ÂÂ Scores saved to Gist! You can now edit the Gist safely.", ephemeral=True)
    else:
        await interaction.followup.send("Ã¢ÂÂ Save failed. Check logs.", ephemeral=True)


@bot.tree.command(name="editscore", description="[Admin] Manually set a player's points")
async def editscore_cmd(interaction: discord.Interaction, username: str, points: int):
    scores = SESSION_DATA.setdefault("scores", {})
    # Find by username
    for uid, s in scores.items():
        if s["username"].lower() == username.lower():
            old = s["points"]
            s["points"] = points
            await interaction.response.send_message(
                f"Ã¢ÂÂ **{s['username']}**: `{old} pts` Ã¢ÂÂ `{points} pts`",
                ephemeral=True
            )
            return
    await interaction.response.send_message(
        f"Ã¢ÂÂ Player `{username}` not found in current session.",
        ephemeral=True
    )


if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
