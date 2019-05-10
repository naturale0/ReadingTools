from bs4 import BeautifulSoup
import requests
import appex
import clipboard



def calc_readtime(text, wpm=150):
    words = split_words(text)
    word_counts = len(words)
    return word_counts / wpm
    

def split_words(text):
    for ws in ('\n', '\t'):
        text = text.replace(ws, ' ')
    for q in ('"', "'", ','):
        text = text.replace(q, '')
    return text.split(' ')


def print_readtime(read_time):
    min = read_time // 1
    sec = (read_time % 1) * 60
    
    rtstr = f' * Approx. {min: .0f} min {sec: .0f} sec'
    print(rtstr)
    return rtstr

def print_ttstime(duration):
    min = duration // 60
    sec = duration % 60
    
    rtstr = f' * Actual. {min: .0f} min {sec: .0f} sec'
    print(rtstr)
    return rtstr

def get_text(url):
    soup = BeautifulSoup(requests.get(url).text, 'html5lib')
    paragraphs = soup.find_all('p')
    text = ' '.join(list(map(p2text, paragraphs)))
    return text

def p2text(p):
    return p.text


if __name__ == '__main__':
    url = appex.get_url()
    print(' please wait..')
    
    if url is None:
        text = clipboard.get()
    else:
        text = get_text(url) 
    rt = calc_readtime(text)
    print_readtime(rt)
