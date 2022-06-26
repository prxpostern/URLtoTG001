from pyrogram import Client, filters
#from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
#from urllib.parse import quote_plus, unquote
from helpers.download_from_url import download_file, get_size
#from helpers.file_handler import send_to_transfersh_async, progress
#from hachoir.parser import createParser
#from hachoir.metadata import extractMetadata
from helpers.display_progress import progress_for_pyrogram, humanbytes
import os, time, datetime, aiohttp, asyncio, mimetypes, logging, math
from helpers.tools import execute, clean_up
from helpers.ffprobe import stream_creator
#from helpers.thumbnail_video import thumb_creator

logger = logging.getLogger(__name__)
status = False


async def rna2(bot , u):
  
  global status
  file_path = None
  
  if not u.reply_to_message:
    await u.reply_text(text=f"Please Reply To Your Audio !\n\nExample:\n**/rna | filename**\n\nsee /help.", quote=True)
    return
  
  logger.info(f"status: {status}")
  if status:
    await u.reply_text(text=f"wait until last process finish. then try again.", quote=True)
    return

  m = u.reply_to_message
  
  if m.audio or m.document:
    ft = m.document or m.audio
    fsize = get_size(ft.file_size)
  else:
    await m.reply_text(text=f"Please Reply To Audio Files !\n\nSee /help", quote=True)
    logger.info(f"No Audio File !")
    return
  
  audio_types = ['.aac', '.m4a', '.mp3', '.wma', '.mka', '.wav', '.oga', '.ogg', '.ra', '.flac', '.amr', '.opus', '.alac', '.aiff']
  
  if ft.mime_type and ft.mime_type.startswith("audio/"):
    pass
  elif (ft.file_name) and (os.path.splitext(ft.file_name)[1] in audio_types):
    pass
  else:
    await m.reply_text(text=f"Please Reply To Audio Files !\n\nSee /help", quote=True)
    logger.info(f"No Audio File !")
    return
  
  tnow = str(datetime.datetime.now())
  tnow = tnow.replace(' ','_')
  tnow = tnow.replace('-','_')
  tnow = tnow.replace(':','_')
  tnow = tnow.replace('/','_')
  tnow = tnow.replace('.','_')
  print("tnow = ", tnow)
  
  oldname = "Audio_CHATID" + str(m.chat.id) + "_DATE_" + str(tnow) + ".mp3"
  if ft.file_name:
    oldname = ft.file_name
    oldname = oldname.replace('%40','@')
    oldname = oldname.replace('%25','_')
    oldname = oldname.replace(' ','_')
  
  print("oldname = ", oldname)
  #########################
  args = u.text.split("|")
  if len(args) <= 1:
    await m.reply_text(text=f"are you kidding me ?\n\nExample:\n`/rna | filename`\n\nsee /hlep.", quote=True)
    return
  #########################
  if len(args) == 2:
    cmd, newname = u.text.split("|", 1)
    newname = newname.strip()
    if newname == "-":
      await m.reply_text(text=f"are you kidding me ?\n\nExample:\n`/rna | filename`\n\nsee /hlep.", quote=True)
      return
                  
    if m.audio and m.audio.title:
      newtitle = m.audio.title
    else:
      newtitle = None
    if m.audio and m.audio.performer:
      newartist = m.audio.performer
    else:
      newartist = None
  
  elif len(args) == 3:
    cmd, newname, newtitle = u.text.split("|", 2)
    newname = newname.strip()
    newtitle = newtitle.strip()
                  
    if newname == "-":
      if newtitle == "-":
        await m.reply_text(text=f"are you kidding me ?\n\nExample:\n`/rna | filename`\n\nsee /hlep.", quote=True)
        return  
                  
    if newname == "-":
      newname = os.path.splitext(oldname)[0]
          
    if newtitle == "-":
      if m.audio and m.audio.title:
        newtitle = m.audio.title
      else:
        newtitle = None
      if m.audio and m.audio.performer:
        newartist = m.audio.performer
      else:
        newartist = None
  
  elif len(args) == 4:
    cmd, newname, newtitle, newartist = u.text.split("|", 3)
    newname = newname.strip()
    newtitle = newtitle.strip()
    newartist = newartist.strip()
    if newname == "-":
      if newtitle == "-":
        if newartist == "-":
          await m.reply_text(text=f"are you kidding me ?\n\nExample:\n`/rna | filename`\n\nsee /hlep.", quote=True)
          return
          
    if newname == "-":
      newname = os.path.splitext(oldname)[0]
                    
    if newtitle == "-":
      if m.audio and m.audio.title:
        newtitle = m.audio.title
      else:
        newtitle = None
    
    if newartist == "-":
      if m.audio and m.audio.performer:
        newartist = m.audio.performer
      else:
        newartist = None

  else:
    await m.reply_text(text=f"Try Again !\n\nExample:\n**/rna | filename**\n**/rna | filename | title(optional) | artists(optional)**", quote=True)
    return

  if os.path.splitext(newname)[1]:
    if os.path.splitext(newname)[1] in audio_types:
      pass
    else:
      await m.reply_text(text=f"use audio extension for new name !\n\nExample:\n**/rna | filename**\n**/rna | filename | title(optional) | artists(optional)**", quote=True)
      fsw = "app"
      return
  else:
    newname = newname + os.path.splitext(oldname)[1]
    logger.info(f"newname = {newname}")
    
  #################################################################### Downloading Audio
  
  status = True
  logger.info(f"status: {status}")
  
  msg = await m.reply_text(text=f"⬇️ Trying To Download Audio", quote=True)

  c_time = time.time()
  file_path = await bot.download_media(
    m,
    file_name=oldname,
    progress=progress_for_pyrogram,
    progress_args=(
      "⬇️ Downloading Audio:",
      msg,
      c_time
    )
  )
  logger.info(f"file_path: {file_path}")
  if not file_path:
    status = False
    await msg.edit(f"❌ Downloading Audio Failed !")
    logger.info(f"status: {status}")
    await clean_up(file_path)
    return
  else:
    if m.audio and m.audio.duration:
      duration = m.audio.duration
    else:
      duration = 0
      probe = await stream_creator(file_path)
      #logger.info(probe)
      duration = int(float(probe["format"]["duration"]))
      ptlist = list(probe["format"]["tags"].keys())
      if "title" in ptlist:
        if not newtitle:
          newtitle = probe["format"]["tags"]["title"]
      if "artist" in ptlist:
        if not newartist:
          newartist = probe["format"]["tags"]["artist"]

    await msg.edit(f"⬆️ Trying to Upload as Audio ...")
      
    c_time = time.time()
    try:
      await bot.send_audio(
        chat_id=m.chat.id,
        file_name=newname,
        performer=newartist,
        title=newtitle,
        duration=duration,
        audio=file_path,
        caption=f"**File:** `{newname}`\n**Title:** `{newtitle}`\n**Artist(s):** `{newartist}`\n**Size:** {fsize}",
        reply_to_message_id=m.id,
        progress=progress_for_pyrogram,
        progress_args=(
          f"⬆️ Uploading as Audio:",
          msg,
          c_time
        )
      )
      await msg.delete()
      status = False
      logger.info(f"status: {status}")
      await clean_up(file_path)
    except Exception as e:
      status = False
      logger.info(f"status: {status}")
      await msg.edit(f"❌ Uploading as Audio Failed **Error:**\n\n{e}")
      await clean_up(file_path)
