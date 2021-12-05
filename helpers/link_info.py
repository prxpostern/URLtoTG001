import requests, os, mimetypes, json
from helpers.download_from_url import get_size
from requests.exceptions import RequestException
from urllib.parse import unquote

async def linfo2(bot , m):
  
  if "|" in m.text:
    url , cfname = m.text.split("|", 1)
    url = url.strip()
    cfname = cfname.strip()
    cfname = cfname.replace('%40','@')
    mt = mimetypes.guess_type(str(cfname))[0]
  else:
    url = m.text.strip()
    if os.path.splitext(url)[1]:
      try:
        r = requests.get(url, allow_redirects=True, stream=True)
        #r.encoding = 'utf-8'
        if "Content-Disposition" in r.headers.keys():
          cfname = r.headers.get("Content-Disposition")
          cfname = cfname.split("filename=")[1]
          if '\"' in cfname:
            cfname = cfname.split("\"")[1]
        else:
          cfname = unquote(os.path.basename(url))
      except RequestException as e:
        await m.reply_text(text=f"Error:\n\n{e}", quote=True)
      
      #fname = re.findall("filename=(.+)", r.headers["Content-Disposition"])[0]
      mt = mimetypes.guess_type(str(url))[0]
    else:
      try:
        r = requests.get(url, allow_redirects=True, stream=True)
        #js = json.loads(r)
        #r.encoding = 'utf-8'
        if "Content-Disposition" in r.headers.keys():
          
          with open('file.json', "w", encoding="utf8") as f:
            json.dump(dict(r.headers), f, ensure_ascii=False)
            #f.close()
          with open('file.json', "r", encoding="utf8") as f:  
            js = json.load(f)
          

          cfname = r.headers.get("Content-Disposition")
          cfname = cfname.split("filename=")[1]
          if '\"' in cfname:
            cfname = cfname.split("\"")[1]
          #cfname = unquote(cfname)
          #mt = mimetypes.guess_type(str(cfname))[0]
        else:
          await m.reply_text(text=f"I Could not Determine The FileType !\nPlease Use Custom Filename With Extension\nSee /help", quote=True)
          return
      except RequestException as e:
        await m.reply_text(text=f"Error:\n\n{e}", quote=True)
        
  r = requests.get(url, allow_redirects=True, stream=True)
  url_size = int(r.headers.get("content-length", 0))
  url_size = get_size(url_size)

  #await m.reply_text(text=f"📋 Link Info:\n\nFile: `{cfname}`\nMime-Type: `{mt}`\nSize: `{url_size}`\n\nUse /upload as reply to your link, it will upload your link to telegram", quote=True)
  await m.reply_text(text=f"{js}", quote=True)
