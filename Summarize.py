from nltk import wordnet
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from collections import Counter
from AppleNewsUtils import *
from Utils import *
import sys
import appex
import clipboard
import webbrowser


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
    "’": "'",
    "“": '"',
    "‘": "'",
    "”": '"',
    "—": "-",
    "…": "."
}

replace_dict = contractions.copy()
replace_dict.update(punctuations)


def replace_abnormals(text):
    """
    Remove or replace pretty quotes and contractions.
    """
    for to_be_replaced, replacement in replace_dict.items():
        text = text.replace(to_be_replaced, replacement)
        text = text.replace(to_be_replaced.capitalize(), replacement)
    return text


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


stop_words = stopwords.words('english')
stop_words += ["ms.", "mr.", "'s"]
punctuations = ["?", "!", ",", ".", ":", ";", "\"", "'", "''", "``", "-", "(", ")"]
unimportant = ['said', 'says', 'day', 'may', '©', 'whether', '%', 'n\'t']
pass_words = stop_words + punctuations + unimportant

def token_lemma_stem(text):
    # 1. tokenize words
    tokenized_words = word_tokenize(preprocess(text))

    tokenized_words = [w.lower() for w in tokenized_words if w.lower() not in pass_words]
    
    # 2. lemmatize words
    lemmatizer = wordnet.WordNetLemmatizer()
    tokenized_words = [lemmatizer.lemmatize(w.lower()) for w in tokenized_words]
    
    # 3. stem words with PorterStemmer
    porter = PorterStemmer()
    tokenized_words = [porter.stem(w) for w in tokenized_words]
    return tokenized_words


def score_words(article):
    tokenized_words = token_lemma_stem(article)
    
    scores = Counter(tokenized_words)
    return scores


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
        sentence = ' '.join(token_lemma_stem(sentence))
        score = 0
        for word, word_score in top50:
            score += sentence.lower().count(word) * word_score
        sentence_scores.append(score/len(sentence)**length_penalty)
    return sentence_scores


def index_sentence_scores(sentence_scores):
    """
    https://stackoverflow.com/questions/7851077/how-to-return-index-of-a-sorted-list
    """
    return sorted(range(len(sentence_scores)), key=lambda k: sentence_scores[k], reverse=True)


def summarize(article, n_sentences=None, length_penalty=0, print_summary=True):
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
    starters = ('But', 'So')
    for s in starters:
        if summary[0].startswith(s):
            summary[0] = summary[0].replace(s, "")[1:].lstrip(',').strip().capitalize()
    
    # select keywords to report
    keywords = word_scores.most_common()[:10]
    keywords = ', '.join([i[0] for i in keywords])
    
    # combine into one big string
    summary_text = "\n\n".join(summary)
    summary_text += f"\n\n\n [KEYWORDS] {keywords}"
    if print_summary:
        print ("=" * 35)
        print ("="*14 + f"{n_sentences} LINES" +"="*14 + "\n")
        
        print (summary_text + "\n")
        
        print ("=" * 35)
    
    return summary_text


if __name__ == '__main__':
    print(' working on it...')
    
    if appex.is_running_extension():
        text = get_safe_text()
        print(' handed over to the main app')
        
        clipboard.set(text)
        webbrowser.open(f'pythonista://ReadingTools/Summarize.py?action=run')
        sys.exit()
        
    else:
        text = get_safe_text()
    
    rephrase = None
    #while True:
    summary = summarize(text, rephrase)
    #try:
    #    rephrase = int(input("rephrase with how many sentences?: "))
    #except ValueError:
    #    break

