from pyrogram import Client, filters
#from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
#from urllib.parse import quote_plus, unquote
#import math
from helpers.download_from_url import get_size
#from helpers.file_handler import send_to_transfersh_async, progress
#from hachoir.parser import createParser
#from hachoir.metadata import extractMetadata
from helpers.display_progress import progress_for_pyrogram, humanbytes
import os, time, datetime, aiohttp, asyncio, mimetypes, logging
from helpers.tools import execute, clean_up
#from helpers.ffprobe import stream_creator
#from helpers.thumbnail_video import thumb_creator

logger = logging.getLogger(__name__)
status = False

async def rnf2(bot , u):
  
  global status
  file_path = None
  
  if not u.reply_to_message:
    await u.reply_text(text=f"Please Reply To Your Document !\n\nExample:\n**/rnf | filename.ext**\n\nsee /help.", quote=True)
    return
  
  logger.info(f"status: {status}")
  if status:
    await u.reply_text(text=f"wait until last process finish. status: {status}", quote=True)
    return
  
  m = u.reply_to_message
  
  if m.video:
    ft = m.video
  elif m.audio:
    ft = m.audio
  elif m.document:
    ft = m.document
  else:
    await m.reply_text(text=f"Please Reply to (audio-video-document) files !\n\nSee /help", quote=True)
    return

  fsize = get_size(ft.file_size)
  
  if not "|" in u.text:
    await m.reply_text(text=f"Please Type New Filename with extension !\n\nExample:\n**/rnf | filename.ext**\n\nsee /help.", quote=True)
    return
  else:
    args = u.text.split("|")
    if len(args) == 2:
      cmd , newname = u.text.split("|", 1)
      newname = newname.strip()
      if not os.path.splitext(newname)[1]:
        await m.reply_text(text=f"Type Extension !\n\nExample:\n**/rnf | filename.ext\n\nsee /help.**", quote=True)
        return
      else:
        tnow = str(datetime.datetime.now())
        tnow = tnow.replace(' ','_')
        tnow = tnow.replace('-','_')
        tnow = tnow.replace(':','_')
        tnow = tnow.replace('/','_')
        tnow = tnow.replace('.','_')
        print("tnow = ", tnow)
        
        ext = os.path.splitext(newname)[1]
        oldname = "File_CHATID" + str(m.chat.id) + "_DATE_" + str(tnow) + str(ext)
        if ft.file_name:
            oldname = ft.file_name
            oldname = oldname.replace('%40','@')
            oldname = oldname.replace('%25','_')
            oldname = oldname.replace(' ','_')

        print("oldname = ", oldname)
        msg = await m.reply_text(text=f"⬇️ Trying To Download Document", quote=True)
        
        #################################################################### Downloading Document
        status = True
        logger.info(f"status: {status}")
        
        c_time = time.time()
        file_path = await bot.download_media(
          m,
          file_name=oldname,
          progress=progress_for_pyrogram,
          progress_args=(
            "⬇️ Downloading Document:",
            msg,
            c_time
          )
        )
        if not file_path:
          status = False
          logger.info(f"status: {status}")
          await msg.edit(f"❌ Downloading Document Failed !")
          await clean_up(file_path)
          return
        try:
          await msg.edit(f"⬆️ Trying to Upload as Document ...")
          c_time = time.time()
          await bot.send_document(
            chat_id=m.chat.id,
            file_name=newname,
            document=file_path,
            force_document=True,
            caption=f"`{newname}` [{fsize}]",
            reply_to_message_id=m.id,
            progress=progress_for_pyrogram,
            progress_args=(
              "⬆️ Uploading as Document:",
              msg,
              c_time
            )
          )
          status = False
          logger.info(f"status: {status}")
          await msg.delete()
          await clean_up(file_path)
        except Exception as e:
          await msg.edit(f"❌ Uploading as Document Failed **Error:**\n\n{e}")
          status = False
          logger.info(f"status: {status}")
          await clean_up(file_path)
    else:
      await m.reply_text(text=f"are you kidding me ?\n\nExample:\n`/rnf | filename.ext`\n\nsee /hlep.", quote=True)
      return
