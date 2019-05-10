import requests
import json
import os
import sys
import time
import pickle
import appex
import webbrowser
from TextTime import *
from AppleNewsUtils import *
from Utils import *
from Summarize import summarize
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def prepare_payloads(text, speed=1.1):
    with open('CONFIDENTIAL', 'rb') as rb:
        api_url, userinfo = pickle.load(rb)
    headers = {'Content-Type': 'application/json'}
    params = {#"ARTICLE_URL": article_url,
              "ARTICLE_TEXT": text,
              "SPEECH_SPEED": speed}
    return [api_url, userinfo, headers, params]


def request_gTTS(api_url, userinfo, headers, params):
    print(' requesting gTTS')
    resp = requests.post(api_url,
                         headers=headers, 
                         data=json.dumps(params),
                         auth=userinfo,
                         verify=False)
    resp = resp.json()
    return resp


def write_mp3(resp, fname='gTTS-output'):
    print(' start writing mp3')
    i = 0
    while os.path.exists(f'{fname}{i}.mp3'):
        i += 1
    
    out_path = f"{fname}{i}.mp3"
    with open(out_path, "wb") as wb:
        wb.write(bytes(resp["audio"]))
    return out_path
    

def main(summary=False):
    text = get_safe_text().replace('—', ', ')
    if summary & appex.is_running_extension():
        print(' handing over to the main app')
        time.sleep(.5)
        
        clipboard.set(text)
        webbrowser.open(f'pythonista://ReadingTools/google_TTS.py?action=run&argv=1')
        return
    
    if summary:
        text = summarize(text, print_summary=True)
        fname = 'summary'
    else:
        fname = 'gTTS-output'
    
    rt = calc_readtime(text)
    print_readtime(rt)
    
    payloads = prepare_payloads(text)
    resp = request_gTTS(*payloads)
    out_path = write_mp3(resp, fname=fname)
    
    print_ttstime(out_path)
    time.sleep(.5)
    webbrowser.open(f'pythonista://ReadingTools/{out_path}')
    
    if appex.is_running_extension():
        remove = input(' remove audio? [Y/n] ')
        if (not remove) or remove.lower() == 'y':
            os.remove(out_path)
            print('  removed')


if __name__ == '__main__':
    if len(sys.argv) > 1:
        main(int(sys.argv[1]))
    else:
        main(0)
