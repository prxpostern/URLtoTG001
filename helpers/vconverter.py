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

async def to_video2(bot , u):
    if not u.reply_to_message:
        await u.reply_text(text=f"Reply To Your Media !")
        return
    m = u.reply_to_message
    if m.audio or m.photo or m.voice or m.location or m.contact:
        await m.reply_text(text=f"Wrong File Type ...")
        return
    else:  
        ft = m.document or m.video
        tempname = "Video_CHATID" + str(m.chat.id) + "_DATE" + str(m.date) + ".mp4"
        if ft.file_name:
            fullname = ft.file_name
            fullname = fullname.replace('%40','@')
            fullname = fullname.replace('%25','_')
            fullname = fullname.replace(' ','_')
        else:
            fullname = "Video_CHATID" + str(m.chat.id) + "_DATE" + str(m.date) + ".mp4"
        fsize = get_size(ft.file_size)
        fn = os.path.splitext(fullname)[0]
        if ft.mime_type.startswith("video/"):
            mes2 = await m.reply_text(
                text=f"**Processing...**",
                quote=True
            )
            c_time = time.time()
            file_path = await bot.download_media(
                m,
                file_name=tempname,
                progress=progress_for_pyrogram,
                progress_args=(
                    "Downloading Status ...",
                    mes2,
                    c_time
                )
            )
            await mes2.edit(f"🌄 Generating thumbnail ...")
            probe = await stream_creator(file_path)
            duration = int(float(probe["format"]["duration"])) 
            video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
            width = int(video_stream['width'] if 'width' in video_stream else 0)
            height = int(video_stream['height'] if 'height' in video_stream else 0)
            thumbnail = await thumb_creator(file_path)
            fnext = fn + ".mp4"
            await mes2.edit(f"⬆️ Trying to Upload as Video ...")
            try:
                c_time = time.time()
                await bot.send_video(
                    chat_id=m.chat.id,
                    file_name=fnext,
                    video=file_path,
                    width=width,
                    height=height,
                    duration=duration,
                    thumb=str(thumbnail),
                    caption=f"`{fnext}` [{fsize}]",
                    reply_to_message_id=m.message_id,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        "⬆️ Uploading Status ...",
                        mes2,
                        c_time
                    )
                )
                await mes2.delete()
                try:
                    os.remove(file_path)
                except:
                    pass
            except Exception as e:
                await mes2.edit(f"❌ Uploading as Video Failed **Error:**\n\n{e}")
                try:
                    os.remove(file_path)
                except:
                    pass
        else:
            await m.reply_text(text=f"Wrong File Type ...")
            return
