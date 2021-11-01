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

download_path = "Downloads/"

async def leecher2(bot , u):
    if not u.reply_to_message:
        await u.reply_text(text=f"Reply To Your Direct Link !")
        return
    
    m = u.reply_to_message
    
    if "|" in m.text:
        url , cfname = m.text.split("|", 1)
        url = url.strip()
        cfname = cfname.strip()
        cfname = cfname.replace('%40','@')
    else:
        url = m.text.strip()
        if os.path.splitext(url)[1]:
            ofn = os.path.basename(url)
        else:
            await m.reply_text(text=f"I Could nott Determine The FileType !\nPlease Use Custom Filename With Extension\nSee /help")
            return
    
    msg = await m.reply_text(text=f"Analyzing Your Link ...")
    
    filename = os.path.join(download_path, os.path.basename(url))
    filename = filename.replace('%25','_')
    filename = filename.replace(' ','_')
    filename = filename.replace('%40','@')
    await msg.edit(f"Successfully Downloaded .")
    
    start = time.time()
    try:
        file_path = await download_file(url, filename, msg, start, bot)
        print(f"file downloaded to {file_path} with name: {filename}")
    except Exception as e:
        print(e)
        await msg.edit(f"Download link is invalid or not accessible ! \n\n **Error:** {e}")
        return
    
    filename = os.path.basename(file_path)
    filename = filename.replace('%40','@')
    filename = filename.replace('%25','_')
    filename = filename.replace(' ','_')
    
    mt = mimetypes.guess_type(str(file_path))[0]
    if mt and mt.startswith("video/"):
        fsw = "vid"
    elif mt and mt.startswith("audio/"):
        fsw = "aud"
    else:
        fsw = "app"
    
    if "|" in m.text:
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
            await msg.delete()
            try:
              os.remove(file_path)
            except:
              pass
            return
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
            await msg.delete()
            try:
              os.remove(file_path)
            except:
              pass
            return
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
            await msg.delete()
            try:
              os.remove(file_path)
            except:
              pass
        except Exception as e:
            await msg.edit(f"Uploading as File Failed **Error:** {e}")
            try:
              os.remove(file_path)
            except:
              pass
            return
