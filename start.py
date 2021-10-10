from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyromod import listen
from urllib.parse import quote_plus
import math
from download_from_url import download_file, get_size
from file_handler import send_to_transfersh_async, progress
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata
from display_progress import progress_for_pyrogram, humanbytes
import os
import time
import datetime
import aiohttp
import asyncio
from tools import execute

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

HELP_TXT = """
    URL | Custom_File_Name.Extension
"""

@bot.on_message(filters.command(["start"]))
async def start(bot , m):
    """Send a message when the command /start is issued."""
    await m.reply_text(text=f"Send Video Link")

    
@bot.on_message(filters.command(["help"]))
async def help(bot , m):
    """Send a message when the command /help is issued."""
    await m.reply_text(text=f"{HELP_TXT}")   

@bot.on_message(filters.private & filters.text)
async def leecher(bot , m):
    """Echo the user message."""

    if " | " in m.text:
        url , cfname = m.text.split(" | ", 1)
    else:
        url = m.text
    
    start = time.time()
    filename = os.path.join(download_path, os.path.basename(url))
    file_path = await download_file(url, filename, msg, start, bot)
            
    print(f"file downloaded to {file_path}")
        
        """ User Input Section """
        await msg2.edit(f"Successfully Downloaded to : `{file_path}`")
        msg3 = await update2.reply("**Step2:** Enter The Extension : \n Examples: \n `_.mkv` \n `_320p.mp4` \n `new.mp3` \n `32k.aac` \n `_.mka` \n\n To Cancel press /cancel")
        

def main():
    """Start the bot."""
    print("\nBot started ...\n")
    bot.run_until_disconnected()

if __name__ == '__main__':
    main()
