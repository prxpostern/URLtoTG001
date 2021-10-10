from telethon import TelegramClient, events, Button
from download_from_url import download_file, get_size
from file_handler import send_to_transfersh_async, progress
import os
import time
import datetime
import aiohttp
import asyncio
from tools import execute

api_id = int(os.environ.get("API_ID"))
api_hash = os.environ.get("API_HASH")
bot_token =os.environ.get("BOT_TOKEN")
                          
download_path = "Downloads/"

bot = TelegramClient('Encoder bot', api_id, api_hash).start(bot_token=bot_token)

HELP_TXT = """
I am a FFmpeg robot. I can convert All Type of Media.
for using me, you have to know about ffmpeg options.

the source and destination name must be deferent.
press /encode to start the proccess. then send your
media file or direct link. type your extension with ".".
`.mkv`
`_360p.mp4`
`_new.aac`
`2.mp3`.
and finaly type your ffmpeg options.

Examples:
Extract Audio without encoding:
`-vn -sn -c:a copy`

Extract Video without encoding:
`-sn -an -c:v copy`

mp3 bitrate 256k:
`-c:a libmp3lame -ab 256k`

trimm video - from minute 10 to minute 20:
`-ss 00:10:00 -to 00:20:00 -c copy`

mp4 + aac resolution 720*576
`-c:v libx264 -s 720*576 -c:a aac -ab 64k`
"""

@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    """Send a message when the command /start is issued."""
    await event.respond(f"Hi! see /help \n\n Send /encode . Follow the Steps")
    raise events.StopPropagation
    
@bot.on(events.NewMessage(pattern='/help'))
async def help(event):
    """Send a message when the command /help is issued."""
    await event.respond(f"{HELP_TXT}")
    raise events.StopPropagation    

@bot.on(events.NewMessage(pattern='/encode'))
async def echo(update):
    """Echo the user message."""
    msg1 = await update.respond(f"**Step1:** Send Your Media File or URL. \n\n To Cancel press /cancel")
    async with bot.conversation(update.message.chat_id) as cv:
        update2 = await cv.wait_event(events.NewMessage(update.message.chat_id))
        
    if update2.text == "/cancel":
      await msg1.delete()
      await update.respond(f"Operation Cancelled By User. \n Send /encode to start again!")
      return
    await msg1.delete()
    msg2 = await update.respond("Downloading...")
    try:
        """Downloading Section."""
        if not os.path.isdir(download_path):
            os.mkdir(download_path)
            
        start = time.time()
        if not update2.message.message.startswith("/") and not update2.message.message.startswith("http") and update2.message.media:
            await msg2.edit("**Downloading starting😉...**")
            file_path = await bot.download_media(update2.message, download_path, progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                progress(d, t, msg2, start)))
        else:
            url = update2.text
            filename = os.path.join(download_path, os.path.basename(url))
            file_path = await download_file(update2.text, filename, msg2, start, bot)
            
        print(f"file downloaded to {file_path}")
        
        """ User Input Section """
        await msg2.edit(f"Successfully Downloaded to : `{file_path}`")
        msg3 = await update2.reply("**Step2:** Enter The Extension : \n Examples: \n `_.mkv` \n `_320p.mp4` \n `new.mp3` \n `32k.aac` \n `_.mka` \n\n To Cancel press /cancel")
        async with bot.conversation(update.message.chat_id) as cv:
          ext1 = await cv.wait_event(events.NewMessage(update.message.chat_id))
        if ext1.text == "/cancel":
          await msg2.delete()
          await msg3.delete()
          os.remove(file_path)
          await update.respond(f"Operation Cancelled By User. \n Send /encode to start again!")
          return
        await msg2.delete()
        await msg3.delete()
        msg4 = await ext1.reply(
              f"**Step3:** Enter FFmpeg Options: \n\n `-sn -vn -c:a copy` \n\n `-ar 48000 -ab 256k -f mp3` \n\n `-c:s copy -c:a copy -c:v libx264` \n\n `-c:v libx264 -s 320*240 -c:a libmp3lame -ar 48000 -ab 64k -f mp4` \n\n To Cancel press /cancel"
        )
        async with bot.conversation(update.message.chat_id) as cv:
          ffcmd1 = await cv.wait_event(events.NewMessage(update.message.chat_id))
          if ffcmd1.text == "/cancel":
            await msg4.delete()
            os.remove(file_path)
            await update.respond(f"Operation Cancelled By User. \n Send /encode to start again!")
            return
        await msg4.delete()  
            
        """ Encoding Section """
        ext2 = ext1.text
        ffcmd2 = ffcmd1.text
        ponlyname = os.path.splitext(file_path)[0]
        file_loc2 = f"{ponlyname}{ext2}"
        name = os.path.basename(file_loc2)
        ffcmd4 = f"ffmpeg -i {file_path} {ffcmd2} {file_loc2} -y"
        msg5 = await ffcmd1.reply(f"`{ffcmd4}` \n\n Encoding ... \n\n **plz wait😍...**")
        await asyncio.sleep(1)
        
        out, err, rcode, pid = await execute(f"{ffcmd4}")
        if rcode != 0:
          await msg5.edit("**FFmpeg: Error Occured. See Logs for more info.**")
          os.remove(file_path)
          os.remove(file_loc2)
          print("Deleted file :", file_path)
          print("Deleted file :", file_loc2)
          print(err)
          return
        
        size = os.path.getsize(file_loc2)
        size_of_file = get_size(size)
        
        """Uploading Section."""
        await msg5.edit(f"Uploading to Telegram ... \n\n **Name: **`{name}`")
        try:
          await bot.send_file(
            update.message.chat_id,
            file=file_loc2,
            caption=f"`{name}` \n\n **Size:** `{size_of_file}`",
            reply_to=update2.message,
            force_document=True,
            supports_streaming=False
          )
        except Exception as e:
          print(e)
          await update.respond(f"Uploading Failed\n\n**Error:** {e}")
        
        await msg5.delete()
        msg6 = await update.respond(f"Uploading to transfer.sh... \n\n **Name: ** `{name}`")
        try:
            download_link, final_date, size = await send_to_transfersh_async(file_loc2, msg5)
            await msg6.edit(f"Successfully Uploaded to Transfer.sh! \n\n **Name: ** `{name}` \n\n **Size:** `{size}` \n\n **Link:** \n {download_link} \n **ExpireDate:** {final_date}")
        except Exception as e:
            print(e)
            await update.respond(f"Uploading to transfer.sh Failed \n\n **Error:** {e}")  
        finally:
           """ Cleaning Section """
           #await msg5.delete()
           await update.respond(f"Send /encode to start new Encoding")
           os.remove(file_path)
           os.remove(file_loc2)
           print("Deleted file :", file_path)
           print("Deleted file :", file_loc2)
    except Exception as e:
        print(e)
        await update.respond(f"Download link is invalid or not accessible ! \n\n **Error:** {e}")

def main():
    """Start the bot."""
    print("\nBot started ...\n")
    bot.run_until_disconnected()

if __name__ == '__main__':
    main()
