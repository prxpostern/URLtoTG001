# GOAL:
# getting track for logging

import logging

LOGGER = logging.getLogger(__name__)

# GOAL:
# create video thumbnail maker handler class

from os import path as os_path, rename as os_rename, remove as os_remove
import asyncio
from helpers.ffprobe import stream_creator

async def thumb_creator(filepath):
    if not os_path.exists(filepath):
        LOGGER.error('File not found : ' + filepath)
        return False

    probe = await stream_creator(filepath)
    video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
    dur = int(float(probe["format"]["duration"]))
    if video_stream and video_stream['width']:
        wid = int(video_stream['width'] if 'width' in video_stream else 0)
    if video_stream and video_stream['height']:
        hei = int(video_stream['height'] if 'height' in video_stream else 0)

    try:
        duration = float(video_stream["duration"]) // 2
    except:
        duration = 0

    out_file = filepath + ".jpg"
    
    cmd = [
        "ffmpeg",
        "-hide_banner",
        '-ss',
        str(duration),
        "-i",
        filepath,
        '-vframes',
        '1',
        '-vf',
        'scale=320:-1',
        '-y',
        out_file
    ]
    LOGGER.debug(cmd)

    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    await process.communicate()
    
    if not os_path.exists(out_file):
        LOGGER.error('No Thumb !')
        return False

    LOGGER.debug('Thumbnail : ' + out_file)
    return out_file, dur, wid, hei

######################################################################
async def set(filepath):
    if not os_path.exists(filepath):
        LOGGER.error('File not found : ' + filepath)
        return False

    prepare_path = filepath + '.prep'
    os_rename(filepath, prepare_path)
    
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-i",
        prepare_path,
        '-vf',
        'scale=320:-1',
        '-y',
        filepath
    ]
    LOGGER.debug(cmd)

    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    await process.communicate()
    os_remove(prepare_path)
    LOGGER.debug('Set thumbnail : ' + filepath)
    return True

async def reset(filepath):
    if not os_path.exists(filepath):
        LOGGER.error('File not found : ' + filepath)
        return True
        
    os_remove(filepath)
    return True
