from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyromod import listen
from urllib.parse import quote_plus, unquote
import math
from helpers.download_from_url import download_file, get_size
from helpers.file_handler import send_to_transfersh_async, progress
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata
from helpers.display_progress import progress_for_pyrogram, humanbytes
import os
import time
import datetime
import aiohttp
import asyncio
import mimetypes
from helpers.tools import execute
from helpers.ffprobe import stream_creator
from helpers.thumbnail_video import thumb_creator
from helpers.url_uploader import leecher2
from helpers.video_renamer import rnv2
from helpers.audio_renamer import rna2
from helpers.file_renamer import rnf2
from helpers.vconverter import to_video2
from helpers.media_info import cinfo2

BOT_TOKEN = os.environ.get("BOT_TOKEN")
API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")

bot = Client(
    "Bot",
    bot_token = BOT_TOKEN,
    api_id = API_ID,
    api_hash = API_HASH
)
                          
download_path = "Downloads/"

if not os.path.isdir(download_path):
    os.mkdir(download_path)

HELP_TXT = """
A Simple Telegram Bot to 
Upload Files From **Direct** and **Google Drive** Links,
Convert Document Media to Video,
and Rename Audio/Video/Document Files.

/upload : reply to your url .
    
    `http://aaa.bbb.ccc/ddd.eee` | **fff.ggg**
    or
    `http://aaa.bbb.ccc/ddd.eee`

/c2v : reply to your document to convert it into streamable video.
    
/rnv : reply to your video. Example:
    
    `/rnv | videoname`
    
/rna : reply to your audio. \"`-`\" : leave without change.

    `/rna | audioname | title | artists`
    `/rna | audioname`
    `/rna | - | title`
    `/rna | - | - | artists`
    
/rnf : reply to your document. Example:

    `/rnf | filename.ext`
"""

@bot.on_message(filters.command(["start"]))
async def start(bot , m):
    """Send a message when the command /start is issued."""
    await m.reply_text(text=f"Hi\n\nSee /help for More Info!")

    
@bot.on_message(filters.command(["help"]))
async def help(bot , m):
    """Send a message when the command /help is issued."""
    await m.reply_text(text=f"{HELP_TXT}")   

@bot.on_message(filters.private & filters.command(["rnv"]))
async def rnv1(bot , u):
    await rnv2(bot,u)
    
@bot.on_message(filters.private & filters.command(["rna"]))
async def rna1(bot , u):
    await rna2(bot,u)
    
@bot.on_message(filters.private & filters.command(["rnf"]))
async def rnf1(bot , u):
    await rnf2(bot,u)    
    
@bot.on_message(filters.private & filters.command(["c2v"]))
async def to_video1(bot , u):
    await to_video2(bot , u)
    
@bot.on_message(filters.private & (filters.audio | filters.document | filters.video))
async def cinfo1(bot , m):
    await cinfo2(bot , m)

@bot.on_message(filters.private & filters.command(["upload"]))
async def leecher1(bot , u):
    await leecher2(bot,u)
    
bot.run()
