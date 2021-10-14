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

HELP_TXT = """
    Please Send Your link like bellow:
  **URL** | **Custom_File_Name.Extension**
    
    Example:
   `http://aaa.bbb.ccc/ddd.eee` | **fff.ggg**
    
    if you want to convert a media 
    that uploaded as document, to video with thumb,
    forward your media to bot and then send /c2v
    as reply to that.
"""

@bot.on_message(filters.command(["start"]))
async def start(bot , m):
    """Send a message when the command /start is issued."""
    await m.reply_text(text=f"Hi . I Can Upload Your Direct Link to Telegram.\nI also can convert document media to video with thumb.\nSee /help for more info!")

    
@bot.on_message(filters.command(["help"]))
async def help(bot , m):
    """Send a message when the command /help is issued."""
    await m.reply_text(text=f"{HELP_TXT}")   

@bot.on_message(filters.command(["c2v"]))
async def to_video(bot , u):
    m = u.reply_to_message
    if m.audio or m.photo or m.voice or m.location or m.contact:
        await m.reply_text(text=f"Wrong File Type ...")
        return
    else:  
        ft = m.document or m.video
        if ft.file_name:
            fullname = ft.file_name
        else:
            fullname = m.date + ".mp4"
        fsize = get_size(ft.file_size)
        fn = os.path.splitext(fullname)[0]
        if ft.mime_type.startswith("video/"):
            try:
                if not os.path.isdir(download_path):
                    os.mkdir(download_path)
                mes2 = await m.reply_text(
                    text=f"**Processing...**",
                    quote=True
                )
                c_time = time.time()
                file_path = await bot.download_media(
                    m,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        "Downloading Status ...",
                        mes2,
                        c_time
                    )
                )
                await mes2.edit(f"Generating thumbnail ...")
                #await asyncio.sleep(5)
                
                #out, err, rcode, pid = await execute(f"ffmpeg -i /Downloads/aaa.mkv -c copy /Downloads/bbb.mp4 -y")
                #if rcode != 0:
                    #await mes2.edit(f"**FFmpeg: Error Occured.**`{err}`\n`{out}`\n`{rcode}`\n`{pid}`")
                    #os.remove("/Downloads/aaa.mkv")
                    #return
                
                #file_path2 = "/Downloads/bbb.mp4"
                size_of_file = os.path.getsize(file_path)
                size = get_size(size_of_file)
                #await mes2.edit(f"Generating thumbnail ...`{err}`\n`{out}`\n`{rcode}`\n`{pid}`\n\n[{size}]")
                #await mes2.edit(f"Generating thumbnail ...")
                #await asyncio.sleep(5)
                probe = await stream_creator(file_path)
                video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
                width = int(video_stream['width'] if 'width' in video_stream else 0)
                height = int(video_stream['height'] if 'height' in video_stream else 0)
                thumbnail = await thumb_creator(file_path)
                fnext = fn + ".mp4"
                duration = int(float(probe["format"]["duration"]))                
                c_time = time.time()
                await mes2.edit(f"Trying to Upload as Video ...")
                #await asyncio.sleep(5)
                await bot.send_video(
                    chat_id=m.chat.id,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        "Uploading Status ...",
                        mes2,
                        c_time
                    ),
                    file_name=fnext,
                    video=file_path,
                    width=width,
                    height=height,
                    duration=duration,
                    thumb=str(thumbnail),
                    caption=f"`{fnext}` [{size}]",
                    reply_to_message_id=m.message_id
                )
                await mes2.delete()
                #os.remove("/Downloads/aaa.mkv")
                os.remove(file_path)
            except Exception as e:
                await mes2.edit(f"Uploading as Video Failed **Error:**\n\n{e}")
        else:
            await m.reply_text(text=f"Wrong File Type ...")
            return

@bot.on_message(filters.private & filters.text)
async def leecher(bot , m):

    if " | " in m.text:
        url , cfname = m.text.split(" | ", 1)
    else:
        url = m.text
    
    msg = await m.reply_text(text=f"Analyzing Your Link ...")
    
    try:        
        if not os.path.isdir(download_path):
            os.mkdir(download_path)
        
        start = time.time()
        filename = os.path.join(download_path, os.path.basename(url))
        file_path = await download_file(url, filename, msg, start, bot)
        print(f"file downloaded to {file_path} with name: {filename}")
        await msg.edit(f"Successfully Downloaded .")
        filename = os.path.basename(file_path)
    except Exception as e:
        print(e)
        await msg.edit(f"Download link is invalid or not accessible ! \n\n **Error:** {e}")        
    
    mt = mimetypes.guess_type(str(file_path))[0]
    
    if mt and mt.startswith("video/"):
        fsw = "vid"
    elif mt and mt.startswith("audio/"):
        fsw = "aud"
    else:
        fsw = "app"
    
    if " | " in m.text:
        filename = cfname
        cfnmt = mimetypes.guess_type(str(cfname))[0]
        if cfnmt and cfnmt.startswith("video/"):
            fsw = "vid"
        elif cfname and cfnmt.startswith("audio/"):
            fsw = "aud"
        else:
            fsw = "app"
    size_of_file = os.path.getsize(file_path)
    size = get_size(size_of_file)
    
    if fsw == "vid":
        try:
            probe = await stream_creator(file_path)
            video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
            width = int(video_stream['width'] if 'width' in video_stream else 0)
            height = int(video_stream['height'] if 'height' in video_stream else 0)
            duration = int(float(probe["format"]["duration"]))
            await msg.edit(f"Generating thumbnail ...")
            thumbnail = await thumb_creator(file_path)
            
            start = time.time()
            await msg.edit(f"Uploading as Video ...")
            await bot.send_video(
                chat_id=m.chat.id,
                progress=progress_for_pyrogram,
                progress_args=(
                    "Uploading as Video Started ...",
                    msg,
                    start
                ),
                file_name=filename,
                video=file_path,
                width=width,
                height=height,
                duration=duration,
                thumb=str(thumbnail),
                caption=f"`{filename}` [{size}]",
                reply_to_message_id=m.message_id
            )
        except Exception as e:
            fsw = "app"
            await msg.edit(f"Uploading as Video Failed **Error:** {e} \n Trying to Upload as File in 3 second!")
            await asyncio.sleep(3)
    
    if fsw == "aud":
        try:
            duration = 0
            metadata = extractMetadata(createParser(file_path))
            if metadata and metadata.has("duration"):
                duration = metadata.get("duration").seconds

            start = time.time()
            await msg.edit(f"Uploading as Audio ...")
            await bot.send_audio(
                chat_id=m.chat.id,
                progress=progress_for_pyrogram,
                progress_args=(
                    "Uploading as Audio Started ...",
                    msg,
                    start
                ),
                file_name=filename,
                duration=duration,
                audio=file_path,
                caption=f"`{filename}` [{size}]",
                reply_to_message_id=m.message_id
            )
        except Exception as e:
            fsw = "app"
            await msg.edit(f"Uploading as Audio Failed **Error:** {e} \n Trying to Upload as File in 3 second!")
            await asyncio.sleep(3)
    
    if fsw == "app":
        try:
            start = time.time()
            await msg.edit(f"Uploading as File ...")
            await bot.send_document(
                chat_id=m.chat.id,
                progress=progress_for_pyrogram,
                progress_args=(
                    "Uploading as File Started ...",
                    msg,
                    start
                ),
                file_name=filename,
                document=file_path,
                force_document=True,
                caption=f"`{filename}` [{size}]",
                reply_to_message_id=m.message_id
            )
        except Exception as e:
            await msg.edit(f"Uploading as File Failed **Error:** {e}")
            os.remove(file_path)
            return
    
    await msg.delete()
    os.remove(file_path)
    
bot.run()
