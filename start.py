from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyromod import listen
from urllib.parse import quote_plus, unquote
import math
from download_from_url import download_file, get_size
from file_handler import send_to_transfersh_async, progress
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata
from display_progress import progress_for_pyrogram, humanbytes
from url_uploader import leecher2
from video_renamer import video_renamer2
from vconverter import to_video2
import os
import time
import datetime
import aiohttp
import asyncio
import mimetypes
from tools import execute
from ffprobe import stream_creator
from thumbnail_video import thumb_creator

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
    Please Send Your link like bellow:
  **URL** | **Custom_File_Name.Extension**
    
    Example:
   `http://aaa.bbb.ccc/ddd.eee` | **fff.ggg**
    or
    `http://aaa.bbb.ccc/ddd.eee`
    
    /upload : reply to your url to start uploading from direct link.
    
    /c2v : reply to your document To Convert It Into Streamable video File.
    
    /rnv : reply to your video `/rename_video | newname`
"""

@bot.on_message(filters.command(["start"]))
async def start(bot , m):
    """Send a message when the command /start is issued."""
    await m.reply_text(text=f"Hi . I Can Upload Your Direct Link to Telegram.\nI Can Convert Document Media to Video.\nI Can Reanme Video Files.\nSee /help for more info!")

    
@bot.on_message(filters.command(["help"]))
async def help(bot , m):
    """Send a message when the command /help is issued."""
    await m.reply_text(text=f"{HELP_TXT}")   

@bot.on_message(filters.command(["rnv"]))
async def video_renamer1(bot , u):
    await video_renamer2(bot,u)
    
@bot.on_message(filters.command(["c2v"]))
async def to_video1(bot , u):
    await to_video2(bot , u)
    
@bot.on_message(filters.private & filters.command(["upload"]))
async def leecher1(bot , u):
    await leecher2(bot,u)
    
bot.run()
