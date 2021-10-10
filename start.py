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
    msg = await m.reply_text(text=f"Downloading Video Link ...")
    
    if " | " in m.text:
        url , cfname = m.text.split(" | ", 1)
    else:
        url = m.text
    
    try:
        """Downloading Section."""
        
        if not os.path.isdir(download_path):
            os.mkdir(download_path)
        
        start = time.time()
        filename = os.path.join(download_path, os.path.basename(url))
        file_path = await download_file(url, filename, msg, start, bot)
        print(f"file downloaded to {file_path} with name: {filename}")
        await msg.edit(f"Successfully Downloaded to : `{file_path}`")
    except Exception as e:
        print(e)
        await msg.edit(f"Download link is invalid or not accessible ! \n\n **Error:** {e}")        
    
    if " | " in m.text:
        filename = cfname
    probe = await stream_creator(file_path)
    video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
    width = int(video_stream['width'] if 'width' in video_stream else 0)
    height = int(video_stream['height'] if 'height' in video_stream else 0)
    thumbnail = await thumb_creator(file_path)
    size_of_file = os.path.getsize(file_path)
    size = get_size(size_of_file)
    try:
        start = time.time()
        await bot.send_video(
            chat_id=m.chat.id,
            progress=progress_for_pyrogram,
            progress_args=(
                "Uploading Video ...",
                msg,
                start
            ),
            file_name=filename,
            video=file_path,
            width=width,
            height=height,
            thumb=str(thumbnail),
            caption=f"`{filename}` [{size}]",
            reply_to_message_id=m.message_id
        )
    except Exception as e:
        os.remove(file_path)
        print(e)
        await msg.edit(f"Uploading Failed **Error:** {e}")    
    
    await msg.delete()
    os.remove(file_path)
    
bot.run()
