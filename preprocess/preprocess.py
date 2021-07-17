import os
import json
import string
import nltk
import numpy as np
# from nltk.stem.cistem import Cistem
# stemmer = Cistem()

def read_stopwords(stopwords_path=None):

    """
    read german stopwords from stopwords.json.
    These stopwords are from libraries e.g. spacy.lang.de.STOP_WORDS and nltk.corpus.stopwords.words('german') etc.
    """
    if stopwords_path == None:
        stopwords_path = os.path.join(os.path.dirname(__file__), 'stopwords.json')

    f = open(stopwords_path, 'r')
    stopwords = json.loads(f.read())
    f.close()
    return stopwords

german_stopwords = read_stopwords()

def tokenize(input_string):
    tokens = [token for token in nltk.word_tokenize(input_string)]
    # tokens = [stemmer.segment(token)[0] for token in tokens]
    return tokens


def filter_tokens(tokens, stopwords=german_stopwords):
    tokens = [t for t in tokens if \
              t not in stopwords and \
              t not in string.punctuation and \
              t not in ['–', '\xa0 ', '\xa0'] and \
              re.search(r'\d', t) == None and
              len(t) > 2]
    return tokens


def preprocess_text(text):
    tokens = tokenize(text.lower())
    filtered_tokens = filter_tokens(tokens)
    return filtered_tokens


def preprocess(text):
    tokens = preprocess_text(text)
    return ' '.join(tokens)

np_preprocess = np.vectorize(preprocess)
# import spacy
# nlp = spacy.load('de_core_news_sm')

# def lemmatize(string):
#     doc = nlp(string)
#     return [token.lemma_ for token in doc]
