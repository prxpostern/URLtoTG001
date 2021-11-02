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

async def rnf2(bot , u):
  
  if not u.reply_to_message:
    await u.reply_text(text=f"Reply To Your Document !\n\nExample:\n**/rnf | filename.ext**")
    return
  
  m = u.reply_to_message
  
  if m.video:
    await u.reply_text(text=f"MimeType: {m.video.mime_type}\n\nUse `/rnv` to rename a video file.\nUse `/c2v` for converting a document to video.\nSee /help")
    return
  elif m.audio:
    await u.reply_text(text=f"MimeType: {m.audio.mime_type}\n\nUse `/rna` to rename an audio file.\nSee /help")
    return
  elif m.document:
    ft = m.document
  else:
    await u.reply_text(text=f"Wrong Filetype !\n\nSee /help")
    return

  fsize = get_size(ft.file_size)
  
  if not "|" in u.text:
    await m.reply_text(text=f"Please Type New Filename with extension !\n\nExample:\n**/rnf | filename.ext**")
    return
  else:
    args = u.text.split("|")
    if len(args) == 2:
      cmd , newname = u.text.split("|", 1)
      newname = newname.strip()
      if not os.path.splitext(newname)[1]:
        await m.reply_text(text=f"Type Extension !\n\nExample:\n**/rnf | filename.ext**")
        return
      else:
        ext = os.path.splitext(newname)[1]
        tempname = "File_CHATID" + str(m.chat.id) + "_DATE" + str(m.date) + str(ext)
        if ft.file_name:
            oldname = ft.file_name
            oldname = oldname.replace('%40','@')
            oldname = oldname.replace('%25','_')
            oldname = oldname.replace(' ','_')
        else:
            oldname = "File_CHATID" + str(m.chat.id) + "_DATE" + str(m.date) + str(ext)
        msg = await m.reply_text(text=f"⬇️ Trying To Download Document")
        c_time = time.time()
        file_path = await bot.download_media(
          m,
          file_name=tempname,
          progress=progress_for_pyrogram,
          progress_args=(
            "⬇️ Downloading Document:",
            msg,
            c_time
          )
        )
        if not file_path:
          await msg.edit(f"❌ Downloading Document Failed !")
          try:
            os.remove(file_path)
          except:
            pass
          return
        try:
          await msg.edit(f"⬆️ Trying to Upload as Document ...")
          c_time = time.time()
          await bot.send_document(
            chat_id=m.chat.id,
            file_name=newname,
            document=file_path,
            caption=f"`{newname}` [{fsize}]",
            reply_to_message_id=m.message_id,
            progress=progress_for_pyrogram,
            progress_args=(
              "⬆️ Uploading as Document:",
              msg,
              c_time
            )
          )
          await msg.delete()
          try:
            os.remove(file_path)
          except:
            pass
        except Exception as e:
          await msg.edit(f"❌ Uploading as Document Failed **Error:**\n\n{e}")
          try:
            os.remove(file_path)
          except:
            pass
    else:
      await m.reply_text(text=f"Try Again !\n\nExample:\n**/rnf | filename.ext**")
      return
