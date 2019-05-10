from AppleNewsUtils import *
from Utils import *


def calc_readtime(text, wpm=160):
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


if __name__ == '__main__':
    print(' please wait..')
    text = get_safe_text()
    
    rt = calc_readtime(text)
    print_readtime(rt)
