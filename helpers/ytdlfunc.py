from __future__ import unicode_literals

import asyncio
import functools
import logging
from concurrent.futures import ThreadPoolExecutor

from pyrogram.types import InlineKeyboardButton
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError

#from ytdlbot import Config
#from ytdlbot.helper_utils.util import humanbytes
from helpers.display_progress import humanbytes

logger = logging.getLogger(__name__)


# https://stackoverflow.com/a/64506715
def run_in_executor(_func):
    @functools.wraps(_func)
    async def wrapped(*args, **kwargs):
        loop = asyncio.get_event_loop()
        func = functools.partial(_func, *args, **kwargs)
        return await loop.run_in_executor(executor=ThreadPoolExecutor(), func=func)

    return wrapped


# extract Youtube info
async def extract_formats(yturl):
    buttons = []
    info = await yt_extract_info(
        video_url=yturl,
        download=False,
        ytdl_opts={"extractor_args": {"youtube": {"skip": ["dash", "hls"]}}},
    )
    
    for listed in info.get("formats"):
        if listed.get("acodec") == "none":
            continue
        media_type = "Audio" if "audio" in listed.get("format") else "Video"
        
        if "audio" in listed.get("format"):
            first = str(listed.get("format_id")) + " - Audio"
        else:
            first = listed.get("format")
        
        #format_note = listed.get("format_note", "format")
        format_note = listed.get("ext")
        # SpEcHiDe/AnyDLBot/anydlbot/plugins/youtube_dl_echo.py#L112
        
        if listed.get("filesize"):
            filesize = humanbytes(listed.get("filesize"))
        elif listed.get("filesize_approx"):
            filesize = humanbytes(listed.get("filesize_approx"))
        else:
            filesize = "null"
        
        acodec = listed.get("acodec")
        av_codec = "empty"
        if listed.get("acodec") == "none" or listed.get("vcodec") == "none":
            av_codec = "none"
        buttons.append(
            [
                InlineKeyboardButton(
                    f"{first} [{format_note}] [{filesize}] {acodec}",
                    f"{media_type}_{listed['format_id']}_{av_codec}_{info['id']}",
                )
            ]
        )

    return info.get("id"), info.get("thumbnail"), info.get("title"), buttons
    
    """template = make_template(
        info.get("title"), info.get("duration"), info.get("upload_date")
    ) 
    for listed in info.get("formats"):
        media_type = "Audio" if "audio" in listed.get("format") else "Video"
        format_note = listed.get("format_note", "format")
        # SpEcHiDe/AnyDLBot/anydlbot/plugins/youtube_dl_echo.py#L112
        filesize = (
            humanbytes(listed.get("filesize")) if listed.get("filesize") else "(best)"
        )
        av_codec = "empty"
        if listed.get("acodec") == "none" or listed.get("vcodec") == "none":
            av_codec = "none"
        buttons.append(
            [
                InlineKeyboardButton(
                    f"{media_type} {format_note} [{listed['ext']}] {filesize}",
                    f"{media_type}_{listed['format_id']}_{av_codec}_{info['id']}",
                )
            ]
        )

    return info.get("id"), info.get("thumbnail"), info.get("title"), buttons
    """

# The codes below were referenced after
# https://github.com/eyaadh/megadlbot_oss/blob/master/mega/helpers/ytdl.py
# https://stackoverflow.com/questions/33836593
async def yt_download(video_id, media_type, av_codec, format_id, output):
    ytdl_opts = {
        "outtmpl": f"{output}/%(title)s_[%(id)s].%(ext)s",
        "ignoreerrors": True,
        "nooverwrites": True,
        "continuedl": True,
        # "noplaylist": True,
        #"max_filesize": Config.MAX_SIZE,
        "max_filesize": 9 * 1024 * 1024 * 1024,
        "restrictfilenames": True,
        "trim_file_name": 50,
    }
    if media_type == "Audio":
        ytdl_opts.update(
            {
                "format": "bestaudio/best",
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": format_id,
                    },
                    {"key": "FFmpegMetadata"},
                ],
            }
        )
    elif media_type == "Video":
        # Special condition, refer 20b0ef4
        if av_codec == "none":
            format_id = f"{format_id}+bestaudio"
        ytdl_opts.update(
            {
                "format": f"{format_id}",
                "postprocessors": [{"key": "FFmpegMetadata"}],
            }
        )
    logger.info(ytdl_opts)
    try:
        info = await yt_extract_info(
            video_url=video_id, download=True, ytdl_opts=ytdl_opts
        )
        return True, info.get("title", "")
    except DownloadError as error_msg:
        return False, error_msg


@run_in_executor
def yt_extract_info(video_url, download, ytdl_opts):
    with YoutubeDL(ytdl_opts) as ytdl:
        info = ytdl.extract_info(video_url, download=download, ie_key="Youtube")
    return info
