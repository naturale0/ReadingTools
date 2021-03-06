import platform
import appex
import clipboard
import os
import re
import requests
from AppleNewsUtils import *


def is_ios():
    return platform.machine().startswith('iP')


def p2text(p):
    return p.text

def get_text(url):
    soup = BeautifulSoup(requests.get(url).text, 'html5lib')
    paragraphs = soup.find_all('p')
    text = ' '.join(list(map(p2text, paragraphs)))
    return text


def get_safe_text():
    url_ext = appex.get_url()
    url_clp = clipboard.get()
    txt_ext = appex.get_text()
    
    if url_ext:
        if check_anews(url_ext):
            url = redirect_anews(url_ext)
            return get_text(url)
        else:
            return get_text(url_ext)
    elif txt_ext:
        return txt_ext
    elif url_clp:
        if url_clp.startswith('http'):
            if check_anews(url_clp):
                url = redirect_anews(url_clp)
                return get_text(url)
            else:
                return get_text(url_clp)
        else:
            return url_clp
    else:
        raise ValueError('no text or url received from app extension or clipboard')
    
    
def get_script_path():
    pwd = os.path.normpath(os.getcwd())
    paths = pwd.split(os.sep)
    st = paths.index("Documents")
    path = os.path.join(*paths[st+1:])
    return path
