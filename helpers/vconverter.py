from pyrogram import Client, filters
#from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
#from urllib.parse import quote_plus, unquote
from helpers.download_from_url import get_size
#from helpers.file_handler import send_to_transfersh_async, progress
#from hachoir.parser import createParser
#from hachoir.metadata import extractMetadata
from helpers.display_progress import progress_for_pyrogram, humanbytes
import os, json, time, datetime, aiohttp, asyncio, mimetypes, math, logging
from helpers.tools import execute, clean_up
#from helpers.ffprobe import stream_creator
from helpers.thumbnail_video import thumb_creator

logger = logging.getLogger(__name__)
status = False

async def to_video2(bot , u):
    
    global status
    probe2 = None
    
    if not u.reply_to_message:
        await u.reply_text(text=f"Reply To Your Video !", quote=True)
        return
    
    logger.info(f"status: {status}")
    if status:
        await u.reply_text(text=f"wait until last process finish. then try again.", quote=True)
        return
    
    m = u.reply_to_message
    
    if m.video or m.document:
        ft = m.document or m.video
        fsize = get_size(ft.file_size)
    else:
        await m.reply_text(text=f"Please Reply To Your Video !\n\nExample:\n**/rnv | filename**\n\nsee /help.", quote=True)
        logger.info(f"No Video File !")
        return
    
    video_types = [
        '.avi', '.mkv', '.mp4', '.wmv', '.mpeg', '.3g2',
        '.divx', '.flv', '.webm', '.rm', '.mov', '.m4p',
        '.f4v', '.swf', '.html5', '.asf', '.ogv', '.divx',
        '.vob', '.m4v', '.mpg', '.mp2', '.3gp', '.mpv'
    ]
    
    if ft.mime_type and ft.mime_type.startswith("video/"):
        pass
    elif (ft.file_name) and (os.path.splitext(ft.file_name)[1] in video_types):
        pass
    else:
        await m.reply_text(text=f"Please Reply To Your Video !\n\nExample:\n**/rnv | filename**\n\nsee /help.", quote=True)
        logger.info(f"No Video File !")
        return
    
    ft = m.document or m.video
    
    tnow = str(datetime.datetime.now())
    tnow = tnow.replace(' ','_')
    tnow = tnow.replace('-','_')
    tnow = tnow.replace(':','_')
    tnow = tnow.replace('/','_')
    tnow = tnow.replace('.','_')
    print("tnow = ", tnow)
  
    oldname = "Video_CHATID" + str(m.chat.id) + "_DATE_" + str(tnow) + ".mp4"
    if ft.file_name:
        oldname = ft.file_name
        oldname = oldname.replace('%40','@')
        oldname = oldname.replace('%25','_')
        oldname = oldname.replace(' ','_')

    print("oldname = ", oldname)
    fn = os.path.splitext(oldname)[0]
    
    #################################################################### Downloading Video
    status = True
    logger.info(f"status: {status}")
            
    msg = await m.reply_text(text=f"⬇️ Trying To Download Video ...", quote=True)
    
    c_time = time.time()
    file_path = await bot.download_media(
        m,
        file_name=oldname,
        progress=progress_for_pyrogram,
        progress_args=(
            "⬇️ Downloading Video:",
            msg,
            c_time
        )
    )
    
    await msg.edit(f"🌄 Generating thumbnail ...")

    """
    probe2 = await execute(f"ffprobe -v quiet -hide_banner -show_format -show_streams -print_format json '{file_path}'")
    if not probe2:
        status = False
        logger.info(f"status: {status}")
        await clean_up(file_path)
        logger.info(f"Deleted: {file_path}")
        await msg.edit_text("Some Error Occured while Fetching Details...")
        return

    probe = json.loads(probe2[0])
    #probe = await stream_creator(file_path)
    #logger.info(probe)
    
    duration = int(float(probe["format"]["duration"]))

    video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
    width = int(video_stream['width'] if 'width' in video_stream else 0)
    height = int(video_stream['height'] if 'height' in video_stream else 0)
    """
    
    thumbnail, duration, width, height = await thumb_creator(file_path)

    fnext = fn + ".mp4"
    await msg.edit(f"⬆️ Trying to Upload as Video ...")
    
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
            reply_to_message_id=m.id,
            progress=progress_for_pyrogram,
            progress_args=(
                "⬆️ Uploading as Video:",
                msg,
                c_time
            )
        )
                
        status = False
        logger.info(f"status: {status}")
        await msg.delete()
        await clean_up(file_path)
    except Exception as e:
        status = False
        logger.info(f"status: {status}")
        await msg.edit(f"❌ Uploading as Video Failed **Error:**\n\n{e}")
        await clean_up(file_path)

