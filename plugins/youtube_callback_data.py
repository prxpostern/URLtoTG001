import asyncio, logging, os, re, shutil, mimetypes, time

from pyrogram import Client, filters
from pyrogram.types import (
    InputMediaAudio,
    InputMediaVideo,
)

#from ytdlbot import Config
from main import Config
from helpers.util import media_duration, width_and_height
from helpers.ytdlfunc import yt_download
from helpers.tgupload import upaudio, upvideo

logger = logging.getLogger(__name__)
ytdata = re.compile(r"^(Video|Audio)_(\d{1,3})_(empty|none)_([\w\-]+)$")


@Client.on_callback_query(filters.regex(ytdata))
async def catch_youtube_dldata(_, q):
    qq = q.message
    qr = q.message.reply_to_message
    cb_data = q.data
    logger.info(cb_data)
    # caption = q.message.caption
    user_id = q.from_user.id
    # Callback Regex capturing
    media_type = q.matches[0].group(1)
    format_id = q.matches[0].group(2)
    av_codec = q.matches[0].group(3)
    video_id = q.matches[0].group(4)

    userdir = os.path.join(os.getcwd(), Config.DOWNLOAD_DIRECTORY, str(user_id), video_id)

    if not os.path.isdir(userdir):
        os.makedirs(userdir)
    
    logger.info(f"Downloading...!")
    await q.edit_message_caption("Downloading...!")
    # await q.edit_message_reply_markup([[InlineKeyboardButton("Processing..")]])

    fetch_media, caption = await yt_download(
        video_id, media_type, av_codec, format_id, userdir
    )
    
    if not fetch_media:
        await asyncio.gather(q.message.reply_text(caption), q.message.delete())
        shutil.rmtree(userdir, ignore_errors=True)
        return
    else:
        logger.info(f'fetch_media: {fetch_media} -- caption: {caption}')
        logger.info(os.listdir(userdir))
        file_name = None
        for content in os.listdir(userdir):
            if ".jpg" not in content:
                file_name = os.path.join(userdir, content)

    if not os.path.exists(file_name):
        await asyncio.gather(q.message.reply_text("Failed"), q.message.delete())
        logger.info("Media not found")
        return
    
    qt = qr.text
    cfname = None
    if "|" in qt:
        cfname = qt.split("|", 1)[1]
        cfname = cfname.strip()
        cfname = cfname.replace('%40','@')

    await q.edit_message_caption(f"download finished .")
    
    time.sleep(3)
    mt = mimetypes.guess_type(str(file_name))[0]
    if mt and mt.startswith("video/"):
        uvstatus = await upvideo(_, qr, qq, file_name, cfname)
        if uvstatus:
            uvstatus = await upvideo(_, qr, qq, file_name, cfname)
        else:
            return
    elif mt and mt.startswith("audio/"):
        uastatus = await upaudio(_, qr, qq, file_name, cfname)
        if uastatus:
            uastatus = await upaudio(_, qr, qq, file_name, cfname)
        else:
            return
    else:
        logger.info("CB_Upload_Error")
