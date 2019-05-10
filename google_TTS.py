import requests
import json
import appex
import sound
import clipboard
import webbrowser
import sound
import sys
import os
import time
import pickle
from rtime import get_text, calc_readtime, print_readtime, print_ttstime
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from appleNewsUtils import get_redirect_url

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


article_url = appex.get_url()
article_text = ''
if not article_url:
    article_text = appex.get_text()
    if not article_text:
        copied = clipboard.get()
        if not copied.startswith('http'):
            article_text = copied
            article_url = ''
            rt = calc_readtime(article_text)
        else:
            article_text = ''
            article_url = copied
            if article_url.startswith('https://apple.news'):
                article_url = get_redirect_url(article_url)
            rt = calc_readtime(get_text(article_url))
    else:
        rt = calc_readtime(article_text)
else:
    if article_url.startswith('https://apple.news'):
        article_url = get_redirect_url(article_url)
    rt = calc_readtime(get_text(article_url))
print_readtime(rt)

with open('CONFIDENTIAL', 'rb') as rb:
    api_url, userinfo = pickle.load(rb)
print(' requesting gTTS')


headers = {'Content-Type': 'application/json'}
params = {"ARTICLE_URL": article_url,
          "ARTICLE_TEXT": article_text,
          "SPEECH_SPEED": .93}

resp = requests.post(api_url,
                     headers=headers, 
                     data=json.dumps(params),
                     auth=userinfo,
                     verify=False)
resp = resp.json()
print(' start writing mp3')


i = 0
while os.path.exists(f'gTTS-output{i}.mp3'):
    i += 1

out_path = f"gTTS-output{i}.mp3"
with open(out_path, "wb") as wb:
    wb.write(bytes(resp["audio"]))
    

print(' start playing audio')
print_ttstime(sound.Player(out_path).duration)
time.sleep(.5)
webbrowser.open(f'pythonista://ReadingTools/{out_path}')

if appex.is_running_extension():
    remove = input(' remove audio? [Y/n] ')
    if (not remove) or remove.lower() == 'y':
        os.remove(out_path)
        print('  removed')
    
sys.exit(0)
