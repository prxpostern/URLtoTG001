import time, os, logging
#from hachoir.parser import createParser
#from hachoir.metadata import extractMetadata
from helpers.download_from_url import get_size
from helpers.tools import clean_up
#from helpers.progress import progress_func
from helpers.display_progress import progress_for_pyrogram
from helpers.thumbnail_video import thumb_creator
from helpers.ffprobe import stream_creator

logger = logging.getLogger(__name__)

# audio uploader
async def upaudio(client, message, msg, file_loc, fname=None):
    #logger.info(message)
    #return
    #
    await msg.edit(f"✏️ Adding Metadata...")
    
    title = None
    artist = None
    thumb = None
    duration = 0
    
    probe = await stream_creator(file_loc)
    #logger.info(probe)
    duration = int(float(probe["format"]["duration"]))
    if 'tags' in probe["format"]:
        if 'tittle' in probe["format"]["tags"]:
            title = probe["format"]["tags"]["title"]
        if 'artist' in probe["format"]["tags"]:
            artist = probe["format"]["tags"]["artist"]
        
    """
    metadata = extractMetadata(createParser(file_loc))
    print(metadata)
    logger.info(metadata)
    if metadata and metadata.has("title"):
        title = metadata.get("title")
    if metadata and metadata.has("artist"):
        artist = metadata.get("artist")
    if metadata and metadata.has("duration"):
        duration = metadata.get("duration").seconds
    """
    
    if fname:
        fn = fname
    else:
        fn = os.path.basename(file_loc)
    size = os.path.getsize(file_loc)
    size = get_size(size)
    
    await msg.edit(f"⬆️ Initiating Upload ...")
    
    caption = f"**File:** `{fn}`\n**Title:** `{title}`\n**Artist(s):** `{artist}`\n**Size:** {size}"
    
    c_time = time.time()    
    try:
        await client.send_audio(
            chat_id=message.chat.id,
            audio=file_loc,
            file_name=fn,
            thumb=thumb,
            caption=caption,
            title=title,
            performer=artist,
            duration=duration,
            reply_to_message_id=message.id,
            progress=progress_for_pyrogram,
            progress_args=(
                f"⬆️ Uploading as Audio:\n\n`{fn}`",
                msg,
                c_time
            )
        )
    except Exception as e:
        print(e)
        logger.info(f"Some Error Occurred.{e}")
        await msg.edit_text("**Some Error Occurred. See Logs for More Info.**")
        time.sleep(3)
        return True

    await msg.delete()
    await clean_up(file_loc)
    return False

    
# video uploader
async def upvideo(client, message, msg, file_loc, fname=None):
    
    await msg.edit(f"🏞 Generating thumbnail ...")
    
    width = 0
    height = 0
    duration = 0
    thumbnail = None
    
    thumbnail, duration, width, height = await thumb_creator(file_loc)
    
    await msg.edit(f"⬆️ Initiating Upload ...")
    
    """
    probe = await stream_creator(file_loc)
    logger.info(probe)
    
    video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
    if video_stream and video_stream['width']:
        width = int(video_stream['width'] if 'width' in video_stream else 0)
    if video_stream and video_stream['height']:
        height = int(video_stream['height'] if 'height' in video_stream else 0)

    duration = int(float(probe["format"]["duration"]))
    """
    size = os.path.getsize(file_loc)
    size = get_size(size)
    #fn = os.path.basename(file_loc)
    if fname:
        fn = fname
    else:
        fn = os.path.basename(file_loc)

    

    c_time = time.time()    
    try:
        await client.send_video(
            chat_id=message.chat.id,
            video=file_loc,
            file_name=fn,
            thumb=str(thumbnail),
            caption=f"`{fn}` [{size}]",
            width=width,
            height=height,
            duration=duration,
            reply_to_message_id=message.id,
            progress=progress_for_pyrogram,
            progress_args=(
                f"⬆️ Uploading as Video:\n\n`{fn}`",
                msg,
                c_time
            )
        )
    except Exception as e:
        print(e)     
        logger.info(f"Some Error Occurred.{e}")
        await msg.edit_text(f"Some Error Occurred.\n\n{e}")
        time.sleep(3)
        return True

    #await msg.delete()
    await clean_up(file_loc)
    return False

# document uploader
async def upfile(client, message, msg, file_loc, fname=None):
    
    await msg.edit(f"⬆️ Initiating Upload ...")
    size = os.path.getsize(file_loc)
    size = get_size(size)
    if fname:
        fn = fname
    else:
        fn = os.path.basename(file_loc)
    c_time = time.time()
    try:
        await client.send_document(
            chat_id=message.chat.id,
            file_name=fn,
            document=file_loc,
            force_document=True,
            caption=f"`{fn}` [{size}]",
            reply_to_message_id=message.id,
            progress=progress_for_pyrogram,
            progress_args=(
                f"⬆️ Uploading as Document:\n\n`{fn}`",
                msg,
                c_time
            )
        )
    except Exception as e:
        await msg.edit(f"❌ Uploading as Document Failed !\n\n**Error:** {e}")
        print(e)     
        logger.info(f"Some Error Occurred.{e}")
        time.sleep(3)
        return True
        
    #await msg.delete()
    await clean_up(file_loc)
    return False
