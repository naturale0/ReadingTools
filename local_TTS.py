from Utils import *
from objc_util import *
from AppleNewsUtils import *
import random


def speak_(text, voice_idxs):
    AVSpeechUtterance = ObjCClass('AVSpeechUtterance')
    AVSpeechSynthesizer = ObjCClass('AVSpeechSynthesizer')
    AVSpeechSynthesisVoice = ObjCClass('AVSpeechSynthesisVoice')
    
    voices = AVSpeechSynthesisVoice.speechVoices()
    
    chosen = random.choice(voice_idxs)
    voice = voices[chosen]
    synthesizer = AVSpeechSynthesizer.new()
    utterance=AVSpeechUtterance.speechUtteranceWithString_(text)
    
    utterance.rate = 0.45
    utterance.voice = voice
    utterance.useCompactVoice = False 
    synthesizer.speakUtterance_(utterance)
    

def select_voices():
    AVSpeechSynthesisVoice = ObjCClass('AVSpeechSynthesisVoice')
    
    idxs = []
    voices = AVSpeechSynthesisVoice.speechVoices()
    for i in range(len(voices)):
        if ('siri' in str(voices[i].description())) and ('en-US' in str(voices[i].description())):
            idxs.append(i)
            
    return idxs
    

if __name__ == '__main__':
    text = get_safe_text()
    text.replace('\n', '.\n')
    
    voices = select_voices()
    speak_(text, voices)
    
    
    
