# coding: utf-8

# # Article Summarizer
# # with Skip-Thoughts-TF
# 
# * [TensorFlow Github - models/research/skip-thoughts](https://github.com/tensorflow/models/tree/master/research/skip_thoughts#encoding-sentences)

# In[1]:


from __future__ import absolute_import
from __future__ import division
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, LancasterStemmer
from collections import defaultdict, Counter
from appleNewsUtils import get_redirect_url
import nltk
import numpy as np
import os.path

import appex
import clipboard


# In[2]:


contractions = {
    "ain't": "am not",
    "aren't": "are not",
    "can't": "cannot",
    "can't've": "cannot have",
    "'cause": "because",
    "could've": "could have",
    "couldn't": "could not",
    "couldn't've": "could not have",
    "didn't": "did not",
    "doesn't": "does not",
    "don't": "do not",
    "hadn't": "had not",
    "hadn't've": "had not have",
    "hasn't": "has not",
    "haven't": "have not",
    "he'd": "he would",
    "he'd've": "he would have"
}
punctuations = {
    "â€™": "'",
    "â€œ": '"',
    "â€˜": "'",
    "â€": '"',
    "â€”": "-"
}

replace_dict = contractions.copy()
replace_dict.update(punctuations)


# In[3]:


def replace_abnormals(text):
    """
    Remove or replace pretty quotes and contractions.
    """
    for to_be_replaced, replacement in replace_dict.items():
        text = text.replace(to_be_replaced, replacement)
        text = text.replace(to_be_replaced.capitalize(), replacement)
    return text


# In[4]:


def preprocess(article):
    """
    INPUT
        articles: list of article texts.
    
    Performs preprocessing operations such as:
        1. Remove or replace pretty quotes and contractions.
        2. Remove new line characters.
    """
    article = replace_abnormals(article)
    lines = article.split('\n')
    for j in reversed(range(len(lines))):
        lines[j] = lines[j].strip()
        if lines[j] == '':
            lines.pop(j)
    return article


# In[5]:


def split_sentences(article):
    """
    Splits the article into individual sentences
    """
    sentences = sent_tokenize(article)
    sentences = [s for sent in sentences for s in sent.split("\n")]
    for j in reversed(range(len(sentences))):
        sent = sentences[j]
        sentences[j] = sent.strip()
        if sent == '':
            sentences.pop(j)

    return sentences  # list of sentences


# In[6]:


def score_words(article):
    # tokenize words
    tokenized_words = word_tokenize(preprocess(article))
    
    stop_words = stopwords.words('english')
    stop_words += ["ms.", "mr.", "'s"]#, "said"]
    punctuations = ["?", "!", ",", ".", ":", ";", "\"", "'", "''", "``"]

    tokenized_words = [w.lower() for w in tokenized_words if w.lower() not in stop_words]
    tokenized_words = [w for w in tokenized_words if w not in punctuations]
    
    # lemmatize words
    lemmatizer = nltk.wordnet.WordNetLemmatizer()
    tokenized_words = [lemmatizer.lemmatize(w.lower()) for w in tokenized_words]
    #print(tokenized_words)
    # stem words with PorterStemmer
    porter = PorterStemmer()
    tokenized_words = [porter.stem(w) for w in tokenized_words]
    
    scores = Counter(tokenized_words)
    return scores


# In[7]:


def score_sentences(sentences, scores, length_penalty):
    """
    INPUT
        sentences: list of sentences, from split_sentences()
        scores: word scores dict, from score_words()
        length_penalty: larger the value, more penalties given to lengthy sentences when scoring
    """
    # use top 50 words to score sentences
    top50 = scores.most_common()[:50]
    sentence_scores = []
    for sentence in sentences:
        score = 0
        for word, word_score in top50:
            score += sentence.lower().count(word) * word_score
        sentence_scores.append(score/len(sentence)**length_penalty)
    return sentence_scores


# In[8]:


def index_sentence_scores(sentence_scores):
    """
    https://stackoverflow.com/questions/7851077/how-to-return-index-of-a-sorted-list
    """
    return sorted(range(len(sentence_scores)), key=lambda k: sentence_scores[k], reverse=True)


# In[9]:


def summarize(article, n_sentences=None, length_penalty=0.33):
    """
    generate summary of the input article.
    """
    article = preprocess(article)
    sentences = split_sentences(preprocess(article))
    
    if n_sentences is None:
        n_sentences = round(len(sentences) **0.6)
    
    if n_sentences > len(sentences):
        raise ValueError("n_sentences should be smaller than the article length.")
    
    word_scores = score_words(article)
    sent_scores = score_sentences(sentences, word_scores, length_penalty=length_penalty)
    # get sorted indices of top-15 sentences.
    sorted_idx = index_sentence_scores(sent_scores)[:n_sentences]
    
    # re-sort indices back to chronological order.
    sorted_idx.sort()
    summary = [sentences[idx] for idx in sorted_idx]
    
    # clean summary texts
    if summary[0].startswith("But"):
        summary[0] = summary[0].replace("But", "")[1:].strip().capitalize()
    
    print ("=" * 35)
    print ("="*14 + f"{n_sentences} LINES" +"="*14 + "\n")
    
    summary_text = "\n\n".join(summary)
    print (summary_text + "\n")
    
    print ("=" * 35)
    
    return summary_text


# ## Test on an article
# * [Two Infants Treated with Universal Immune Cells Have Their Cancer Vanish - MIT Technology Reviews](https://www.technologyreview.com/s/603502/two-infants-treated-with-universal-immune-cells-have-their-cancer-vanish/)

# In[10]:

text = appex.get_text()
if text is None:
    text = clipboard.get()
if len(text) < 100:
    url = appex.get_url()
    if url is None:
        url = clipboard.get()
    if len(url) < 5:
        exit()
        
    from bs4 import BeautifulSoup
    import requests
    
    if url.startswith('https://apple.news'):
        url = get_redirect_url(url)
    response = requests.get(url, allow_redirects=True)
    soup = BeautifulSoup(response.content, 'html5lib')
    text = ' '.join(map(lambda p: p.text, soup.find_all('p')))



"""Doctors in London say they have cured two babies of leukemia in the worldâ€™s first attempt to treat cancer with genetically engineered immune cells from a donor.

The experiments, which took place at Londonâ€™s Great Ormond Street Hospital, raise the possibility of off-the-shelf cellular therapy using inexpensive supplies of universal cells that could be dripped into patients' veins on a momentâ€™s notice.

The ready-made approach could pose a challenge to companies including Juno Therapeutics and Novartis, each of which has spent tens of millions of dollars pioneering treatments that require collecting a patientâ€™s own blood cells, engineering them, and then re-infusing them.

Both methods rely on engineering T cells-the hungry predator cells of the immune system-so they attack leukemic cells.

The British infants, ages 11 and 16 months, each had leukemia and had undergone previous treatments that failed, according to a description of their cases published Wednesday in Science Translational Medicine. Waseem Qasim, a physician and gene-therapy expert who led the tests, reported that both children remain in remission.

Although the cases drew wide media attention in Britain, some researchers said that because the London team also gave the children standard chemotherapy, they failed to show the cell treatment actually cured the kids. â€œThere is a hint of efficacy but no proof,â€ says Stephan Grupp, director of cancer immunotherapy at the Childrenâ€™s Hospital of Philadelphia, who collaborates with Novartis. â€œIt would be great if it works, but that just hasnâ€™t been shown yet.â€

Rights to the London treatment, developed by the biotech company Cellectis, were recently sold and it is now being further developed by the drug companies Servier and Pfizer.

Treatments using engineered T-cells, commonly known as CAR-T, are new and not yet sold commercially. But they have shown stunning success against blood cancers. In studies so far by Novartis and Juno, about half of patients are permanently cured after receiving altered versions of their own blood cells.

But commercializing such personalized treatments raises unprecedented logistical headaches. Grupp says Novartis has outfitted a manufacturing center in New Jersey and that patient cells have been flown in from 25 hospitals in 11 countries, modified, then quickly shipped back. Novartis has said it will seek U.S. approval to sell its T-cell treatment for children this year.

The promise of immunotherapy has drawn huge investments, yet many newer entrants are betting instead on the off-the-shelf approach. Among them are biotech giant Regeneron, Kite Therapeutics, Fate Therapeutics, and Cell Medica.  

â€œThe patient could be treated immediately, as opposed to taking cells from a patient and manufacturing them,â€ says Julianne Smith, vice president of CAR-T development for Cellectis, which specializes in supplying universal cells.  

In the off-the-shelf approach, blood is collected from a donor and then turned into â€œhundredsâ€ of doses that can then be stored frozen, says Smith. â€œWe estimate the cost to manufacture a dose would be about $4,000,â€ she says. That's compared to a cost of around $50,000 to alter a patient's cells and return them.

Either type of treatment is likely to cost insurers half a million dollars or more if they reach the market.

Robert Nelsen, a venture capitalist and a founder of Juno Therapeutics, which raised hundreds of millions for the custom approach, says heâ€™s not worried about companies developing universal alternatives. â€œWhat they can do in the future is what we can do today,â€ Nelsen said in an interview last year. â€œAnd I guarantee you even if things were equal, which they are not, you would want your own stuff, not someone elseâ€™s cells.â€

The London treatment is notable for involving the most extensively engineered cells ever given to a patient, with a total of four genetic changes, two of them introduced by gene editing using a method called TALENs. One alteration was to strip the donor cells of their propensity to attack the body of another person. Another directs them to attack cancer cells.

In the U.S. and China, scientists are also racing to apply gene editing to make improved treatments for cancer and other diseases."""


# In[18]:

rephrase = None
while True:
    summary = summarize(text, rephrase)
    
    #clipboard.set(summary)
    #print('(copied to clipboard.)')
    
    rephrase = int(input("rephrase with how many sentences?: "))

# ---
# 
# # TODO: URL input

# In[12]:


'''
from bs4 import BeautifulSoup
import requests


# In[13]:


response = requests.get("https://www.nytimes.com/2019/04/04/us/fake-uber-driver-assaults.html")


# In[14]:


soup = BeautifulSoup(response.text, "html5lib")
text = ' '.join(map(lambda p: p.text, soup.find_all('p'))).encode("utf-8")
text


# In[19]:


summarize(text);
'''
