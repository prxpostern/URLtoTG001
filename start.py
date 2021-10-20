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
    or
    `http://aaa.bbb.ccc/ddd.eee`
    
    /upload : reply to your url to start uploading from direct link.
    /c2v : reply to your document To Convert It Into Streamable video File.
    /rename_video : Example = `/rename_video | myname`
"""

@bot.on_message(filters.command(["start"]))
async def start(bot , m):
    """Send a message when the command /start is issued."""
    await m.reply_text(text=f"Hi . I Can Upload Your Direct Link to Telegram.\nI Can Convert Document Media to Video.\nI Can Reanme Video Files.\nSee /help for more info!")

    
@bot.on_message(filters.command(["help"]))
async def help(bot , m):
    """Send a message when the command /help is issued."""
    await m.reply_text(text=f"{HELP_TXT}")   

@bot.on_message(filters.command(["rename_video"]))
async def video_renamer(bot , u):
    
    if not u.reply_to_message:
        await u.reply_text(text=f"Reply To Your Video !\nExample:\n`/rename_video | onlyfilename`")
        return
    
    m = u.reply_to_message
    ft = m.document or m.video
    fsize = get_size(ft.file_size)
    if m.audio or m.photo or m.voice or m.location or m.contact:
        await m.reply_text(text=f"Please Reply To Video !\nMimeType: {ft.mime_type}")
        return
    else:
        if ft.file_name:
            oldname = ft.file_name
            oldname = oldname.replace('%40','@')
            oldname = oldname.replace('%25','_')
            oldname = oldname.replace(' ','_')
        else:
            oldname = "Video_CHATID" + str(m.chat.id) + "_DATE" + str(m.date) + ".mp4"

    if ft.mime_type.startswith("video/"):
        if not "|" in u.text:
            await u.reply_text(text=f"Please Type New Filename !\nExample:\n`**/rename_video | <onlyfilename>**`")
            return
        else:
            args = u.text.split("|")
            if len(args) <= 1:
                await u.reply_text(text=f"Please Type New Filename !\nExample:\n`**/rename_video | <onlyfilename>**`")
                return
            else:
                cmd , newname = u.text.split("|", 1)
                cmd = cmd.strip()
                if os.path.splitext(newname)[1]:
                    await u.reply_text(text=f"Dont Type Extension !\nExample:\n`**/rename_video | <onlyfilename>**`")
                    return
                else:
                    newname = newname.strip() + ".mp4"
                    msg1 = await u.reply_text(text=f"Current Filename: `{oldname}` [{fsize}]\nNew Name: `{newname}`")
                    msg2 = await u.reply_text(text=f"Trying To Download Media")
                    #if not os.path.isdir(download_path):
                    #    os.mkdir(download_path)
                    c_time = time.time()
                    file_path = await bot.download_media(
                        m,
                        file_name=oldname,
                        progress=progress_for_pyrogram,
                        progress_args=(
                            "Downloading Status ...",
                            msg2,
                            c_time
                        )
                    )
                    if not file_path:
                        await msg1.delete()
                        await msg2.edit(f"Download Failed !")
                        try:
                            os.remove(file_path)
                        except:
                            pass
                        return
                    else:
                        await msg2.edit(f"🌄 Generating thumbnail ...")
                        probe = await stream_creator(file_path)
                        video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
                        width = int(video_stream['width'] if 'width' in video_stream else 0)
                        height = int(video_stream['height'] if 'height' in video_stream else 0)
                        thumbnail = await thumb_creator(file_path)
                        duration = int(float(probe["format"]["duration"]))
                        try:
                            await msg2.edit(f"⬆️ Trying to Upload as Video ...")
                            c_time = time.time()
                            await bot.send_video(
                                chat_id=m.chat.id,
                                file_name=newname,
                                video=file_path,
                                width=width,
                                height=height,
                                duration=duration,
                                thumb=str(thumbnail),
                                caption=f"`{newname}` [{fsize}]",
                                reply_to_message_id=m.message_id,
                                progress=progress_for_pyrogram,
                                progress_args=(
                                    "⬆️ Uploading Status ...",
                                    msg2,
                                    c_time
                                )
                            )
                            await msg1.delete()
                            await msg2.delete()
                            try:
                                os.remove(file_path)
                            except:
                                pass
                        except Exception as e:
                            await msg1.delete()
                            await msg2.edit(f"❌ Uploading as Video Failed **Error:**\n\n{e}")
                            try:
                                os.remove(file_path)
                            except:
                                pass
    else:
        await m.reply_text(text=f"Please Reply To Video !\nMimeType: {ft.mime_type}")
        return

@bot.on_message(filters.command(["c2v"]))
async def to_video(bot , u):
    if not u.reply_to_message:
        await u.reply_text(text=f"Reply To Your Media !")
        return
    m = u.reply_to_message
    if m.audio or m.photo or m.voice or m.location or m.contact:
        await m.reply_text(text=f"Wrong File Type ...")
        return
    else:  
        ft = m.document or m.video
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
                file_name=fullname,
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

@bot.on_message(filters.private & filters.command(["upload"]))
async def leecher(bot , u):
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
    
    try:        
        if not os.path.isdir(download_path):
            os.mkdir(download_path)
        
        start = time.time()
        filename = os.path.join(download_path, os.path.basename(url))
        filename = filename.replace('%25','_')
        filename = filename.replace(' ','_')
        filename = filename.replace('%40','@')
        file_path = await download_file(url, filename, msg, start, bot)
        print(f"file downloaded to {file_path} with name: {filename}")
        await msg.edit(f"Successfully Downloaded .")
        filename = os.path.basename(file_path)
        filename = filename.replace('%40','@')
        filename = filename.replace('%25','_')
        filename = filename.replace(' ','_')
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
