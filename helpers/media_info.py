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

async def cinfo2(bot , m):
   
   if m.photo:
      fsize = get_size(m.photo.file_size)
      await m.reply_text(text=f"**Media Info**:\n\n**Size**: {fsize}\n**Width:** {m.photo.width}\n**height:** {m.photo.height}\n\nSee /help.", quote=True)
      return
   ft = m.audio or m.video or m.document
   fsize = get_size(ft.file_size)
   if ft.mime_type and ft.mime_type.startswith("audio/"):
      if ft.file_name:
         fn = str(ft.file_name)
      else:
         fn = "No File Name Detected!"
      if m.document:
         await m.reply_text(text=f"**Media Info**:\n\n**MimeType**: {ft.mime_type}\n**Filename**: `{fn}`\n**Size**: {fsize}\n\n**You Can Use** /rna **to rename and edit audio tags.**\n\nSee /help.", quote=True)
         return
      if m.audio.title:
         tt = str(ft.title)
      else:
         tt = "No Title Detected!"
      if m.audio.performer:
         pf = str(ft.performer)
      else:
         pf = "No artist(s) Detected!"
      await m.reply_text(text=f"**Media Info**:\n\n**MimeType**: {ft.mime_type}\n**Filename**: `{fn}`\n**Title**: `{tt}`\n**Artist**: `{pf}`\n**Size**: {fsize}\n\n**You Can Use** /rna **to rename and edit audio tags.**\n\nSee /help.", quote=True)
   elif ft.mime_type and ft.mime_type.startswith("video/"):
      if ft.file_name:
         fn = str(ft.file_name)
      else:
         fn = "No File Name Detected!"
      await m.reply_text(text=f"**Media Info**:\n\n**MimeType**: {ft.mime_type}\n**Filename**: `{fn}`\n**Size**: {fsize}\n\n**You Can Use** /c2v **to convert or** /rnv **to rename this video.**\n\nSee /help.", quote=True)
   else:
      if ft.file_name:
         fn = str(ft.file_name)
      else:
         fn = "No File Name Detected!"
      await m.reply_text(text=f"**Media Info**:\n\n**MimeType**: {ft.mime_type}\n**Filename**: `{fn}`\n**Size**: {fsize}\n\n**You Can Use** /rnf **to rename this file.**\n\nSee /help.", quote=True)
